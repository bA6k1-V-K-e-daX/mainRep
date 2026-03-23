import argparse
import json
import os
import re
import sys
import requests
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import torch
from PIL import Image, ImageDraw
from transformers import (
    AutoModelForZeroShotObjectDetection,
    AutoProcessor,
)

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.base_pipline.sam_pipline import (
    build_merged_mask_and_report,
    load_sam_components,
)


VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}

QWEN_LITE_PROMPT = """
Extract visual objects from the user request. Output ONLY English words separated by " . ".

Rules:
- Lowercase, no explanations, no extra words
- Extract ONLY entities explicitly mentioned by the user
- Translate non-English words to English (e.g., "кот" -> "cat", "машина" -> "car")
- Remove duplicates and obvious synonyms (keep one canonical form)
- Do NOT expand categories: if user says "animals", output "animal" (not cat.dog.horse)
- Do NOT add classes not mentioned by the user
- Skip actions, emotions, places, abstract concepts, weather, time, fictional objects
- If request contains no visual objects -> output nothing (empty)

Examples:
User: найди кота и собаку -> cat . dog
User: машина, авто, автомобиль -> car
User: bike, bicycle, cycle -> bicycle
User: воробей, орёл, сова -> sparrow . eagle . owl
User: человек, люди, персона -> person
User: животные -> animal
User: транспорт -> vehicle
User: птицы -> bird
User: красивые закаты и эмоции ->
User: любовь, счастье, грусть ->
User: время, дата, завтра ->
User: единорог, дракон, фея ->
User: найди всё -> object
User: найти объекты на фото -> object

Request: {user_prompt}
Answer:
"""

LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://127.0.0.1:8081")

def collect_images(image_path: Optional[Path], images_dir: Optional[Path]) -> List[Path]:
    if image_path and images_dir:
        raise ValueError("Use either --image or --images-dir, not both.")
    if not image_path and not images_dir:
        raise ValueError("Provide --image or --images-dir.")

    if image_path:
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        return [image_path]

    if not images_dir.exists():
        raise FileNotFoundError(f"Directory not found: {images_dir}")

    images = sorted(
        p for p in images_dir.iterdir() if p.is_file() and p.suffix.lower() in VALID_EXTENSIONS
    )
    if not images:
        raise ValueError(f"No images found in: {images_dir}")
    return images


def build_prompt_from_dictionary(dictionary_name: str) -> str:
    # Legacy helper kept for compatibility with older runs/args.
    return "object."


def map_token_to_english_label(token: str) -> str:
    token = token.strip().lower()
    return token


def is_generic_query(query: str) -> bool:
    q = query.strip().lower()
    generic_phrases = [
        "find everything",
        "detect everything",
        "find all",
        "all objects",
        "find objects",
        "detect objects",
        "найди все",
        "найди всё",
        "найти все",
        "найти всё",
        "найди объекты",
        "найти объекты",
        "объекты на фото",
        "object",
        "objects",
    ]
    return any(phrase in q for phrase in generic_phrases)


def normalize_specific_query_to_prompt(query: str) -> str:
    q = query.lower()
    q = re.sub(r"[\"'`]+", " ", q)
    q = re.sub(r"\b(find|detect|segment|locate)\b", " ", q)
    q = re.sub(r"\b(найди|найти|сегментируй|сегментировать|обнаружь|обнаружить)\b", " ", q)
    q = re.sub(r"\b(on image|in image|on photo|in photo|на фото|на изображении)\b", " ", q)
    q = q.replace(" и ", ",")
    q = q.replace(" and ", ",")

    q = re.sub(r"\b(мне|пожалуйста|pls|please)\b", " ", q)
    tokens = [t.strip() for t in re.split(r"[,;]+", q) if t.strip()]
    normalized: List[str] = []
    for token in tokens:
        token = map_token_to_english_label(token)
        token = re.sub(r"[^a-z0-9\s\-]", "", token)
        token = re.sub(r"\s+", " ", token).strip()
        normalized.append(token)

    if not normalized:
        return "object."
    return ". ".join(normalized) + "."


def normalize_labels(labels: List[str]) -> List[str]:
    canonical_map = {
        "auto": "car",
        "automobile": "car",
        "vehicle": "car",
        "motorbike": "motorcycle",
        "bike": "bicycle",
        "cycle": "bicycle",
        "stool": "chair",
        "man": "person",
        "woman": "person",
        "people": "person",
        "human": "person",
        "kitty": "cat",
        "puppy": "dog",
        "motociclet": "motorcycle",
    }
    normalized: List[str] = []
    for raw in labels:
        val = raw.strip().lower()
        if not val:
            continue
        val = map_token_to_english_label(val)
        val = re.sub(r"[^a-z0-9\s\-]", "", val)
        val = re.sub(r"\s+", " ", val).strip()
        val = canonical_map.get(val, val)
        if val in {"object", "objects"}:
            continue
        if val and val not in normalized:
            normalized.append(val)
    return normalized


BAD_LABEL_TOKENS = {
    "example",
    "examples",
    "query",
    "queries",
    "extraid0",
    "extraid1",
    "extraid2",
    "none",
    "null",
}


def is_plausible_label(label: str) -> bool:
    value = label.strip().lower()
    if not value:
        return False
    if any(ch.isdigit() for ch in value):
        return False
    if len(value.split()) > 2:
        return False
    if value in BAD_LABEL_TOKENS:
        return False
    tokens = value.split()
    for tok in tokens:
        if tok in BAD_LABEL_TOKENS:
            return False
        if not re.fullmatch(r"[a-z][a-z\-]*", tok):
            return False
    return True


def clean_plausible_labels(labels: List[str]) -> List[str]:
    cleaned: List[str] = []
    for label in labels:
        if is_plausible_label(label) and label not in cleaned:
            cleaned.append(label)
    return cleaned


def are_english_labels(labels: List[str]) -> bool:
    if not labels:
        return False
    return all(is_plausible_label(label) for label in labels)


def parse_query_with_llm(
    query: str,
    llm_model_id: str = None,  # Больше не используется, оставлен для совместимости
    device: str = None,        # Больше не используется
    max_new_tokens: int = 96,
) -> Dict[str, object]:
    """
    Заменяет локальную загрузку LLM на HTTP-запрос к llama.cpp серверу.
    Экономит ~1.3 ГБ VRAM и ускоряет запуск.
    """
    prompt = QWEN_LITE_PROMPT.format(user_prompt=query)
    
    try:
        resp = requests.post(
            f"{LLM_SERVICE_URL}/v1/chat/completions",
            json={
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_new_tokens,
                "temperature": 0.0,
            },
            timeout=30
        )
        resp.raise_for_status()
        raw_text = resp.json()['choices'][0]['message']['content'].strip()
    except requests.exceptions.ConnectionError:
        return {
            "ok": False,
            "labels": [],
            "raw_text": "",
            "status": "connection_error",
            "error": f"Cannot connect to LLM service at {LLM_SERVICE_URL}"
        }
    except Exception as e:
        return {
            "ok": False,
            "labels": [],
            "raw_text": "",
            "status": "http_error",
            "error": str(e)
        }
    
    parse_status = "delimiter_parse"
    cleaned_output = raw_text.replace("\n", " ").strip()
    
    if cleaned_output in {"", "none", "[]"}:
        return {"ok": False, "labels": [], "raw_text": raw_text, "status": "empty_output"}
    
    chunks = [c.strip() for c in re.split(r"\s*\.\s*", cleaned_output) if c.strip()]
    labels = clean_plausible_labels(normalize_labels(chunks))
    labels = [x for x in labels if 1 <= len(x.split()) <= 3]
    
    if not labels:
        return {"ok": False, "labels": [], "raw_text": raw_text, "status": parse_status}
    
    return {"ok": True, "labels": labels, "raw_text": raw_text, "status": parse_status}


def resolve_query_with_llm(
    query: str,
    llm_model_id: str = None,  # Не используется, оставлен для совместимости
    device: str = None,        # Не используется
    llm_max_new_tokens: int = 96,
) -> Dict[str, object]:
    """Обёртка для parse_query_with_llm с обработкой ошибок"""
    try:
        parsed = parse_query_with_llm(
            query=query,
            llm_model_id=llm_model_id,
            device=device,
            max_new_tokens=llm_max_new_tokens,
        )
    except Exception as exc:
        return {
            "ok": False,
            "labels": [],
            "prompt": "",
            "raw_text": "",
            "status": "exception",
            "error": str(exc),
        }
    
    labels: List[str] = [str(x) for x in parsed.get("labels", [])]
    if not parsed.get("ok") or not labels or not are_english_labels(labels):
        return {
            "ok": False,
            "labels": [],
            "prompt": "",
            "raw_text": str(parsed.get("raw_text", "")),
            "status": str(parsed.get("status", "invalid")),
            "error": "",
        }
    
    prompt = ". ".join(labels) + "."
    return {
        "ok": True,
        "labels": labels,
        "prompt": prompt,
        "raw_text": str(parsed.get("raw_text", "")),
        "status": str(parsed.get("status", "ok")),
        "error": "",
    }


def build_effective_prompt(query: str, label_dictionary: str) -> str:
    if is_generic_query(query):
        return "object."
    return normalize_specific_query_to_prompt(query)


def save_outputs_colored(
    image: Image.Image,
    mask_uint8: np.ndarray,
    out_prefix: Path,
    detections: List[Dict[str, object]] = None,
    individual_masks: List[np.ndarray] = None
) -> Tuple[Path, Path]:
    """Сохраняет маску и оверлей, где каждый объект своего цвета."""
    mask_img = Image.fromarray(mask_uint8, mode="L")
    mask_path = out_prefix.with_name(f"{out_prefix.name}_mask.png")
    overlay_path = out_prefix.with_name(f"{out_prefix.name}_overlay.png")
    
    overlay = image.convert("RGB").copy()
    draw = ImageDraw.Draw(overlay)
    
    if individual_masks and detections and len(individual_masks) == len(detections):
        color_mask = np.zeros((image.height, image.width, 3), dtype=np.uint8)
        
        for idx, (det, box_mask) in enumerate(zip(detections, individual_masks)):
            color = get_distinct_color(idx)
            color_mask[box_mask > 0] = color
            # Рамки и подписи убраны - только цветная маска
        
        color_mask_img = Image.fromarray(color_mask, mode="RGB")
        color_mask_path = out_prefix.with_name(f"{out_prefix.name}_color_mask.png")
        color_mask_img.save(color_mask_path)
        
        alpha = Image.fromarray((mask_uint8 > 0).astype(np.uint8) * 140, mode="L")
        color_mask_overlay = Image.fromarray(color_mask, mode="RGB")
        overlay.paste(color_mask_overlay, mask=alpha)
    else:
        red = Image.new("RGB", image.size, (255, 40, 40))
        alpha = Image.fromarray((mask_uint8 > 0).astype(np.uint8) * 110, mode="L")
        overlay.paste(red, mask=alpha)

    mask_img.save(mask_path)
    overlay.save(overlay_path)
    return mask_path, overlay_path


def prepare_image_and_prompts(
    image: Image.Image,
    max_side: int,
    resize_mode: str,
) -> Tuple[Image.Image, float, Tuple[int, int]]:
    original_size = image.size
    width, height = original_size
    current_max_side = max(width, height)

    if max_side <= 0:
        return image, 1.0, original_size
    if resize_mode == "downscale_only" and current_max_side <= max_side:
        return image, 1.0, original_size
    if current_max_side == max_side:
        return image, 1.0, original_size

    scale = max_side / float(current_max_side)
    new_size = (max(1, int(round(width * scale))), max(1, int(round(height * scale))))
    resized = image.resize(new_size, Image.Resampling.BILINEAR)
    return resized, scale, original_size


def detect_boxes_from_text(
    detector_processor: AutoProcessor,
    detector_model: AutoModelForZeroShotObjectDetection,
    image: Image.Image,
    text_prompt: str,
    device: str,
    box_threshold: float,
    text_threshold: float,
) -> List[Dict[str, object]]:
    # GroundingDINO works more reliably with dot-terminated prompts.
    prompt = text_prompt.strip()
    if not prompt.endswith("."):
        prompt = f"{prompt}."

    # 1. Получаем данные от процессора (объект BatchEncoding)
    inputs = detector_processor(images=image, text=prompt, return_tensors="pt").to(device)
    
    # 2. ВАЖНО: Сохраняем input_ids ДО превращения inputs в обычный словарь
    input_ids = inputs["input_ids"]
    
    # 3. ИЗМЕНЕНИЯ ДЛЯ FP16 (превращает BatchEncoding в dict)
    if device == "cuda":
        inputs = {k: v.half() if v.dtype == torch.float32 else v for k, v in inputs.items()}
    
    # 4. Запуск модели
    with torch.no_grad():
        with torch.autocast(device_type=device, dtype=torch.float16):
            outputs = detector_model(**inputs)

    # 5. Пост-процессинг (используем сохранённую переменную input_ids)
    try:
        results = detector_processor.post_process_grounded_object_detection(
            outputs=outputs,
            input_ids=input_ids,  # ✅ ИСПРАВЛЕНО: используем переменную, а не inputs.input_ids
            threshold=box_threshold,
            text_threshold=text_threshold,
            target_sizes=[image.size[::-1]],
        )
    except TypeError:
        # Compatibility fallback for versions that still expect box_threshold.
        results = detector_processor.post_process_grounded_object_detection(
            outputs=outputs,
            input_ids=input_ids,  # ✅ ИСПРАВЛЕНО: используем переменную, а не inputs.input_ids
            box_threshold=box_threshold,
            text_threshold=text_threshold,
            target_sizes=[image.size[::-1]],
        )
        
    if not results:
        return []

    payload = results[0]
    boxes = payload["boxes"].detach().cpu().tolist()
    scores = payload["scores"].detach().cpu().tolist() if "scores" in payload else [None] * len(boxes)
    if "text_labels" in payload:
        labels = payload["text_labels"]
    elif "labels" in payload:
        labels = payload["labels"]
    else:
        labels = ["unknown"] * len(boxes)

    detections: List[Dict[str, object]] = []
    for idx, box in enumerate(boxes):
        score = float(scores[idx]) if scores[idx] is not None else None
        label = str(labels[idx]) if labels[idx] is not None else "unknown"
        detections.append(
            {
                "label": label,
                "score": score,
                "box": [float(v) for v in box],
            }
        )
    return detections


def scale_boxes(boxes: List[List[float]], scale: float) -> List[List[float]]:
    if scale == 1.0:
        return boxes
    return [[b[0] * scale, b[1] * scale, b[2] * scale, b[3] * scale] for b in boxes]


def save_boxes_preview(
    image: Image.Image,
    detections: List[Dict[str, object]],
    out_prefix: Path,
    save_when_empty: bool = False,
) -> Optional[Path]:
    if not detections and not save_when_empty:
        return None
    preview = image.convert("RGB").copy()
    draw = ImageDraw.Draw(preview)
    for det in detections:
        box = det["box"]
        label = str(det.get("label", "unknown"))
        score = det.get("score")
        score_text = f"{score:.2f}" if isinstance(score, float) else "n/a"
        text = f"{label} {score_text}"
        draw.rectangle(box, outline=(0, 255, 0), width=2)
        text_anchor = (box[0] + 2, max(0, box[1] - 14))
        draw.text(text_anchor, text, fill=(0, 255, 0))
    preview_path = out_prefix.with_name(f"{out_prefix.name}_boxes.png")
    preview.save(preview_path)
    return preview_path


def save_empty_segmentation_artifacts(image: Image.Image, out_prefix: Path) -> Tuple[Path, Path]:
    empty_mask = np.zeros((image.height, image.width), dtype=np.uint8)
    return save_outputs_colored(image, empty_mask, out_prefix, detections=None, individual_masks=None)


def save_detections_json(
    detections: List[Dict[str, object]],
    image_size: Tuple[int, int],
    out_prefix: Path,
) -> Path:
    payload = {
        "image_size": {"width": image_size[0], "height": image_size[1]},
        "detections": detections,
    }
    json_path = out_prefix.with_name(f"{out_prefix.name}_detections.json")
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return json_path


def build_image_output_prefix(output_dir: Path, image_path: Path) -> Path:
    # Per-image folder to keep artifacts isolated for batch runs.
    ext = image_path.suffix.lower().lstrip(".") or "img"
    folder_name = f"{image_path.stem}_{ext}"
    image_dir = output_dir / folder_name
    image_dir.mkdir(parents=True, exist_ok=True)
    return image_dir / image_path.stem


def append_report_block(report_path: Path, image_name: str, detections: List[Dict[str, object]]) -> None:
    with report_path.open("a", encoding="utf-8") as f:
        f.write(f"{image_name}\n")
        f.write(json.dumps(detections, ensure_ascii=False))
        f.write("\n---\n")


def write_query_error(output_dir: Path, payload: Dict[str, object]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    error_path = output_dir / "query_error.json"
    error_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return error_path


def filter_detections_by_area(
    detections: List[Dict[str, object]],
    image_size: Tuple[int, int],
    min_box_area_ratio: float,
    max_box_area_ratio: float,
    large_box_confidence_override: float,
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    width, height = image_size
    image_area = float(max(1, width * height))
    kept: List[Dict[str, object]] = []
    dropped: List[Dict[str, object]] = []

    for det in detections:
        box = det["box"]
        w = max(0.0, float(box[2]) - float(box[0]))
        h = max(0.0, float(box[3]) - float(box[1]))
        ratio = (w * h) / image_area
        det["box_area_ratio"] = ratio

        score = float(det.get("score") or 0.0)
        large_box_allowed = ratio > max_box_area_ratio and score >= large_box_confidence_override
        if ratio < min_box_area_ratio or (ratio > max_box_area_ratio and not large_box_allowed):
            det["drop_reason"] = (
                f"box_area_ratio={ratio:.4f} not in [{min_box_area_ratio:.4f}, {max_box_area_ratio:.4f}]"
            )
            dropped.append(det)
        else:
            if large_box_allowed:
                det["large_box_override"] = True
            kept.append(det)

    kept.sort(key=lambda x: float(x.get("score") or 0.0), reverse=True)
    dropped.sort(key=lambda x: float(x.get("score") or 0.0), reverse=True)
    return kept, dropped


def filter_detections_by_confidence(
    detections: List[Dict[str, object]],
    min_confidence: float,
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    if min_confidence <= 0.0:
        return detections, []

    kept: List[Dict[str, object]] = []
    dropped: List[Dict[str, object]] = []
    for det in detections:
        score = float(det.get("score") or 0.0)
        if score >= min_confidence:
            kept.append(det)
        else:
            det["drop_reason"] = f"score={score:.4f} < min_confidence={min_confidence:.4f}"
            dropped.append(det)
    return kept, dropped


def _box_iou(box_a: List[float], box_b: List[float]) -> float:
    ax1, ay1, ax2, ay2 = [float(v) for v in box_a]
    bx1, by1, bx2, by2 = [float(v) for v in box_b]
    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)
    inter_w = max(0.0, inter_x2 - inter_x1)
    inter_h = max(0.0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - inter_area
    if union <= 0.0:
        return 0.0
    return inter_area / union


def deduplicate_cross_label_detections(
    detections: List[Dict[str, object]],
    iou_threshold: float,
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    if iou_threshold <= 0.0 or len(detections) <= 1:
        return detections, []

    ordered = sorted(detections, key=lambda x: float(x.get("score") or 0.0), reverse=True)
    kept: List[Dict[str, object]] = []
    dropped: List[Dict[str, object]] = []
    for det in ordered:
        current_box = [float(v) for v in det["box"]]
        is_duplicate = False
        for accepted in kept:
            accepted_box = [float(v) for v in accepted["box"]]
            if _box_iou(current_box, accepted_box) >= iou_threshold:
                det["drop_reason"] = (
                    f"cross_label_duplicate_iou>={iou_threshold:.2f} with label={accepted.get('label')}"
                )
                dropped.append(det)
                is_duplicate = True
                break
        if not is_duplicate:
            kept.append(det)
    return kept, dropped


def infer_stage_b_labels_from_stage_a(
    stage_a_detections: List[Dict[str, object]],
    candidate_labels: List[str],
    stage1_score_threshold: float,
    stage1_topk: int,
) -> List[str]:
    if not candidate_labels:
        return []

    scores: Dict[str, float] = {label: 0.0 for label in candidate_labels}
    for det in stage_a_detections:
        raw_label = str(det.get("label", "")).lower()
        det_score = float(det.get("score") or 0.0)
        for label in candidate_labels:
            # GroundingDINO labels can contain punctuation or combined pieces.
            if re.search(rf"(^|[^a-z]){re.escape(label)}([^a-z]|$)", raw_label):
                if det_score > scores[label]:
                    scores[label] = det_score

    selected = [label for label, score in scores.items() if score >= stage1_score_threshold]
    if not selected:
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        fallback = [label for label, score in ranked if score > 0.0]
        if fallback:
            selected = fallback
        else:
            # If Stage A gives no usable mapping, keep first labels as conservative fallback.
            selected = candidate_labels[:]

    if stage1_topk > 0:
        selected = selected[:stage1_topk]
    return selected


def run(
    sam_model_id: str,
    detector_model_id: str,
    image_files: Sequence[Path],
    output_dir: Path,
    text_prompt: str,
    target_labels: Optional[List[str]],
    device: str,
    max_side: int,
    cpu_threads: int,
    box_threshold: float,
    text_threshold: float,
    min_box_area_ratio: float,
    max_box_area_ratio: float,
    max_boxes: int,
    min_confidence: float,
    large_box_confidence_override: float,
    dedup_iou_threshold: float,
    detect_mode: str,
    stage1_topk: int,
    stage1_score_threshold: float,
    resize_mode: str,
    llm_trace: Optional[Dict[str, object]],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "report.txt"
    if report_path.exists():
        report_path.unlink()

    if device == "cpu":
        torch.set_num_threads(cpu_threads)
        if cpu_threads > 1:
            torch.set_num_interop_threads(max(1, cpu_threads // 2))
        print(f"[INFO] CPU threads: {torch.get_num_threads()}")

    run_meta = {
        "sam_model_id": sam_model_id,
        "detector_model_id": detector_model_id,
        "text_prompt": text_prompt,
        "target_labels": target_labels or [],
        "device": device,
        "max_side": max_side,
        "box_threshold": box_threshold,
        "text_threshold": text_threshold,
        "min_box_area_ratio": min_box_area_ratio,
        "max_box_area_ratio": max_box_area_ratio,
        "max_boxes": max_boxes,
        "min_confidence": min_confidence,
        "large_box_confidence_override": large_box_confidence_override,
        "dedup_iou_threshold": dedup_iou_threshold,
        "detect_mode": detect_mode,
        "stage1_topk": stage1_topk,
        "stage1_score_threshold": stage1_score_threshold,
        "resize_mode": resize_mode,
        "cpu_threads": cpu_threads if device == "cpu" else None,
        "images": [str(p) for p in image_files],
        "llm_trace": llm_trace or {},
    }
    (output_dir / "run_config.json").write_text(
        json.dumps(run_meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    if llm_trace is not None:
        (output_dir / "llm_parse.json").write_text(
            json.dumps(llm_trace, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    print(f"[INFO] Loading detector processor: {detector_model_id}")
    detector_processor = AutoProcessor.from_pretrained(detector_model_id)
    print(f"[INFO] Loading detector model: {detector_model_id}")
    detector_model = AutoModelForZeroShotObjectDetection.from_pretrained(detector_model_id).to(device)
    detector_model.eval()

    # --- ДОБАВИТЬ ЭТОТ БЛОК ДЛЯ FP16 ---
    if device == "cuda":
        detector_model = detector_model.half()
    # -----------------------------------

    sam_processor, sam_model = load_sam_components(sam_model_id=sam_model_id, device=device)

    # --- ДОБАВИТЬ ЭТОТ БЛОК ДЛЯ FP16 ---
    if device == "cuda":
        sam_model = sam_model.half()
    # -----------------------------------

    for image_path in image_files:
        original_image = Image.open(image_path).convert("RGB")
        image, _resize_scale, original_size = prepare_image_and_prompts(
            image=original_image,
            max_side=max_side,
            resize_mode=resize_mode,
        )
        raw_detections: List[Dict[str, object]] = []
        label_queries = target_labels or []
        if label_queries and detect_mode == "hybrid":
            stage_a = detect_boxes_from_text(
                detector_processor=detector_processor,
                detector_model=detector_model,
                image=image,
                text_prompt=text_prompt,
                device=device,
                box_threshold=box_threshold,
                text_threshold=text_threshold,
            )
            stage_b_labels = infer_stage_b_labels_from_stage_a(
                stage_a_detections=stage_a,
                candidate_labels=label_queries,
                stage1_score_threshold=stage1_score_threshold,
                stage1_topk=stage1_topk,
            )
            for label in stage_b_labels:
                per_label = detect_boxes_from_text(
                    detector_processor=detector_processor,
                    detector_model=detector_model,
                    image=image,
                    text_prompt=label,
                    device=device,
                    box_threshold=box_threshold,
                    text_threshold=text_threshold,
                )
                for det in per_label:
                    det["label"] = label
                raw_detections.extend(per_label)
        elif label_queries:
            for label in label_queries:
                per_label = detect_boxes_from_text(
                    detector_processor=detector_processor,
                    detector_model=detector_model,
                    image=image,
                    text_prompt=label,
                    device=device,
                    box_threshold=box_threshold,
                    text_threshold=text_threshold,
                )
                for det in per_label:
                    det["label"] = label
                raw_detections.extend(per_label)
        elif text_prompt.strip():
            raw_detections = detect_boxes_from_text(
                detector_processor=detector_processor,
                detector_model=detector_model,
                image=image,
                text_prompt=text_prompt,
                device=device,
                box_threshold=box_threshold,
                text_threshold=text_threshold,
            )
        if not raw_detections:
            print(f"[WARN] {image_path.name} -> no objects found for prompt: '{text_prompt}'")
            out_prefix = build_image_output_prefix(output_dir, image_path)
            save_detections_json([], image.size, out_prefix)
            save_boxes_preview(image, [], out_prefix, save_when_empty=True)
            save_empty_segmentation_artifacts(original_image, out_prefix)
            append_report_block(report_path, image_path.name, [])
            continue

        deduped, dedup_dropped = deduplicate_cross_label_detections(
            detections=raw_detections,
            iou_threshold=dedup_iou_threshold,
        )
        detections, dropped = filter_detections_by_area(
            detections=deduped,
            image_size=image.size,
            min_box_area_ratio=min_box_area_ratio,
            max_box_area_ratio=max_box_area_ratio,
            large_box_confidence_override=large_box_confidence_override,
        )
        dropped.extend(dedup_dropped)
        detections, dropped_by_conf = filter_detections_by_confidence(
            detections=detections,
            min_confidence=min_confidence,
        )
        dropped.extend(dropped_by_conf)
        if max_boxes > 0:
            detections = detections[:max_boxes]

        if not detections:
            print(
                f"[WARN] {image_path.name} -> all boxes filtered out "
                f"(raw={len(raw_detections)}, dropped={len(dropped)})."
            )
            out_prefix = build_image_output_prefix(output_dir, image_path)
            save_detections_json(raw_detections, original_size, out_prefix)
            save_boxes_preview(image, [], out_prefix, save_when_empty=True)
            save_empty_segmentation_artifacts(original_image, out_prefix)
            append_report_block(report_path, image_path.name, [])
            continue

        out_prefix = build_image_output_prefix(output_dir, image_path)
        save_boxes_preview(image, detections, out_prefix)  # Для превью оставляем уменьшенное
        save_detections_json(raw_detections, original_size, out_prefix)

        # Запуск SAM (на уменьшенном изображении с уменьшенными боксами)
        if device == "cuda":
            with torch.autocast(device_type=device, dtype=torch.float16):
                merged_mask, report_detections, individual_masks = build_merged_mask_and_report(
                    sam_processor=sam_processor,
                    sam_model=sam_model,
                    image=image,  # уменьшенное
                    detections=detections,  # ещё НЕ масштабированные
                    device=device,
                )
        else:
            merged_mask, report_detections, individual_masks = build_merged_mask_and_report(
                sam_processor=sam_processor,
                sam_model=sam_model,
                image=image,
                detections=detections,
                device=device,
            )

        # Масштабируем маски к оригиналу
        mask_uint8 = merged_mask
        if image.size != original_size:
            mask_uint8 = np.array(
                Image.fromarray(mask_uint8, mode="L").resize(original_size, Image.Resampling.NEAREST)
            )
            individual_masks = [
                np.array(Image.fromarray(m, mode="L").resize(original_size, Image.Resampling.NEAREST))
                for m in individual_masks
            ]
            
            # Масштабируем боксы к оригиналу (ПОСЛЕ SAM!)
            scale_x = original_size[0] / image.size[0]
            scale_y = original_size[1] / image.size[1]
            scaled_detections = []
            for det in detections:
                box = det["box"]
                scaled_box = [
                    box[0] * scale_x,
                    box[1] * scale_y,
                    box[2] * scale_x,
                    box[3] * scale_y,
                ]
                scaled_detections.append({**det, "box": scaled_box})
            detections = scaled_detections

        mask_path, overlay_path = save_outputs_colored(
            original_image,
            mask_uint8,
            out_prefix,
            detections,  # теперь отмасштабированные
            individual_masks
        )
        
        append_report_block(report_path, image_path.name, report_detections)
        top = detections[0]
        print(
            f"[OK] {image_path.name} -> {mask_path.name}, {overlay_path.name}, "
            f"boxes={len(detections)}, top={top.get('label')} score={top.get('score')}"
        )
        
        # --- ДОБАВИТЬ ЭТОТ БЛОК ---
        if device == "cuda":
            torch.cuda.empty_cache()
        # --------------------------
        
    # Выход из цикла for
    print(f"[DONE] Results saved to: {output_dir}")
    print(f"[DONE] Report saved to: {report_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Text + image segmentation using GroundingDINO (text->boxes) + SAM (boxes->mask)."
    )
    parser.add_argument(
        "--sam-model-id",
        default="facebook/sam-vit-base",
        help="HF model id for SAM.",
    )
    parser.add_argument(
        "--detector-model-id",
        default="IDEA-Research/grounding-dino-tiny",
        help="HF model id for text-to-box detector.",
    )
    parser.add_argument("--image", type=Path, help="Path to a single image.")
    parser.add_argument("--images-dir", type=Path, help="Path to a directory with images.")
    parser.add_argument(
        "--text",
        default="object",
        help="Text prompt, e.g. 'rat' or 'person'. If omitted, generic 'object' is used.",
    )
    parser.add_argument(
        "--query",
        default=None,
        help="Natural-language query, e.g. 'find all objects' or 'cat, dog'. Overrides --text.",
    )
    parser.add_argument(
        "--label-dictionary",
        choices=["none", "coco"],
        default="coco",
        help="Deprecated and ignored.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("sam3_outputs"),
        help="Where to save masks and overlays.",
    )
    parser.add_argument(
        "--device",
        default="cuda" if torch.cuda.is_available() else "cpu",
        choices=["cpu", "cuda"],
        help="Device for inference.",
    )
    parser.add_argument(
        "--max-side",
        type=int,
        default=None,
        help="Resize image to this max side before inference (faster, less RAM).",
    )
    parser.add_argument(
        "--cpu-threads",
        type=int,
        default=max(1, (os.cpu_count() or 4) // 2),
        help="Number of CPU threads for torch.",
    )
    parser.add_argument(
        "--preset",
        choices=["cpu_safe", "balanced", "quality"],
        default="cpu_safe",
        help="Runtime profile. cpu_safe is default for weak hardware.",
    )
    parser.add_argument(
        "--box-threshold",
        type=float,
        default=0.25,
        help="Detector confidence threshold for boxes.",
    )
    parser.add_argument(
        "--text-threshold",
        type=float,
        default=0.20,
        help="Detector text match threshold.",
    )
    parser.add_argument(
        "--min-box-area-ratio",
        type=float,
        default=0.002,
        help="Drop boxes smaller than this area ratio.",
    )
    parser.add_argument(
        "--max-box-area-ratio",
        type=float,
        default=0.85,
        help="Drop boxes larger than this area ratio.",
    )
    parser.add_argument(
        "--max-boxes",
        type=int,
        default=20,
        help="Maximum number of boxes to pass to SAM after filtering.",
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.45,
        help="Minimum detection confidence to keep.",
    )
    parser.add_argument(
        "--large-box-confidence-override",
        type=float,
        default=0.90,
        help="Keep very large boxes if score is above this value.",
    )
    parser.add_argument(
        "--dedup-iou-threshold",
        type=float,
        default=0.92,
        help="Drop overlapping cross-label duplicate boxes above this IoU.",
    )
    parser.add_argument(
        "--no-filters",
        action="store_true",
        help="Disable area/box limits (useful for quick full-pass batch runs).",
    )
    parser.add_argument(
        "--filters-mode",
        choices=["auto", "on", "off"],
        default="auto",
        help="Filter behavior: on/off or auto (recommended: auto keeps filters enabled).",
    )
    parser.add_argument(
        "--query-parser",
        choices=["auto", "rule", "llm"],
        default="llm",
        help="Method to parse user query into labels.",
    )
    parser.add_argument(
        "--llm-model-id",
        default="Qwen/Qwen2.5-1.5B-Instruct",
        help="LLM for query-to-label parsing.",
    )
    parser.add_argument(
        "--llm-max-new-tokens",
        type=int,
        default=96,
        help="Max new tokens for LLM structured output.",
    )
    parser.add_argument(
        "--strict-query-classes",
        action="store_true",
        default=True,
        help="Stop pipeline if no valid classes extracted from user query.",
    )
    parser.add_argument(
        "--resize-mode",
        choices=["downscale_only", "force"],
        default="downscale_only",
        help="Resize policy: downscale_only avoids upscaling small images.",
    )
    parser.add_argument(
        "--detect-mode",
        choices=["per_class", "hybrid", "single_prompt"],
        default="hybrid",
        help="Detection strategy: hybrid does stage-A then per-class stage-B.",
    )
    parser.add_argument(
        "--stage1-topk",
        type=int,
        default=5,
        help="In hybrid mode, run Stage-B only for top-K labels.",
    )
    parser.add_argument(
        "--stage1-score-threshold",
        type=float,
        default=0.30,
        help="In hybrid mode, keep labels from Stage-A above this score.",
    )
    args = parser.parse_args()

    if args.max_side is None:
        if args.preset == "cpu_safe":
            args.max_side = 768
        elif args.preset == "balanced":
            args.max_side = 1024
        else:
            args.max_side = 1536

    user_query = args.query if args.query is not None else args.text
    llm_trace: Dict[str, object] = {
        "query_parser": args.query_parser,
        "user_query": user_query,
        "llm_model_id": args.llm_model_id,
        "status": "not_used",
        "raw_text": "",
        "labels": [],
        "error": "",
    }

    no_user_prompt = args.query is None and args.text.strip().lower() == "object"
    if no_user_prompt:
        # No prompt from user -> generic open-vocabulary search without dictionary expansion.
        effective_prompt = "object."
        target_labels: List[str] = []
        llm_trace["status"] = "skipped_no_prompt"
    else:
        target_labels = []
        if args.query_parser == "rule":
            effective_prompt = build_effective_prompt(user_query, args.label_dictionary)
            target_labels = clean_plausible_labels(normalize_labels([c.strip() for c in effective_prompt.split(".") if c.strip()]))
            llm_trace["status"] = "skipped_rule_parser"
            llm_trace["labels"] = target_labels
        elif args.query_parser == "llm":
            llm_result = resolve_query_with_llm(
                query=user_query,
                llm_model_id=args.llm_model_id,  # Игнорируется в новой версии
                device=args.device,               # Игнорируется
                llm_max_new_tokens=max(16, args.llm_max_new_tokens),
    )
            llm_trace.update(
                {
                    "status": llm_result.get("status", "unknown"),
                    "raw_text": llm_result.get("raw_text", ""),
                    "labels": llm_result.get("labels", []),
                    "error": llm_result.get("error", ""),
                }
            )
            if llm_result.get("ok"):
                effective_prompt = str(llm_result["prompt"])
                target_labels = clean_plausible_labels(normalize_labels([str(x) for x in llm_result.get("labels", [])]))
            else:
                print("[WARN] LLM returned no explicit classes. Skipping detections for this query.")
                effective_prompt = ""
                target_labels = []
        else:
            # Auto: LLM-only for natural language queries, no dictionary fallback.
            looks_natural = args.query is not None or (" " in user_query.strip())
            if looks_natural:
                llm_result = resolve_query_with_llm(
                    query=user_query,
                    llm_model_id=args.llm_model_id,
                    device=args.device,
                    llm_max_new_tokens=max(16, args.llm_max_new_tokens),
                )
                llm_trace.update(
                    {
                        "status": llm_result.get("status", "unknown"),
                        "raw_text": llm_result.get("raw_text", ""),
                        "labels": llm_result.get("labels", []),
                        "error": llm_result.get("error", ""),
                    }
                )
                if llm_result.get("ok"):
                    effective_prompt = str(llm_result["prompt"])
                    target_labels = clean_plausible_labels(normalize_labels([str(x) for x in llm_result.get("labels", [])]))
                else:
                    print("[WARN] LLM returned no explicit classes. Skipping detections for this query.")
                    effective_prompt = ""
                    target_labels = []
            else:
                effective_prompt = ""
                target_labels = []
                llm_trace["status"] = "skipped_auto_non_natural"

    # Guardrail: for explicit user query we stop early when no classes were extracted.
    if (
        args.strict_query_classes
        and args.query is not None
        and not no_user_prompt
        and not effective_prompt.strip()
    ):
        payload = {
            "ok": False,
            "error": "invalid_query_no_classes",
            "message": "Failed to extract valid object classes from query. Please provide a clearer request.",
            "query": user_query,
            "llm_trace": llm_trace,
        }
        error_path = write_query_error(args.output_dir, payload)
        print("[ERROR] Invalid query: no classes extracted. Detection pipeline stopped.")
        print(f"[ERROR] Details saved to: {error_path}")
        return

    disable_filters = args.no_filters
    if args.filters_mode == "off":
        disable_filters = True
    elif args.filters_mode == "on":
        disable_filters = False
    elif args.filters_mode == "auto":
        disable_filters = args.no_filters

    if disable_filters:
        args.box_threshold = 0.0
        args.text_threshold = 0.0
        args.min_box_area_ratio = 0.0
        args.max_box_area_ratio = 1.0
        args.max_boxes = 0
    else:
        # Safe defaults to avoid giant noisy outputs in "find all" mode.
        if args.box_threshold <= 0.0:
            args.box_threshold = 0.25
        if args.text_threshold <= 0.0:
            args.text_threshold = 0.25
        if args.max_boxes <= 0:
            args.max_boxes = 5

    images = collect_images(args.image, args.images_dir)
    run(
        sam_model_id=args.sam_model_id,
        detector_model_id=args.detector_model_id,
        image_files=images,
        output_dir=args.output_dir,
        text_prompt=effective_prompt,
        target_labels=target_labels,
        device=args.device,
        max_side=args.max_side,
        cpu_threads=max(1, args.cpu_threads),
        box_threshold=args.box_threshold,
        text_threshold=args.text_threshold,
        min_box_area_ratio=max(0.0, args.min_box_area_ratio),
        max_box_area_ratio=min(1.0, args.max_box_area_ratio),
        max_boxes=max(0, args.max_boxes),
        min_confidence=max(0.0, min(1.0, args.min_confidence)),
        large_box_confidence_override=max(0.0, min(1.0, args.large_box_confidence_override)),
        dedup_iou_threshold=max(0.0, min(1.0, args.dedup_iou_threshold)),
        detect_mode=args.detect_mode,
        stage1_topk=max(0, args.stage1_topk),
        stage1_score_threshold=max(0.0, min(1.0, args.stage1_score_threshold)),
        resize_mode=args.resize_mode,
        llm_trace=llm_trace,
    )
def get_distinct_color(index: int) -> Tuple[int, int, int]:
    """Генерирует уникальный цвет для каждого объекта по индексу."""
    # Используем золотое сечение для равномерного распределения цветов
    golden_ratio = 0.618033988749895
    hue = (index * golden_ratio) % 1.0
    
    # Конвертация HSV в RGB вручную (чтобы не тащить лишние библиотеки)
    h = hue
    s = 0.8
    v = 0.9
    
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i %= 6
    
    if i == 0: r, g, b = v, t, p
    elif i == 1: r, g, b = q, v, p
    elif i == 2: r, g, b = p, v, t
    elif i == 3: r, g, b = p, q, v
    elif i == 4: r, g, b = t, p, v
    elif i == 5: r, g, b = v, p, q
    
    return (int(r * 255), int(g * 255), int(b * 255))

if __name__ == "__main__":
    main()
