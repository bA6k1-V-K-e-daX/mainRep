from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch
from PIL import Image
from transformers import SamModel, SamProcessor


def pick_best_mask(masks: torch.Tensor, iou_scores: torch.Tensor) -> np.ndarray:
    masks_cpu = masks.detach().cpu()
    scores_cpu = iou_scores.detach().cpu()

    if masks_cpu.ndim == 4 and scores_cpu.ndim == 2:
        best_idx = int(torch.argmax(scores_cpu[0]).item())
        selected = masks_cpu[0, best_idx]
    elif masks_cpu.ndim == 3 and scores_cpu.ndim == 1:
        best_idx = int(torch.argmax(scores_cpu).item())
        selected = masks_cpu[best_idx]
    elif masks_cpu.ndim == 2:
        selected = masks_cpu
    else:
        selected = masks_cpu.reshape(-1, masks_cpu.shape[-2], masks_cpu.shape[-1])[0]

    mask_np = selected.numpy() > 0
    return mask_np.astype(np.uint8) * 255


def load_sam_components(sam_model_id: str, device: str) -> Tuple[SamProcessor, SamModel]:
    print(f"[INFO] Loading SAM processor: {sam_model_id}")
    sam_processor = SamProcessor.from_pretrained(sam_model_id)
    print(f"[INFO] Loading SAM model: {sam_model_id}")
    sam_model = SamModel.from_pretrained(sam_model_id).to(device)
    sam_model.eval()
    return sam_processor, sam_model


def build_merged_mask_and_report(
    sam_processor: SamProcessor,
    sam_model: SamModel,
    image: Image.Image,
    detections: List[Dict[str, object]],
    device: str,
) -> Tuple[np.ndarray, List[Dict[str, object]], List[np.ndarray]]:
    merged_mask = np.zeros((image.height, image.width), dtype=np.uint8)
    report_detections: List[Dict[str, object]] = []
    individual_masks: List[np.ndarray] = []

    for det in detections:
        box = det["box"]
        sam_inputs = sam_processor(
            images=image,
            input_boxes=[[box]],
            return_tensors="pt",
        ).to(device)
        with torch.no_grad():
            outputs = sam_model(**sam_inputs, multimask_output=True)

        masks = sam_processor.image_processor.post_process_masks(
            outputs.pred_masks.cpu(),
            sam_inputs["original_sizes"].cpu(),
            sam_inputs["reshaped_input_sizes"].cpu(),
        )[0]
        iou_scores = outputs.iou_scores[0]
        box_mask = pick_best_mask(masks, iou_scores)
        merged_mask = np.maximum(merged_mask, box_mask)
        individual_masks.append(box_mask)
        report_detections.append(
            {
                "class": str(det.get("label", "unknown")),
                "confidence": float(det.get("score") or 0.0),
                "bbox": [float(v) for v in box],
            }
        )

    return merged_mask, report_detections, individual_masks

