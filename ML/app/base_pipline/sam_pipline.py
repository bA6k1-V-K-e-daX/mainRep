from pathlib import Path
from typing import List, Dict, Tuple

import numpy as np
import torch
from PIL import Image

from transformers import Sam3Model, Sam3Processor

from config.settings import VisionConfig


def _resize_to_max(image: Image.Image, max_size: int) -> Image.Image:
    w, h = image.size
    if max(w, h) <= max_size:
        return image
    scale = max_size / max(w, h)
    return image.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)


def load_sam3_components(checkpoint_path: str, device: str) -> Tuple[Sam3Processor, Sam3Model]:
    """Загружает SAM3 из локальной папки (model.safetensors + config.json).
    Для CUDA использует fp16 для экономии VRAM."""
    print(f"[INFO] Loading SAM3 from: {checkpoint_path}")
    dtype = torch.float16 if device == "cuda" else torch.float32
    model = Sam3Model.from_pretrained(checkpoint_path, torch_dtype=dtype)
    model = model.to(device).eval()
    processor = Sam3Processor.from_pretrained(checkpoint_path)
    print("[INFO] SAM3 loaded successfully")
    return processor, model


def run_sam3_detections(
    processor: Sam3Processor,
    model: Sam3Model,
    images: List[Image.Image],
    labels: List[str],
    device: str,
    score_threshold: float = 0.0,
) -> List[List[Dict]]:
    """
    Запускает SAM3 для батча изображений и каждой текстовой метки.

    Возвращает List[List[Dict]] — один список детекций на каждое изображение:
      [{'label': str, 'score': float, 'box': [x1,y1,x2,y2], '_mask': np.ndarray HxW uint8}]

    '_mask' — бинарная маска (0/255) в пространстве исходного изображения.
    Ключ '_mask' должен быть удалён перед сохранением в JSON.
    """
    orig_sizes = [img.size for img in images]
    images_resized = [_resize_to_max(img, VisionConfig.MAX_IMAGE_SIZE) for img in images]
    img_sizes = [img.size for img in images_resized]

    autocast_ctx = (
        torch.autocast(device_type="cuda", dtype=torch.float16)
        if device == "cuda"
        else torch.autocast(device_type="cpu", enabled=False)
    )

    # Кодируем все изображения батча за один вызов
    img_inputs = processor(images=images_resized, return_tensors="pt").to(device)
    with torch.no_grad(), autocast_ctx:
        vision_embeds = model.get_vision_features(pixel_values=img_inputs.pixel_values)

    target_sizes = img_inputs.get("original_sizes")
    if target_sizes is not None:
        target_sizes = target_sizes.tolist()
    else:
        target_sizes = [[h, w] for (w, h) in img_sizes]

    all_detections: List[List[Dict]] = [[] for _ in images]

    for label in labels:
        text_inputs = processor(
            text=[label] * len(images), return_tensors="pt", padding=True
        ).to(device)

        with torch.no_grad(), autocast_ctx:
            outputs = model(
                vision_embeds=vision_embeds,
                input_ids=text_inputs.input_ids,
                attention_mask=text_inputs.attention_mask,
            )

        results_list = processor.post_process_instance_segmentation(
            outputs,
            threshold=score_threshold,
            mask_threshold=0.5,
            target_sizes=target_sizes,
        )

        for img_idx, (results, (orig_w, orig_h)) in enumerate(zip(results_list, orig_sizes)):
            masks = results.get("masks", [])
            scores = results.get("scores", [])

            for mask_t, score_t in zip(masks, scores):
                score = float(score_t)
                mask_np = mask_t.cpu().numpy().astype(np.uint8) * 255

                # Resize к оригинальному размеру если нужно
                if mask_np.shape != (orig_h, orig_w):
                    mask_img = Image.fromarray(mask_np, mode="L").resize(
                        (orig_w, orig_h), Image.Resampling.NEAREST
                    )
                    mask_np = np.array(mask_img)

                # Bbox из маски
                coords = np.where(mask_np > 0)
                if len(coords[0]) == 0:
                    continue
                y1, y2 = int(coords[0].min()), int(coords[0].max())
                x1, x2 = int(coords[1].min()), int(coords[1].max())

                all_detections[img_idx].append({
                    "label": label,
                    "score": score,
                    "box": [float(x1), float(y1), float(x2), float(y2)],
                    "_mask": mask_np,
                })

    return all_detections
