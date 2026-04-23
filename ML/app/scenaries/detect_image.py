"""
Сценарий обработки одного запроса детекции.

Новый поток (Gemma 4 Vision):
    1. Пока llama-server (Gemma) работает — для каждой картинки:
       a. Vision-вызов: картинка + prompt → [{"label", "confidence"}]
       b. Confidence-фильтр (min >= 0.6 по умолчанию)
       c. Relevance-фильтр (текстовый вызов Gemma без картинки)
    2. Собираем per-image словарь {image_name: [labels]}.
    3. Останавливаем Gemma (освобождаем VRAM).
    4. Запускаем detection_pipline.py с labels.json (SAM3).
    5. Перезапускаем Gemma для следующего запроса.
    6. Читаем report.txt и возвращаем результат.
"""

import json
import logging
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from config.settings import VisionConfig
from app.base_pipline.gemma_client import extract_labels_for_image

logger = logging.getLogger(__name__)

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}


def _stop_llama_server() -> None:
    """Убивает процесс llama-server чтобы освободить VRAM для SAM3."""
    logger.info("Stopping llama-server to free VRAM...")
    try:
        if platform.system() == "Windows":
            subprocess.run(["taskkill", "/F", "/IM", "llama-server.exe"], capture_output=True)
        else:
            subprocess.run(["pkill", "-f", "llama-server"], capture_output=True)
        time.sleep(1)
        logger.info("llama-server stopped")
    except Exception as e:
        logger.warning(f"Could not stop llama-server: {e}")


def _start_llama_server() -> None:
    """Перезапускает llama-server (Gemma) и ждёт готовности."""
    logger.info("Restarting llama-server...")
    try:
        from services import LlamaServer
        server = LlamaServer()
        if server.start(timeout=180):
            logger.info("llama-server restarted successfully")
        else:
            logger.error("llama-server failed to restart")
    except Exception as e:
        logger.error(f"Could not restart llama-server: {e}")


def _collect_images(source_path: Path) -> List[Path]:
    return sorted(
        p for p in source_path.iterdir()
        if p.is_file() and p.suffix.lower() in VALID_EXTENSIONS
    )


def _analyze_images_with_gemma(
    images: List[Path],
    query: str,
    output_dir: Path,
) -> Dict[str, List[str]]:
    """
    Для каждой картинки вызывает Gemma Vision + relevance filter.
    Возвращает mapping {image_name: [labels]}.
    Сохраняет трассу в output_dir/gemma_analysis.json.
    """
    labels_per_image: Dict[str, List[str]] = {}
    trace: List[dict] = []

    for idx, img_path in enumerate(images, 1):
        logger.info(f"[Gemma {idx}/{len(images)}] {img_path.name}")
        result = extract_labels_for_image(img_path, query)

        labels_per_image[img_path.name] = result["labels"]
        trace.append({
            "image": img_path.name,
            "labels": result["labels"],
            "labels_raw": result["labels_raw"],
            "filtered_by_confidence": result["filtered_by_confidence"],
            "filtered_by_relevance": result["filtered_by_relevance"],
            "status": result["status"],
            "error": result["error"],
        })

        if result["labels"]:
            logger.info(f"  → {result['labels']}")
        else:
            logger.info("  → [] (ничего релевантного)")

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "gemma_analysis.json").write_text(
        json.dumps({"query": query, "per_image": trace}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return labels_per_image


class ImageDetectionUseCase:
    def execute(
        self,
        query_id: int,
        dir_path: str,
        prompt: str,
    ) -> Tuple[str, dict, list[dict]]:
        if not dir_path:
            raise ValueError("dir_path cannot be empty")
        if not Path(dir_path).exists():
            raise FileNotFoundError(f"Path does not exist: {dir_path}")

        base = Path(dir_path)
        source_path = base / str(query_id) / "source"
        save_path = base / str(query_id) / "result"

        if not source_path.exists():
            raise FileNotFoundError(f"Source path does not exist: {source_path}")

        effective_prompt = (prompt or "").strip()
        if not effective_prompt:
            raise ValueError("prompt cannot be empty")

        images = _collect_images(source_path)
        if not images:
            raise FileNotFoundError(f"No images found in: {source_path}")

        # 1. Gemma Vision + relevance filter для каждой картинки
        labels_per_image = _analyze_images_with_gemma(images, effective_prompt, save_path)

        # Если НИ для одной картинки не найдено релевантных меток —
        # сохраняем ошибку и возвращаем пустой результат.
        total_labels = sum(len(v) for v in labels_per_image.values())
        if total_labels == 0:
            logger.warning("Gemma не нашла ни одного релевантного объекта")
            save_path.mkdir(parents=True, exist_ok=True)
            (save_path / "report.txt").write_text("", encoding="utf-8")
            return str(save_path), {}, []

        # 2. Останавливаем Gemma — освобождаем VRAM для SAM3
        _stop_llama_server()

        try:
            # 3. SAM3 подпроцесс с per-image labels JSON
            self._run_sam_pipeline(
                source_path=source_path,
                save_path=save_path,
                labels_per_image=labels_per_image,
                original_query=effective_prompt,
            )
        finally:
            # 4. Перезапускаем Gemma для следующего запроса
            _start_llama_server()

        counts, instance_infos = self._read_report(save_path / "report.txt")
        return str(save_path), counts, instance_infos

    def _run_sam_pipeline(
        self,
        source_path: Path,
        save_path: Path,
        labels_per_image: Dict[str, List[str]],
        original_query: str = "",
    ) -> None:
        save_path.mkdir(parents=True, exist_ok=True)
        labels_json_path = save_path / "labels_per_image.json"
        labels_json_path.write_text(
            json.dumps(labels_per_image, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        script_path = Path(__file__).resolve().parents[1] / "base_pipline" / "detection_pipline.py"
        cmd = [
            sys.executable,
            str(script_path),
            "--images-dir", str(source_path),
            "--labels-json", str(labels_json_path),
            "--output-dir", str(save_path),
            "--sam3-checkpoint", VisionConfig.get_checkpoint_path(),
        ]
        if original_query:
            cmd += ["--original-query", original_query]

        completed = subprocess.run(cmd, capture_output=True, text=True)
        if completed.returncode != 0:
            raise RuntimeError(
                "SAM pipeline failed.\n"
                f"stdout:\n{completed.stdout}\n"
                f"stderr:\n{completed.stderr}"
            )

        query_error = save_path / "query_error.json"
        if query_error.exists():
            payload = json.loads(query_error.read_text(encoding="utf-8"))
            raise ValueError(payload.get("message", "Invalid query for class extraction"))

    def _read_report(self, report_path: Path) -> Tuple[dict, list[dict]]:
        counts: dict[str, int] = {}
        instance_infos: list[dict] = []
        if not report_path.exists():
            return counts, instance_infos

        lines = report_path.read_text(encoding="utf-8").splitlines()
        idx = 0
        while idx < len(lines):
            img_name = lines[idx].strip()
            idx += 1
            if not img_name:
                continue
            if idx >= len(lines):
                break
            json_line = lines[idx].strip()
            idx += 1
            try:
                detections = json.loads(json_line) if json_line else []
            except json.JSONDecodeError:
                detections = []

            for det in detections:
                cls_name = str(det.get("class", "unknown"))
                conf = float(det.get("confidence", 0.0))
                bbox = [float(v) for v in det.get("bbox", [])]
                counts[cls_name] = counts.get(cls_name, 0) + 1
                instance_infos.append({
                    "class_name": cls_name,
                    "confidence": conf,
                    "bbox": bbox,
                })

            if idx < len(lines) and lines[idx].strip() == "---":
                idx += 1

        return counts, instance_infos
