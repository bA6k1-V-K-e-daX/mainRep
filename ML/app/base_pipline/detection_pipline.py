"""
SAM3 detection + segmentation pipeline (subprocess).

Принимает либо:
  --text "car . person"              — один список меток на все изображения
  --labels-json /path/to/labels.json — mapping {image_name: [labels]} per-image

В новом Gemma-флоу используется --labels-json (каждая картинка имеет свои метки,
отобранные Gemma Vision + relevance filter).
"""

import argparse
import gc
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import torch
from PIL import Image, ImageDraw

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.base_pipline.sam_pipline import (
    load_sam3_components,
    run_sam3_detections,
)


VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}


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


def load_labels_per_image(path: Path) -> Dict[str, List[str]]:
    """Загружает mapping {image_name: [labels]} из JSON."""
    if not path.exists():
        raise FileNotFoundError(f"labels-json not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("labels-json must be an object mapping image_name -> list[str]")
    out: Dict[str, List[str]] = {}
    for name, labels in data.items():
        if isinstance(labels, list):
            out[str(name)] = [str(x).strip().lower() for x in labels if str(x).strip()]
        else:
            out[str(name)] = []
    return out


def parse_text_labels(text: str) -> List[str]:
    """Разбирает --text 'car . person . dog' → ['car', 'person', 'dog']."""
    if not text:
        return []
    chunks = [c.strip().lower() for c in re.split(r"[.,]", text) if c.strip()]
    seen = set()
    out = []
    for c in chunks:
        if c and c not in seen and c != "object":
            seen.add(c)
            out.append(c)
    return out


def save_outputs_colored(
    image: Image.Image,
    mask_uint8: np.ndarray,
    out_prefix: Path,
    detections: List[Dict[str, object]] = None,
    individual_masks: List[np.ndarray] = None,
) -> Tuple[Path, Path]:
    mask_img = Image.fromarray(mask_uint8, mode="L")
    mask_path = out_prefix.with_name(f"{out_prefix.name}_mask.png")
    overlay_path = out_prefix.with_name(f"{out_prefix.name}_overlay.png")

    overlay = image.convert("RGB").copy()

    if individual_masks and detections and len(individual_masks) == len(detections):
        color_mask = np.zeros((image.height, image.width, 3), dtype=np.uint8)
        for idx, (_, box_mask) in enumerate(zip(detections, individual_masks)):
            color = get_distinct_color(idx)
            color_mask[box_mask > 0] = color

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


def run(
    sam3_checkpoint_path: str,
    image_files: Sequence[Path],
    output_dir: Path,
    labels_per_image: Dict[str, List[str]],
    fallback_labels: List[str],
    device: str,
    cpu_threads: int,
    min_box_area_ratio: float,
    max_box_area_ratio: float,
    max_boxes: int,
    min_confidence: float,
    large_box_confidence_override: float,
    dedup_iou_threshold: float,
) -> None:
    """
    Основной цикл. На каждое изображение берутся метки из labels_per_image
    (по имени файла). Если нет — используются fallback_labels.
    """
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
        "sam3_checkpoint_path": sam3_checkpoint_path,
        "labels_per_image": labels_per_image,
        "fallback_labels": fallback_labels,
        "device": device,
        "min_box_area_ratio": min_box_area_ratio,
        "max_box_area_ratio": max_box_area_ratio,
        "max_boxes": max_boxes,
        "min_confidence": min_confidence,
        "large_box_confidence_override": large_box_confidence_override,
        "dedup_iou_threshold": dedup_iou_threshold,
        "cpu_threads": cpu_threads if device == "cpu" else None,
        "images": [str(p) for p in image_files],
    }
    (output_dir / "run_config.json").write_text(
        json.dumps(run_meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    sam3_processor, sam3_model = load_sam3_components(
        checkpoint_path=sam3_checkpoint_path,
        device=device,
    )

    for image_path in image_files:
        image = Image.open(image_path).convert("RGB")

        # Берём метки per-image, либо fallback
        query_labels = labels_per_image.get(image_path.name, fallback_labels)
        if not query_labels:
            print(f"[SKIP] {image_path.name} -> нет меток от Gemma, пропуск")
            out_prefix = build_image_output_prefix(output_dir, image_path)
            save_detections_json([], image.size, out_prefix)
            save_boxes_preview(image, [], out_prefix, save_when_empty=True)
            save_empty_segmentation_artifacts(image, out_prefix)
            append_report_block(report_path, image_path.name, [])
            continue

        raw_detections = run_sam3_detections(
            processor=sam3_processor,
            model=sam3_model,
            images=[image],
            labels=query_labels,
            device=device,
        )[0]

        if not raw_detections:
            print(f"[WARN] {image_path.name} -> no objects found for labels: {query_labels}")
            out_prefix = build_image_output_prefix(output_dir, image_path)
            save_detections_json([], image.size, out_prefix)
            save_boxes_preview(image, [], out_prefix, save_when_empty=True)
            save_empty_segmentation_artifacts(image, out_prefix)
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
            raw_for_json = [{k: v for k, v in d.items() if k != "_mask"} for d in raw_detections]
            save_detections_json(raw_for_json, image.size, out_prefix)
            save_boxes_preview(image, [], out_prefix, save_when_empty=True)
            save_empty_segmentation_artifacts(image, out_prefix)
            append_report_block(report_path, image_path.name, [])
            continue

        out_prefix = build_image_output_prefix(output_dir, image_path)

        detections_for_json = [{k: v for k, v in d.items() if k != "_mask"} for d in detections]
        save_detections_json(detections_for_json, image.size, out_prefix)
        save_boxes_preview(image, detections_for_json, out_prefix)

        individual_masks: List[np.ndarray] = [det.pop("_mask") for det in detections]
        merged_mask = np.zeros((image.height, image.width), dtype=np.uint8)
        for m in individual_masks:
            merged_mask = np.maximum(merged_mask, m)

        report_detections = [
            {
                "class": str(det.get("label", "unknown")),
                "confidence": float(det.get("score") or 0.0),
                "bbox": [float(v) for v in det.get("box", [])],
            }
            for det in detections
        ]

        mask_path, overlay_path = save_outputs_colored(
            image, merged_mask, out_prefix, detections, individual_masks,
        )

        append_report_block(report_path, image_path.name, report_detections)
        top = detections[0]
        print(
            f"[OK] {image_path.name} -> {mask_path.name}, {overlay_path.name}, "
            f"boxes={len(detections)}, top={top.get('label')} score={top.get('score'):.3f}"
        )

        if device == "cuda":
            torch.cuda.empty_cache()

    print(f"[DONE] Results saved to: {output_dir}")
    print(f"[DONE] Report saved to: {report_path}")

    del sam3_model, sam3_processor
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
    print("[INFO] GPU memory released")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Text-prompted detection + segmentation using SAM3."
    )
    parser.add_argument(
        "--sam3-checkpoint",
        default=os.getenv("SAM3_CHECKPOINT_PATH", ""),
        help="Path to local SAM3 checkpoint folder.",
    )
    parser.add_argument("--image", type=Path, help="Path to a single image.")
    parser.add_argument("--images-dir", type=Path, help="Path to a directory with images.")
    parser.add_argument(
        "--labels-json",
        type=Path,
        default=None,
        help="JSON file: {image_name: [labels]}. Overrides --text.",
    )
    parser.add_argument(
        "--text",
        default="",
        help="Fallback labels 'car . person . dog' applied to images not in --labels-json.",
    )
    parser.add_argument(
        "--original-query",
        default=None,
        help="Original user prompt for traceability.",
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
    )
    parser.add_argument(
        "--cpu-threads",
        type=int,
        default=max(1, (os.cpu_count() or 4) // 2),
    )
    parser.add_argument("--min-box-area-ratio", type=float, default=0.002)
    parser.add_argument("--max-box-area-ratio", type=float, default=0.85)
    parser.add_argument("--max-boxes", type=int, default=20)
    parser.add_argument("--min-confidence", type=float, default=0.30)
    parser.add_argument("--large-box-confidence-override", type=float, default=0.90)
    parser.add_argument("--dedup-iou-threshold", type=float, default=0.92)
    parser.add_argument("--no-filters", action="store_true")
    parser.add_argument(
        "--filters-mode",
        choices=["auto", "on", "off"],
        default="auto",
    )
    args = parser.parse_args()

    labels_per_image: Dict[str, List[str]] = {}
    if args.labels_json:
        labels_per_image = load_labels_per_image(args.labels_json)
        print(f"[INFO] Loaded per-image labels for {len(labels_per_image)} images")

    fallback_labels = parse_text_labels(args.text)
    if fallback_labels:
        print(f"[INFO] Fallback labels: {fallback_labels}")

    if not labels_per_image and not fallback_labels:
        payload = {
            "ok": False,
            "error": "no_labels",
            "message": "No labels provided via --labels-json or --text.",
            "query": args.original_query or "",
        }
        write_query_error(args.output_dir, payload)
        print("[ERROR] No labels to detect. Stopped.")
        return

    disable_filters = args.no_filters
    if args.filters_mode == "off":
        disable_filters = True
    elif args.filters_mode == "on":
        disable_filters = False
    elif args.filters_mode == "auto":
        disable_filters = args.no_filters

    if disable_filters:
        args.min_box_area_ratio = 0.0
        args.max_box_area_ratio = 1.0
        args.max_boxes = 0

    images = collect_images(args.image, args.images_dir)
    run(
        sam3_checkpoint_path=args.sam3_checkpoint,
        image_files=images,
        output_dir=args.output_dir,
        labels_per_image=labels_per_image,
        fallback_labels=fallback_labels,
        device=args.device,
        cpu_threads=max(1, args.cpu_threads),
        min_box_area_ratio=max(0.0, args.min_box_area_ratio),
        max_box_area_ratio=min(1.0, args.max_box_area_ratio),
        max_boxes=max(0, args.max_boxes),
        min_confidence=max(0.0, min(1.0, args.min_confidence)),
        large_box_confidence_override=max(0.0, min(1.0, args.large_box_confidence_override)),
        dedup_iou_threshold=max(0.0, min(1.0, args.dedup_iou_threshold)),
    )


def get_distinct_color(index: int) -> Tuple[int, int, int]:
    golden_ratio = 0.618033988749895
    hue = (index * golden_ratio) % 1.0
    h, s, v = hue, 0.8, 0.9

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
    else: r, g, b = v, p, q

    return (int(r * 255), int(g * 255), int(b * 255))


if __name__ == "__main__":
    main()
