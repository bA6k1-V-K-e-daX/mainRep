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

SYSTEM_PROMPT = """You are a visual object detector. Your entire output MUST be a single JSON array and NOTHING else.

OUTPUT FORMAT (strict):
- ONLY a JSON array like [{"label": "car", "confidence": 0.9}, {"label": "dog", "confidence": 0.7}] or []
- Each element MUST be an object: {"label": "<lowercase noun>", "confidence": <float 0.0–1.0>}
- confidence = how certain the object is present in the image.
- Omit any object where confidence < 0.5 — do not include it at all.
- NO explanations, NO reasoning, NO markdown fences, NO comments, NO prose before or after.

HOW TO DECIDE (do this mentally, do NOT write it down):
1. PARSE THE REQUEST: Extract ALL specific nouns/objects mentioned in the user's request. Translate them into English if they are in another language. Create a mental "Target List" of these labels.
2. SCAN THE IMAGE: Identify ALL distinct, visible objects in the image.
3. MERGE AND VERIFY:
   - For each item in the "Target List": Check if it is visibly present in the image.
     - If YES: Add it to the output with high confidence (e.g., 0.8–0.95).
     - If NO: Do NOT include it. (Do not hallucinate objects just because they were requested).
   - For other prominent objects found in the image (NOT in the "Target List"):
     - If they are clearly visible and significant, add them to the output with appropriate confidence.
4. FINAL FILTER: Remove duplicates. Ensure all labels are lowercase English singular nouns. Remove any entry with confidence < 0.5.

CRITICAL ANTI-HALLUCINATION RULES:
- NEVER output a label just because the user asked for it. It MUST be visible in the image.
- If the user asks for "wheels" but only a cat is visible -> Output [].
- If the user asks for "cat and dog", and only a cat is visible -> Output [{"label": "cat", "confidence": 0.9}]. Do NOT output "dog".
- If the user asks for "cat", but you also see a prominent "dog" -> Output BOTH [{"label": "cat", ...}, {"label": "dog", ...}]. The model should detect relevant requested items AND other obvious objects.
- "only cars" / "только машины": STRICT MODE. Ignore ANY object that is not a car. Bus, truck, bicycle are NOT cars. Output [] if no cars are present.
- Cartoons/drawings count (cartoon cat = "cat"), but do not invent objects that are not drawn.
- "wheels" / "колёса": only return ["wheel"] if a wheel is LARGE AND CLEARLY VISIBLE as the main subject.

LABEL STYLE:
- Specific English nouns, lowercase. "tram" not "train car", "sedan"→"car", "puppy"→"dog".
- Broad requests get specific labels: "transport" + you see a bus → ["bus"], not ["transport"].
- Deduplicate: 5 cars → ["car"] once.

EXAMPLES (request | what is in the image | correct output):
- "find animals"           | a horse with a rider                     | [{"label": "horse", "confidence": 0.95}]
- "find animals"           | a parked car, no animals                 | []
- "only cars" / "машины"   | a bus                                    | []
- "only cars" / "машины"   | a sedan and an SUV                       | [{"label": "car", "confidence": 0.95}]
- "find all vehicles"      | a cat close-up                           | []
- "find wheels"            | a cat lying on the floor                 | []
- "find wheels"            | a bicycle close-up, wheel fills frame    | [{"label": "wheel", "confidence": 0.9}]
- "find furniture"         | a woman reading on a sofa                | [{"label": "sofa", "confidence": 0.95}]
- "cat and dog"            | only a cat is visible                    | [{"label": "cat", "confidence": 0.9}]
- "cat"                    | a cat and a prominent dog                | [{"label": "cat", "confidence": 0.9}, {"label": "dog", "confidence": 0.85}]
- "машина и дерево"        | a car next to a tree                     | [{"label": "car", "confidence": 0.9}, {"label": "tree", "confidence": 0.9}]
- "машина и дерево"        | only a car is visible                    | [{"label": "car", "confidence": 0.9}]

Your entire response is the JSON array. Nothing else. Example of valid output:
[{"label": "car", "confidence": 0.92}, {"label": "bicycle", "confidence": 0.61}]"""

USER_PROMPT_TEMPLATE = """User's request: "{prompt}"

Step A (mentally): identify what is ACTUALLY in this image.
Step B (mentally): keep only items that match the request above, assign confidence 0.0–1.0.
Step C (output): JSON array of {{"label": "...", "confidence": ...}} objects, or [] if none match.

Output ONLY the JSON array. No reasoning text."""

RELEVANCE_FILTER_SYSTEM = (
    "You are a strict relevance filter. "
    "Given a user request and a list of detected objects, "
    "return ONLY the objects that belong to the category the user asked for. "
    "Output a JSON array of strings like [\"car\", \"bus\"], or [] if none match. "
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
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,
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
) -> List[str]:
    """Текстовый вызов Gemma: оставляет только метки, релевантные запросу."""
    if not labels:
        return []

    user_msg = (
        f'User request: "{query}"\n'
        f'Detected objects: {json.dumps(labels, ensure_ascii=False)}\n'
        f'Relevant objects (JSON array):'
    )

    payload = {
        "messages": [
            {"role": "system", "content": RELEVANCE_FILTER_SYSTEM},
            {"role": "user", "content": user_msg},
        ],
        "max_tokens": 128,
        "temperature": 0.0,
        "stream": False,
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
                lbl = item.lower().strip()
            elif isinstance(item, dict):
                lbl = str(item.get("label", item.get("class", item.get("name", "")))).lower().strip()
            else:
                continue
            if lbl and lbl in original_set:
                filtered.append(lbl)
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
        "max_tokens": 128,
        "temperature": 0.0,
        "stream": False,
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
        "max_tokens": 128,
        "temperature": 0.0,
        "stream": False,
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
            "status": "error",
            "error": result.get("error"),
        }

    labels_raw = result["labels"]
    passed_conf = [i for i in labels_raw if i.get("confidence", 1.0) >= min_confidence]
    dropped_conf = [i["label"] for i in labels_raw if i.get("confidence", 1.0) < min_confidence]

    label_strings = [i["label"] for i in passed_conf]
    dropped_rel: List[str] = []
    if use_relevance_filter and label_strings:
        relevant = filter_labels_by_relevance(query, label_strings)
        relevant_set = set(relevant)
        dropped_rel = [l for l in label_strings if l not in relevant_set]
        label_strings = relevant

    return {
        "labels": label_strings,
        "labels_raw": labels_raw,
        "filtered_by_confidence": dropped_conf,
        "filtered_by_relevance": dropped_rel,
        "status": "success",
        "error": None,
    }
