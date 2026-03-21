import json
import subprocess
import sys
from pathlib import Path
from typing import Tuple

class ImageDetectionUseCase:
    def execute(
        self,
        query_id: int,
        dir_path: str,
        prompt: str,
        min_confidence: float = 0.5
    ) -> tuple[str, dict, list[dict]]:
        # Валидация
        if not dir_path:
            raise ValueError("dir_path cannot be empty")
        if not Path(dir_path).exists():
            raise FileNotFoundError(f"Path does not exist: {dir_path}")

        # Подготовка путей (совместимо с текущей структурой volume/<query_id>/{source,result})
        base = Path(dir_path)
        source_path = base / str(query_id) / "source"
        save_path = base / str(query_id) / "result"

        if not source_path.exists():
            raise FileNotFoundError(f"Source path does not exist: {source_path}")

        effective_prompt = (prompt or "").strip()
        if not effective_prompt:
            raise ValueError("prompt cannot be empty")

        self._run_sam_pipeline(
            source_path=source_path,
            save_path=save_path,
            prompt=effective_prompt,
        )

        counts, instance_infos = self._read_report(save_path / "report.txt")
        return str(save_path), counts, instance_infos

    def _run_sam_pipeline(self, source_path: Path, save_path: Path, prompt: str) -> None:
        script_path = Path(__file__).resolve().parents[1] / "scripts" / "sam3_quick_test.py"
        cmd = [
            sys.executable,
            str(script_path),
            "--images-dir",
            str(source_path),
            "--query",
            prompt,
            "--query-parser",
            "llm",
            "--output-dir",
            str(save_path),
        ]
        completed = subprocess.run(cmd, capture_output=True, text=True)
        if completed.returncode != 0:
            raise RuntimeError(
                "SAM pipeline failed.\n"
                f"stdout:\n{completed.stdout}\n"
                f"stderr:\n{completed.stderr}"
            )

        # Query guardrail in new pipeline: stop on bad query.
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
                instance_infos.append(
                    {
                        "class_name": cls_name,
                        "confidence": conf,
                        "bbox": bbox,
                    }
                )

            if idx < len(lines) and lines[idx].strip() == "---":
                idx += 1

        return counts, instance_infos
