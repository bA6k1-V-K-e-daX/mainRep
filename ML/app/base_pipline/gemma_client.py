"""
Gemma 4 Vision client — vision анализ + relevance filter.

Портировано из tests/test_gemma.py с той же логикой:
  1. analyze_single_image()       — картинка + промпт → [{"label", "confidence"}]
  2. filter_labels_by_relevance() — текстовый пост-фильтр релевантности
  3. extract_labels_for_image()   — высокоуровневая обёртка для пайплайна
"""

import base64
import json
import logging
import re
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional

import requests
from PIL import Image

from config.settings import LLMConfig

logger = logging.getLogger(__name__)


# ============================================================
# ПРОМПТЫ (идентичны test_gemma.py)
# ============================================================

SYSTEM_PROMPT = """You are a visual object detector. Output ONLY a JSON array, nothing else.

FORMAT: [{"label": "car", "confidence": 0.9}] or []
- confidence 0.0–1.0; omit entry if < 0.5
- labels: lowercase English singular nouns; deduplicate (5 cars → "car" once)
- NO text, NO markdown, NO reasoning outside the array

PROCESS (mental only, do NOT write):
1. Parse user's request — extract target object nouns (translate non-English to English)
2. Check each target: is it visually present in the image? Include only if YES
3. Do NOT include objects not matching the request, even if visible

STRICT MODE ("only X" / "только X"): output ONLY that category, nothing else
ANTI-HALLUCINATION: NEVER output a label you don't visually see. Request for "wheels" on a cat image → []"""

USER_PROMPT_TEMPLATE = 'Request: "{prompt}"\nOutput JSON array of objects that are BOTH visible in this image AND relevant to the request.'

RELEVANCE_FILTER_SYSTEM = (
    "You are a relevance scorer. "
    "Given a user request and a list of detected objects, "
    "score each object's relevance to the request from 0.0 to 1.0. "
    "Output ONLY a JSON array like [{\"label\": \"car\", \"relevance\": 0.95}]. "
    "1.0 = exact match or direct member of requested category. "
    "0.5 = loosely related. "
    "0.0 = unrelated. "
    "Nothing else — no explanations, no markdown, no extra text."
)

EXTRACT_USER_LABELS_SYSTEM = """You extract object labels from a user request.

RULES:
- Output ONLY a JSON array of strings, nothing else.
- Each string: English, lowercase, singular noun.
- Translate non-English terms to English.
- Ignore verbs, adjectives, filler words ("find", "detect", "please", "only", "все", "найди").
- Deduplicate.

EXAMPLES:
- "Крыло, фюзеляж, пропеллер, рама" -> ["wing", "fuselage", "propeller", "frame"]
- "найди машины и автобусы"         -> ["car", "bus"]
- "только собаки"                   -> ["dog"]
- "cats and dogs"                    -> ["cat", "dog"]
- "самолёт"                         -> ["airplane"]

Your entire response is the JSON array. Nothing else."""

STRICT_FILTER_SYSTEM = """You map detected objects to an allowed label list.

For each detected object, list which allowed labels it covers:
- Exact match: "car" covers "car"
- Synonym: "plane" covers "airplane"
- Hyponym (subcategory): "sedan" covers "car", "dog" covers "animal", "cat" covers "animal"

DROP the detected object (empty covers list) if:
- It is a HYPERNYM (parent category) of the allowed labels: "airplane" does NOT cover "wing" (wing is a PART of airplane). "vehicle" does NOT cover "car".
- It is unrelated: "drone" does NOT cover "car".
- It is a sibling: "bus" does NOT cover "car".

Output ONLY a JSON array like:
[{"detected": "cat", "covers": ["animal"]}, {"detected": "dog", "covers": ["animal"]}]
Include every detected object (with empty "covers" if it matches nothing).
No explanations, no markdown, nothing else."""

MISSING_LABELS_SYSTEM = """You decide which user-requested labels are NOT already covered by the detected list.

Coverage rules (apply ALL):
1. Exact match: 'car' covers 'car'.
2. Synonyms: 'plane' covers 'airplane'.
3. Hypernym covers hyponym: 'vehicle' covers 'bus', 'dog' covers 'puppy'.
4. Hyponym covers hypernym: if specific instances of a category are detected, the category IS covered.
   Examples: ['tiger','elephant'] covers 'animal'; ['bus','car'] covers 'vehicle'; ['sofa'] covers 'furniture'.

Output ONLY a JSON array of strings — the subset of requested labels MISSING from the detected list.
If all are covered (including via rule 4), output [].
Use EXACT strings from the requested list (do not rewrite).
No explanations, no markdown, nothing else."""


# ============================================================
# ПАРСИНГ ОТВЕТА
# ============================================================

def parse_labels_from_response(raw_text: str) -> List[Dict]:
    """Извлекает [{"label", "confidence"}] из ответа Gemma."""
    raw_text = (raw_text or "").strip()
    candidates = re.findall(r'\[[^\[\]]*\]', raw_text, re.DOTALL)

    for candidate in reversed(candidates):
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if not isinstance(data, list):
            continue

        items = []
        for item in data:
            if isinstance(item, str):
                label = item.lower().strip()
                confidence = 1.0
            elif isinstance(item, dict):
                label = (
                    item.get("label", "")
                    or item.get("class", "")
                    or item.get("name", "")
                    or item.get("object", "")
                )
                label = str(label).lower().strip()
                raw_conf = item.get("confidence", item.get("score", item.get("prob", 1.0)))
                try:
                    confidence = max(0.0, min(1.0, float(raw_conf)))
                except (TypeError, ValueError):
                    confidence = 1.0
            else:
                continue
            if label:
                items.append({"label": label, "confidence": confidence})

        seen = set()
        cleaned = []
        for item in items:
            label = item["label"]
            if not label or label in {"none", "null", "n/a"}:
                continue
            if label in seen:
                continue
            seen.add(label)
            cleaned.append(item)
        return cleaned

    return []


# ============================================================
# VISION CALL (изображение + запрос → метки с confidence)
# ============================================================

def analyze_single_image(
    image: Image.Image,
    prompt: str,
    max_tokens: int = 256,
    temperature: float = 0.0,
    timeout: int = 120,
    max_image_size: Optional[int] = None,
) -> Dict:
    """Отправляет изображение в Gemma 4 Vision, возвращает labels с confidence."""
    if max_image_size is None:
        max_image_size = LLMConfig.MAX_IMAGE_SIZE
    if max(image.size) > max_image_size:
        ratio = max_image_size / max(image.size)
        new_size = (int(image.width * ratio), int(image.height * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)

    buffered = BytesIO()
    image.save(buffered, format="JPEG", quality=LLMConfig.JPEG_QUALITY)
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": USER_PROMPT_TEMPLATE.format(prompt=prompt)},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}},
                ],
            },
        ],
        "max_tokens": max(max_tokens, 512),
        "temperature": temperature,
        "stream": False,
        "chat_template_kwargs": {"enable_thinking": False},
    }

    try:
        response = requests.post(
            LLMConfig.get_chat_url(),
            json=payload,
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        raw_text = response.json()["choices"][0]["message"]["content"].strip()
        return {
            "labels": parse_labels_from_response(raw_text),
            "raw_response": raw_text,
            "status": "success",
            "error": None,
        }
    except Exception as e:
        logger.warning(f"Gemma vision call failed: {e}")
        return {"labels": [], "raw_response": "", "status": "error", "error": str(e)}


# ============================================================
# RELEVANCE FILTER (текстовый, без картинки)
# ============================================================

def filter_labels_by_relevance(
    query: str,
    labels: List[str],
    timeout: int = 60,
    threshold: Optional[float] = None,
) -> List[str]:
    """Текстовый вызов Gemma: оставляет только метки с relevance >= threshold."""
    if not labels:
        return []
    if threshold is None:
        threshold = LLMConfig.RELEVANCE_THRESHOLD

    user_msg = (
        f'User request: "{query}"\n'
        f'Detected objects: {json.dumps(labels, ensure_ascii=False)}\n'
        f'Score each object (JSON array):'
    )

    payload = {
        "messages": [
            {"role": "system", "content": RELEVANCE_FILTER_SYSTEM},
            {"role": "user", "content": user_msg},
        ],
        "max_tokens": 512,
        "temperature": 0.0,
        "stream": False,
        "chat_template_kwargs": {"enable_thinking": False},
    }

    try:
        response = requests.post(
            LLMConfig.get_chat_url(),
            json=payload,
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        raw = response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.warning(f"Relevance filter failed ({e}), keeping all labels")
        return labels

    candidates = re.findall(r'\[[^\[\]]*\]', raw, re.DOTALL)
    original_set = set(labels)
    for candidate in reversed(candidates):
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if not isinstance(data, list):
            continue
        filtered = []
        for item in data:
            if isinstance(item, str):
                # Старый формат (строка без score) — принимаем если в original_set
                lbl = item.lower().strip()
                if lbl and lbl in original_set:
                    filtered.append(lbl)
            elif isinstance(item, dict):
                lbl = str(item.get("label", item.get("class", item.get("name", "")))).lower().strip()
                try:
                    score = float(item.get("relevance", item.get("score", item.get("confidence", 1.0))))
                except (TypeError, ValueError):
                    score = 1.0
                if lbl and lbl in original_set and score >= threshold:
                    filtered.append(lbl)
                    logger.debug(f"Relevance filter: '{lbl}' score={score:.2f} >= {threshold} → keep")
                elif lbl and lbl in original_set:
                    logger.debug(f"Relevance filter: '{lbl}' score={score:.2f} < {threshold} → drop")
        return filtered

    return []


# ============================================================
# ИЗВЛЕЧЕНИЕ ПОЛЬЗОВАТЕЛЬСКИХ МЕТОК ИЗ PROMPT (текстовый)
# ============================================================

def _parse_string_array(raw: str) -> Optional[List[str]]:
    """Извлекает JSON-массив строк из ответа Gemma; None если распарсить не удалось."""
    candidates = re.findall(r'\[[^\[\]]*\]', raw or "", re.DOTALL)
    for candidate in reversed(candidates):
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if not isinstance(data, list):
            continue
        out: List[str] = []
        seen = set()
        for item in data:
            if isinstance(item, str):
                s = item.lower().strip()
            elif isinstance(item, dict):
                s = str(item.get("label", item.get("class", item.get("name", "")))).lower().strip()
            else:
                continue
            if s and s not in seen:
                seen.add(s)
                out.append(s)
        return out
    return None


def _fallback_split_prompt(prompt: str) -> List[str]:
    """Простой split по ',' если Gemma недоступна."""
    out: List[str] = []
    seen = set()
    for part in (prompt or "").split(","):
        s = part.strip().lower()
        if s and s not in seen:
            seen.add(s)
            out.append(s)
    return out


def extract_user_labels_from_prompt(prompt: str, timeout: int = 60) -> List[str]:
    """Извлекает метки из prompt-а пользователя и переводит в английский lowercase."""
    prompt = (prompt or "").strip()
    if not prompt:
        return []

    user_msg = f'User request: "{prompt}"\nLabels (JSON array of English lowercase nouns):'
    payload = {
        "messages": [
            {"role": "system", "content": EXTRACT_USER_LABELS_SYSTEM},
            {"role": "user", "content": user_msg},
        ],
        "max_tokens": 512,
        "temperature": 0.0,
        "stream": False,
        "chat_template_kwargs": {"enable_thinking": False},
    }

    try:
        response = requests.post(
            LLMConfig.get_chat_url(),
            json=payload,
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        raw = response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.warning(f"extract_user_labels_from_prompt failed ({e}); using comma-split fallback")
        return _fallback_split_prompt(prompt)

    parsed = _parse_string_array(raw)
    if parsed is None:
        logger.warning("Could not parse user-labels JSON; using comma-split fallback")
        return _fallback_split_prompt(prompt)
    return parsed


def _extract_outer_array(raw: str) -> Optional[str]:
    """Находит первый top-level JSON array [...] в raw через bracket counting.
    Нужно когда массив содержит вложенные массивы (re.findall матчит их первыми)."""
    start = (raw or "").find('[')
    if start == -1:
        return None
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(raw)):
        c = raw[i]
        if esc:
            esc = False
            continue
        if c == '\\':
            esc = True
            continue
        if c == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                return raw[start:i+1]
    return None


def filter_and_map_detections(
    detected: List[str],
    user_labels: List[str],
    timeout: int = 60,
) -> Dict[str, List[str]]:
    """
    За один Gemma-вызов:
      - Строго фильтрует detected (отсеивает hypernym-ы и unrelated)
      - Возвращает mapping {detected_label: [user_labels, которые он покрывает]}

    Пример: detected=["cat","dog"], user_labels=["animal"]
            → {"cat": ["animal"], "dog": ["animal"]}
    Пример: detected=["airplane"], user_labels=["wing","propeller"]
            → {} (airplane — hypernym, ничего не покрывает)
    """
    if not detected:
        return {}
    if not user_labels:
        return {d: [] for d in detected}

    user_msg = (
        f"Allowed labels: {json.dumps(list(user_labels), ensure_ascii=False)}\n"
        f"Detected objects: {json.dumps(list(detected), ensure_ascii=False)}\n"
        f"Mapping (JSON array):"
    )
    payload = {
        "messages": [
            {"role": "system", "content": STRICT_FILTER_SYSTEM},
            {"role": "user", "content": user_msg},
        ],
        "max_tokens": 512,
        "temperature": 0.0,
        "stream": False,
        "chat_template_kwargs": {"enable_thinking": False},
    }

    try:
        response = requests.post(
            LLMConfig.get_chat_url(),
            json=payload,
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        raw = response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.warning(f"Strict filter failed ({e}); keeping all detected")
        return {d: [] for d in detected}

    # Парсим внешний массив [{"detected": "...", "covers": [...]}] через bracket counting
    detected_set = set(detected)
    user_set = set(user_labels)
    outer = _extract_outer_array(raw)
    if outer is None:
        logger.warning("Could not find outer JSON array in strict-filter response; keeping all detected")
        return {d: [] for d in detected}
    try:
        data = json.loads(outer)
    except json.JSONDecodeError as e:
        logger.warning(f"Strict-filter JSON parse error ({e}); keeping all detected")
        return {d: [] for d in detected}
    if not isinstance(data, list):
        return {d: [] for d in detected}

    result: Dict[str, List[str]] = {}
    for item in data:
        if not isinstance(item, dict):
            continue
        det = str(item.get("detected", "")).lower().strip()
        if det not in detected_set:
            continue
        covers_raw = item.get("covers", [])
        if not isinstance(covers_raw, list):
            covers_raw = []
        covers = [str(c).lower().strip() for c in covers_raw]
        covers = [c for c in covers if c in user_set]
        if covers:
            result[det] = covers
    return result


def find_missing_user_labels(
    detected: List[str],
    user_labels: List[str],
    timeout: int = 60,
) -> List[str]:
    """
    Возвращает подмножество user_labels, не покрытое detected (с учётом синонимов/гиперонимов).
    Если detected пусто — возвращает user_labels целиком.
    """
    if not user_labels:
        return []
    if not detected:
        return list(user_labels)

    user_msg = (
        f"Detected: {json.dumps(list(detected), ensure_ascii=False)}\n"
        f"Requested: {json.dumps(list(user_labels), ensure_ascii=False)}\n"
        f"Missing (JSON array, using exact strings from Requested):"
    )
    payload = {
        "messages": [
            {"role": "system", "content": MISSING_LABELS_SYSTEM},
            {"role": "user", "content": user_msg},
        ],
        "max_tokens": 512,
        "temperature": 0.0,
        "stream": False,
        "chat_template_kwargs": {"enable_thinking": False},
    }

    try:
        response = requests.post(
            LLMConfig.get_chat_url(),
            json=payload,
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        raw = response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.warning(f"find_missing_user_labels failed ({e}); using string-diff fallback")
        detected_set = set(detected)
        return [l for l in user_labels if l not in detected_set]

    parsed = _parse_string_array(raw)
    if parsed is None:
        detected_set = set(detected)
        return [l for l in user_labels if l not in detected_set]

    user_set = set(user_labels)
    return [l for l in parsed if l in user_set]


# ============================================================
# ВЫСОКОУРОВНЕВАЯ ОБЁРТКА ДЛЯ ПАЙПЛАЙНА
# ============================================================

def extract_labels_for_image(
    image_path: Path,
    query: str,
    min_confidence: Optional[float] = None,
    use_relevance_filter: Optional[bool] = None,
    user_labels: Optional[List[str]] = None,
) -> Dict:
    """
    Полный цикл для одного изображения:
      vision → confidence-фильтр → relevance-фильтр → итоговый список меток.

    Returns:
        {
            "labels": ["car", "bicycle"],           # финальные метки для SAM3
            "labels_raw": [{"label","confidence"}], # до фильтрации
            "filtered_by_confidence": [...],
            "filtered_by_relevance": [...],
            "status": "success" | "error",
            "error": Optional[str],
        }
    """
    if min_confidence is None:
        min_confidence = LLMConfig.MIN_GEMMA_CONFIDENCE
    if use_relevance_filter is None:
        use_relevance_filter = LLMConfig.USE_RELEVANCE_FILTER

    try:
        image = Image.open(image_path).convert("RGB")
    except Exception as e:
        return {
            "labels": [],
            "labels_raw": [],
            "filtered_by_confidence": [],
            "filtered_by_relevance": [],
            "covered_user_labels": [],
            "status": "error",
            "error": f"Cannot open image: {e}",
        }

    result = analyze_single_image(image, query)
    if result["status"] != "success":
        return {
            "labels": [],
            "labels_raw": [],
            "filtered_by_confidence": [],
            "filtered_by_relevance": [],
            "covered_user_labels": [],
            "status": "error",
            "error": result.get("error"),
        }

    labels_raw = result["labels"]
    passed_conf = [i for i in labels_raw if i.get("confidence", 1.0) >= min_confidence]
    dropped_conf = [i["label"] for i in labels_raw if i.get("confidence", 1.0) < min_confidence]

    label_strings = [i["label"] for i in passed_conf]
    dropped_rel: List[str] = []
    covered_user_labels: List[str] = []
    if use_relevance_filter and label_strings:
        if user_labels:
            # Строгая фильтрация + mapping: {detected: [covered user_labels]}
            mapping = filter_and_map_detections(label_strings, user_labels)
            kept = list(mapping.keys())
            dropped_rel = [l for l in label_strings if l not in mapping]
            # Union покрытых user_labels (для fallback в detect_image.py)
            covered_set: set = set()
            for covers in mapping.values():
                covered_set.update(covers)
            covered_user_labels = [l for l in user_labels if l in covered_set]
            label_strings = kept
        else:
            relevant = filter_labels_by_relevance(query, label_strings)
            relevant_set = set(relevant)
            dropped_rel = [l for l in label_strings if l not in relevant_set]
            label_strings = relevant

    return {
        "labels": label_strings,
        "labels_raw": labels_raw,
        "filtered_by_confidence": dropped_conf,
        "filtered_by_relevance": dropped_rel,
        "covered_user_labels": covered_user_labels,
        "status": "success",
        "error": None,
    }
