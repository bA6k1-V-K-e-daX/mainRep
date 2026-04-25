#!/usr/bin/env python3
"""
Gemma 4 Vision + SAM3 Pipeline
Полный пайплайн для обработки изображений с мультимодальной LLM и сегментацией
"""

import base64
import json
import re
import gc
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from io import BytesIO

import requests
import numpy as np
from PIL import Image, ImageDraw


# ============================================================
# КОНФИГУРАЦИЯ
# ============================================================

GEMMA_URL = "http://localhost:8000"
SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".tif"}

# Промпты для Gemma 4 Vision
# Промпты для Gemma 4 Vision — FALLBACK ВЕРСИЯ
SYSTEM_PROMPT = """You are a visual object detector. Your entire output MUST be a single JSON array and NOTHING else.

OUTPUT FORMAT (strict):
- ONLY a JSON array like [{"label": "car", "confidence": 0.9}, {"label": "dog", "confidence": 0.7}] or []
- Each element MUST be an object: {"label": "<lowercase noun>", "confidence": <float 0.0–1.0>}
- confidence = how certain the object is BOTH present in the image AND relevant to the user's request
- Omit any object where confidence < 0.5 — do not include it at all
- NO explanations, NO reasoning, NO markdown fences, NO comments, NO prose before or after

HOW TO DECIDE (do this mentally, do NOT write it down):
A. First, list what you ACTUALLY see in the image — ignore the user request for a moment.
B. Then, check the user's request. Which of the things you saw in step A match it?
C. Output only those. If NONE match, output [].

CRITICAL ANTI-HALLUCINATION RULES:
- Do NOT output a label just because the user asked about it. A request for "wheels" on an image of a cat → [].
- Do NOT copy words from the request into the output unless you literally see the object.
- If the user asks for a narrow type (e.g. "only cars" / "только машины"), return [] for related-but-different objects — bus, truck, bicycle, train, motorcycle are NOT cars.
- The most prominent object in the image is NOT automatically a match. A close-up cat is still [] for a "find vehicles" request.
- Cartoons/drawings count (cartoon cat = "cat"), but do not invent objects that are not drawn.
- "wheels" / "колёса": only return ["wheel"] if a wheel is LARGE AND CLEARLY VISIBLE as the main subject. A car in the distance has wheels but they are not visibly prominent → []. A bicycle close-up with the wheel filling the frame → ["wheel"].

LABEL STYLE:
- Specific English nouns, lowercase. "tram" not "train car", "sedan"→"car", "puppy"→"dog".
- Broad requests get specific labels: "transport" + you see a bus → ["bus"], not ["transport"].
- Deduplicate: 5 cars → ["car"] once.

EXAMPLES (request | what is in the image | correct output):
- "find animals"           | a horse with a rider                     | ["horse"]
- "find animals"           | a parked car, no animals                 | []
- "only cars" / "машины"   | a bus                                    | []
- "only cars" / "машины"   | a train                                  | []
- "only cars" / "машины"   | a bicycle                                | []
- "only cars" / "машины"   | a sedan and an SUV                       | ["car"]
- "find all vehicles"      | a cat close-up                           | []
- "find all vehicles"      | a dog on a sidewalk                      | []
- "find all vehicles"      | a horse in a field                       | []
- "find wheels"            | a cat lying on the floor                 | []
- "find wheels"            | a horse in a field                       | []
- "find wheels"            | a cartoon drawing with no wheels         | []
- "find wheels"            | a bicycle close-up, wheel fills frame    | ["wheel"]
- "find wheels"            | a bus where wheels are small/cropped out | []
- "find furniture"         | an outdoor photo of a cat by a pot       | []
- "find furniture"         | a bird on a branch                       | []
- "find furniture"         | a woman reading on a sofa                | ["sofa"]
- "find food"              | an empty street                          | []
- "find food"              | a cat, no food visible                   | []
- "find transport"         | a cat on a chair                         | []

Your entire response is the JSON array. Nothing else. Example of valid output:
[{"label": "car", "confidence": 0.92}, {"label": "bicycle", "confidence": 0.61}]"""

USER_PROMPT_TEMPLATE = """User's request: "{prompt}"

Step A (mentally): identify what is ACTUALLY in this image.
Step B (mentally): keep only items that match the request above, assign confidence 0.0–1.0.
Step C (output): JSON array of {{"label": "...", "confidence": ...}} objects, or [] if none match.

Output ONLY the JSON array. No reasoning text."""


# ============================================================
# ФУНКЦИИ ДЛЯ РАБОТЫ С GEMMA 4 VISION
# ============================================================

def parse_labels_from_response(raw_text: str) -> List[Dict]:
    """
    Извлекает список {"label": str, "confidence": float} из ответа Gemma.
    Берёт ПОСЛЕДНИЙ валидный JSON-массив в тексте (после любого reasoning).
    Если JSON не найден — возвращает [] вместо угадывания.
    Дедуплицирует лейблы с сохранением порядка.
    """
    raw_text = raw_text.strip()

    # Ищем ВСЕ кандидаты на JSON-массив, пытаемся распарсить с конца.
    # Это защищает от случаев когда модель привела пример массива в reasoning,
    # а финальный ответ идёт в конце.
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

        # Фильтр мусора + дедуп с сохранением порядка
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

    # JSON не найден — модель не соблюдала формат. Не угадываем.
    return []


def analyze_single_image(
    image: Image.Image,
    prompt: str,
    image_name: str = "image.jpg",
    gemma_url: str = GEMMA_URL,
    max_tokens: int = 256,
    temperature: float = 0.0,
    timeout: int = 60,
    max_image_size: int = 2048,  # Увеличено для лучшего распознавания мелких объектов
) -> Dict:
    """
    Отправляет ОДНО изображение в Gemma 4 Vision и получает список объектов.
    """
    
    # Опциональный ресайз (можно закомментировать для максимального качества)
    if max(image.size) > max_image_size:
        ratio = max_image_size / max(image.size)
        new_size = (int(image.width * ratio), int(image.height * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)
    
    # Кодируем в base64
    buffered = BytesIO()
    image.save(buffered, format="JPEG", quality=85)  # Качество 85% для лучшего распознавания
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    # Формируем payload
    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": USER_PROMPT_TEMPLATE.format(prompt=prompt)},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False
    }
    
    try:
        response = requests.post(
            f"{gemma_url}/v1/chat/completions",
            json=payload,
            timeout=timeout,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        result = response.json()
        raw_text = result["choices"][0]["message"]["content"].strip()
        labels = parse_labels_from_response(raw_text)
        
        return {
            "labels": labels,
            "raw_response": raw_text,
            "status": "success",
            "error": None
        }
        
    except requests.exceptions.ConnectionError:
        return {"labels": [], "raw_response": "", "status": "error", "error": f"Cannot connect to Gemma at {gemma_url}"}
    except requests.exceptions.Timeout:
        return {"labels": [], "raw_response": "", "status": "error", "error": f"Request timeout after {timeout}s"}
    except Exception as e:
        return {"labels": [], "raw_response": "", "status": "error", "error": str(e)}


RELEVANCE_FILTER_SYSTEM = (
    "You are a strict relevance filter. "
    "Given a user request and a list of detected objects, "
    "return ONLY the objects that belong to the category the user asked for. "
    "Output a JSON array of strings like [\"car\", \"bus\"], or [] if none match. "
    "Nothing else — no explanations, no markdown, no extra text."
)


def filter_labels_by_relevance(
    query: str,
    labels: List[str],
    gemma_url: str = GEMMA_URL,
    timeout: int = 30,
) -> List[str]:
    """
    Text-only Gemma call: filters `labels` to those relevant to `query`.
    No image is sent — pure relevance reasoning.
    Falls back to returning all labels if the call fails.
    """
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
            f"{gemma_url}/v1/chat/completions",
            json=payload,
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        raw = response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"  [WARN] Relevance filter failed ({e}), keeping all labels")
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


def process_images_with_gemma_vision(
    prompt: str,
    images_folder: str,
    gemma_url: str = GEMMA_URL,
    max_tokens: int = 256,
    temperature: float = 0.0,
    timeout: int = 60,
    save_results: bool = True,
    output_file: Optional[str] = None,
    use_relevance_filter: bool = True,
) -> Dict:
    """
    Отправляет ВСЕ изображения из папки в Gemma 4 Vision с одним промптом.
    """
    
    images_folder = Path(images_folder)
    if not images_folder.exists():
        raise FileNotFoundError(f"Folder not found: {images_folder}")
    
    # Собираем все изображения
    image_paths = []
    for ext in SUPPORTED_FORMATS:
        image_paths.extend(images_folder.glob(f"*{ext}"))
        image_paths.extend(images_folder.glob(f"*{ext.upper()}"))
    
    image_paths = sorted(set(image_paths))
    
    if not image_paths:
        raise ValueError(f"No supported images found in: {images_folder}")
    
    print(f"[INFO] Found {len(image_paths)} images in {images_folder}")
    print(f"[INFO] Prompt: '{prompt}'")
    print(f"[INFO] Gemma URL: {gemma_url}")
    print("-" * 60)
    
    results = []
    
    for idx, img_path in enumerate(image_paths, 1):
        print(f"[{idx}/{len(image_paths)}] Processing: {img_path.name}")
        
        try:
            image = Image.open(img_path).convert("RGB")
            result = analyze_single_image(
                image=image,
                prompt=prompt,
                image_name=img_path.name,
                gemma_url=gemma_url,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=timeout
            )
            
            labels_with_conf = result.get("labels", [])

            if use_relevance_filter and labels_with_conf:
                raw_strings = [item["label"] for item in labels_with_conf]
                relevant_strings = filter_labels_by_relevance(prompt, raw_strings, gemma_url)
                relevant_set = set(relevant_strings)
                filtered_out = [item["label"] for item in labels_with_conf if item["label"] not in relevant_set]
                labels_with_conf = [item for item in labels_with_conf if item["label"] in relevant_set]
                if filtered_out:
                    print(f"  ✗ Irrelevant (filtered): {filtered_out}")

            results.append({
                "image": str(img_path),
                "image_name": img_path.name,
                "labels": labels_with_conf,
                "raw_response": result.get("raw_response", ""),
                "status": result.get("status", "error"),
                "error": result.get("error", None)
            })

            if labels_with_conf:
                label_strs = [f"{item['label']}({item['confidence']:.2f})" for item in labels_with_conf]
                print(f"  ✓ Found: {', '.join(label_strs)}")
            else:
                print(f"  ○ No relevant objects found")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append({
                "image": str(img_path),
                "image_name": img_path.name,
                "labels": [],
                "raw_response": "",
                "status": "error",
                "error": str(e)
            })
    
    summary = {
        "prompt": prompt,
        "gemma_url": gemma_url,
        "total_images": len(image_paths),
        "images_with_objects": sum(1 for r in results if r["labels"]),
        "total_objects_found": sum(len(r["labels"]) for r in results),
        "results": results
    }
    
    if save_results:
        if output_file is None:
            output_file = images_folder / "gemma_analysis_results.json"
        else:
            output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print("-" * 60)
        print(f"[INFO] Results saved to: {output_file}")
    
    print("-" * 60)
    print(f"[SUMMARY]")
    print(f"  Total images: {summary['total_images']}")
    print(f"  Images with objects: {summary['images_with_objects']}")
    print(f"  Total objects found: {summary['total_objects_found']}")
    
    return summary


# ============================================================
# ФУНКЦИИ ДЛЯ РАБОТЫ С SAM3
# ============================================================

def get_distinct_color(index: int) -> Tuple[int, int, int]:
    """Генерирует уникальный цвет для каждого объекта."""
    golden_ratio = 0.618033988749895
    hue = (index * golden_ratio) % 1.0
    s, v = 0.8, 0.9
    
    i = int(hue * 6.0)
    f = (hue * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i %= 6
    
    if i == 0: r, g, b = v, t, p
    elif i == 1: r, g, b = q, v, p
    elif i == 2: r, g, b = p, v, t
    elif i == 3: r, g, b = p, q, v
    elif i == 4: r, g, b = t, p, v
    else: r, g, b = v, p, q
    
    return (int(r * 255), int(g * 255), int(b * 255))


def save_outputs_colored(
    image: Image.Image,
    mask_uint8: np.ndarray,
    out_prefix: Path,
    detections: List[Dict] = None,
    individual_masks: List[np.ndarray] = None
) -> Tuple[Path, Path]:
    """Сохраняет маску и оверлей с цветовой разметкой."""
    mask_path = out_prefix.with_name(f"{out_prefix.name}_mask.png")
    overlay_path = out_prefix.with_name(f"{out_prefix.name}_overlay.png")
    
    mask_img = Image.fromarray(mask_uint8, mode="L")
    mask_img.save(mask_path)
    
    overlay = image.convert("RGB").copy()
    
    if individual_masks and detections and len(individual_masks) == len(detections):
        color_mask = np.zeros((image.height, image.width, 3), dtype=np.uint8)
        
        for idx, (det, box_mask) in enumerate(zip(detections, individual_masks)):
            color = get_distinct_color(idx)
            color_mask[box_mask > 0] = color
        
        alpha = Image.fromarray((mask_uint8 > 0).astype(np.uint8) * 140, mode="L")
        color_mask_overlay = Image.fromarray(color_mask, mode="RGB")
        overlay.paste(color_mask_overlay, mask=alpha)
    else:
        red = Image.new("RGB", image.size, (255, 40, 40))
        alpha = Image.fromarray((mask_uint8 > 0).astype(np.uint8) * 110, mode="L")
        overlay.paste(red, mask=alpha)
    
    overlay.save(overlay_path)
    return mask_path, overlay_path


def save_boxes_preview(
    image: Image.Image,
    detections: List[Dict],
    out_prefix: Path,
    save_when_empty: bool = False,
) -> Optional[Path]:
    """Сохраняет превью с bounding boxes."""
    if not detections and not save_when_empty:
        return None
    
    preview = image.convert("RGB").copy()
    draw = ImageDraw.Draw(preview)
    
    for det in detections:
        box = det.get("box", det.get("bbox", []))
        if len(box) >= 4:
            label = str(det.get("label", "unknown"))
            score = det.get("score", det.get("confidence", 0))
            text = f"{label} {score:.2f}" if score else label
            draw.rectangle(box, outline=(0, 255, 0), width=2)
            text_anchor = (box[0] + 2, max(0, box[1] - 14))
            draw.text(text_anchor, text, fill=(0, 255, 0))
    
    preview_path = out_prefix.with_name(f"{out_prefix.name}_boxes.png")
    preview.save(preview_path)
    return preview_path


def save_detections_json(
    detections: List[Dict],
    image_size: Tuple[int, int],
    out_prefix: Path,
) -> Path:
    """Сохраняет детекции в JSON."""
    payload = {
        "image_size": {"width": image_size[0], "height": image_size[1]},
        "detections": detections,
    }
    json_path = out_prefix.with_name(f"{out_prefix.name}_detections.json")
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return json_path


# ============================================================
# ПОЛНЫЙ ПАЙПЛАЙН: GEMMA + SAM3
# ============================================================

def run_full_pipeline(
    prompt: str,
    images_folder: str,
    output_dir: str,
    sam3_checkpoint: str,
    gemma_url: str = GEMMA_URL,
    device: str = "cuda",
    min_confidence: float = 0.3,
    min_gemma_confidence: float = 0.6,
    save_intermediate: bool = True,
) -> Dict:
    """
    Полный пайплайн: Gemma 4 Vision → SAM3.

    Args:
        prompt: Запрос пользователя ("найди транспорт и людей")
        images_folder: Папка с изображениями
        output_dir: Папка для результатов
        sam3_checkpoint: Путь к весам SAM3
        gemma_url: URL сервера Gemma 4
        device: "cuda" или "cpu"
        min_confidence: Минимальный порог уверенности для SAM3 детекций
        min_gemma_confidence: Минимальный порог confidence из Gemma (фильтр до SAM3)
        save_intermediate: Сохранять ли промежуточные результаты Gemma

    Returns:
        Dict с полными результатами обработки
    """
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("🚀 FULL PIPELINE: Gemma 4 Vision + SAM3")
    print("=" * 60)
    
    # ========== STAGE 1: GEMMA 4 VISION ==========
    print("\n[STAGE 1] Gemma 4 Vision - analyzing images...")
    
    gemma_results = process_images_with_gemma_vision(
        prompt=prompt,
        images_folder=images_folder,
        gemma_url=gemma_url,
        save_results=save_intermediate,
        output_file=str(output_dir / "gemma_analysis.json") if save_intermediate else None
    )
    
    # Фильтруем только изображения с найденными объектами
    images_to_process = [
        r for r in gemma_results["results"]
        if r["status"] == "success" and r["labels"]
    ]
    
    print(f"\n[STAGE 1] Done. {len(images_to_process)}/{gemma_results['total_images']} images have objects for SAM3")
    
    if not images_to_process:
        print("[INFO] No objects found by Gemma. Pipeline finished.")
        return {
            "status": "completed",
            "gemma_results": gemma_results,
            "sam3_results": [],
            "message": "No objects detected by Gemma"
        }
    
    # ========== STAGE 2: SAM3 SEGMENTATION ==========
    print("\n[STAGE 2] SAM3 - segmenting detected objects...")
    print("[INFO] Loading SAM3 model...")
    
    # Импортируем SAM3 (только когда нужно)
    from app.base_pipline.sam_pipline import load_sam3_components, run_sam3_detections
    
    sam3_processor, sam3_model = load_sam3_components(
        checkpoint_path=sam3_checkpoint,
        device=device
    )
    
    sam3_results = []
    
    for idx, img_data in enumerate(images_to_process, 1):
        img_path = Path(img_data["image"])
        labels_with_conf = img_data["labels"]
        labels = [
            item["label"]
            for item in labels_with_conf
            if item.get("confidence", 1.0) >= min_gemma_confidence
        ]

        print(f"\n  [{idx}/{len(images_to_process)}] {img_path.name}")
        filtered_out = [item for item in labels_with_conf if item.get("confidence", 1.0) < min_gemma_confidence]
        if filtered_out:
            print(f"       Filtered (conf<{min_gemma_confidence}): {[item['label'] for item in filtered_out]}")

        if not labels:
            print(f"       All labels filtered by gemma_confidence >= {min_gemma_confidence}, skipping")
            continue

        print(f"       Labels: {labels}")
        
        try:
            image = Image.open(img_path).convert("RGB")
            
            # SAM3 ищет ТОЛЬКО те метки, которые Gemma подтвердила
            detections = run_sam3_detections(
                processor=sam3_processor,
                model=sam3_model,
                image=image,
                labels=labels,
                device=device
            )
            
            # Фильтрация по confidence
            detections = [d for d in detections if d.get("score", 0) >= min_confidence]
            
            # Сохраняем результаты
            out_prefix = output_dir / img_path.stem
            
            if detections:
                # Извлекаем маски
                individual_masks = [d.pop("_mask", None) for d in detections]
                individual_masks = [m for m in individual_masks if m is not None]
                
                if individual_masks:
                    merged_mask = np.zeros((image.height, image.width), dtype=np.uint8)
                    for m in individual_masks:
                        merged_mask = np.maximum(merged_mask, m)
                    
                    save_outputs_colored(
                        image, merged_mask, out_prefix,
                        detections=detections,
                        individual_masks=individual_masks
                    )
                
                detections_for_json = [{k: v for k, v in d.items() if k != "_mask"} for d in detections]
                save_detections_json(detections_for_json, image.size, out_prefix)
                save_boxes_preview(image, detections_for_json, out_prefix)
                
                print(f"       ✓ SAM3 found {len(detections)} objects")
            else:
                print(f"       ○ SAM3 found no objects (filtered by confidence)")
                save_detections_json([], image.size, out_prefix)
            
            sam3_results.append({
                "image": str(img_path),
                "image_name": img_path.name,
                "gemma_labels": labels,
                "sam3_detections": len(detections),
                "status": "success"
            })
            
        except Exception as e:
            print(f"       ✗ Error: {e}")
            sam3_results.append({
                "image": str(img_path),
                "image_name": img_path.name,
                "gemma_labels": labels,
                "sam3_detections": 0,
                "status": "error",
                "error": str(e)
            })
        
        # Очистка GPU
        if device == "cuda":
            import torch
            torch.cuda.empty_cache()
    
    # Очистка SAM3
    del sam3_model, sam3_processor
    gc.collect()
    if device == "cuda":
        import torch
        torch.cuda.empty_cache()
    
    # ========== ИТОГИ ==========
    full_results = {
        "status": "completed",
        "prompt": prompt,
        "gemma_results": {
            "total_images": gemma_results["total_images"],
            "images_with_objects": gemma_results["images_with_objects"],
            "total_objects_found": gemma_results["total_objects_found"]
        },
        "sam3_results": {
            "processed_images": len(sam3_results),
            "total_detections": sum(r["sam3_detections"] for r in sam3_results),
            "details": sam3_results
        }
    }
    
    # Сохраняем полный отчёт
    with open(output_dir / "full_pipeline_results.json", "w", encoding="utf-8") as f:
        json.dump(full_results, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print("✅ PIPELINE COMPLETED")
    print("=" * 60)
    print(f"Gemma: {gemma_results['images_with_objects']}/{gemma_results['total_images']} images with objects")
    print(f"SAM3:  {full_results['sam3_results']['total_detections']} total segmentations")
    print(f"Results saved to: {output_dir}")
    
    return full_results


# ============================================================
# ТОЧКА ВХОДА
# ============================================================

if __name__ == "__main__":
    IMAGES_FOLDER = "C:/Projects/Ml_detection/mainRep/ML/volume/3/source"
    RESULTS_DIR = Path("C:/Projects/Ml_detection/mainRep/ML/volume/3/result")
    GEMMA_URL = "http://localhost:8000"

    # (slug, prompt) — slug используется как имя файла results_<slug>.json
    TEST_PROMPTS = [
        # === Широкие категории: должны сработать на несколько изображений ===
        ("all_transport",   "хочу найти весь транспорт"),       # car, bus, bicycle, motorcycle, boat, train
        ("all_animals",     "Поищи животных"),                  # cat, dog, horse, bird

        # === Узкие типы: тест на анти-галлюцинации ===
        # "только машины" НЕ должны матчить bus/bicycle/motorcycle/train
        ("cars_only",       "найди только легковые машины"),    # только car
        ("dogs_only",       "найди только собак"),              # только dog (не cat/horse/bird)

        # === Подкатегории транспорта ===
        ("water_transport", "водный транспорт"),                # только boat
        ("rail_transport",  "рельсовый транспорт"),             # только train
        ("two_wheeled",     "двухколёсный транспорт"),          # bicycle, motorcycle

        # === Кросс-категория (общее свойство) ===
        ("wheeled",         "что-нибудь с колёсами"),           # car, bus, bicycle, motorcycle, train

        # === Одиночные объекты ===
        ("find_cat",        "Найди кота"),                      # cat
        ("find_bird",       "Птица"),                           # bird
        ("find_person",     "человек"),                         # person

        # === Семантические запросы ===
        ("pets",            "домашние питомцы"),                # cat, dog (не horse/bird)
        ("furniture",       "мебель"),                          # chair

        # === Негативный тест: должен возвращать [] на всех ===
        ("aliens",          "Найди инопланетян"),               # []

        # === Запутывающие запросы (проверка релевантности) ===
        ("healthy_cat",     "Найди здорового котяру"),          # cat (не person!)
        ("public_transport","общественный транспорт"),          # bus, train (не car/bicycle)
    ]

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    summary_rows = []

    for idx, (slug, prompt) in enumerate(TEST_PROMPTS, 1):
        print("\n" + "#" * 60)
        print(f"# [{idx}/{len(TEST_PROMPTS)}] PROMPT: '{prompt}'  →  results_{slug}.json")
        print("#" * 60)

        output_file = RESULTS_DIR / f"results_{slug}.json"

        try:
            result = process_images_with_gemma_vision(
                prompt=prompt,
                images_folder=IMAGES_FOLDER,
                gemma_url=GEMMA_URL,
                max_tokens=256,
                save_results=True,
                output_file=str(output_file),
            )
            summary_rows.append({
                "slug": slug,
                "prompt": prompt,
                "images_with_objects": result["images_with_objects"],
                "total_objects_found": result["total_objects_found"],
                "per_image": [(r["image_name"], r["labels"]) for r in result["results"]],
            })
        except Exception as e:
            print(f"[ERROR] Prompt '{prompt}' failed: {e}")
            summary_rows.append({"slug": slug, "prompt": prompt, "error": str(e)})

    # Сводная таблица по всем промптам
    print("\n\n" + "=" * 60)
    print("CROSS-PROMPT SUMMARY")
    print("=" * 60)
    for row in summary_rows:
        if "error" in row:
            print(f"  ✗ [{row['slug']}] ERROR: {row['error']}")
            continue
        print(f"\n  [{row['slug']}] '{row['prompt']}'")
        print(f"    images with objects: {row['images_with_objects']}, total labels: {row['total_objects_found']}")
        for name, label_dicts in row["per_image"]:
            marker = "✓" if label_dicts else "○"
            label_strs = [f"{item['label']}({item.get('confidence', 1.0):.2f})" for item in label_dicts]
            print(f"      {marker} {name}: {label_strs}")

    # Сохраняем общий свод
    summary_path = RESULTS_DIR / "cross_prompt_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_rows, f, indent=2, ensure_ascii=False)
    print(f"\n[INFO] Cross-prompt summary saved to: {summary_path}")