import json
import logging
import os
import platform
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Tuple

import requests

# Импортируем конфиг для пути к SAM3
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from config.settings import VisionConfig

logger = logging.getLogger(__name__)

_LLM_PORT = int(os.getenv("LLAMA_PORT", "8081"))
_LLM_URL = f"http://127.0.0.1:{_LLM_PORT}"

_QWEN_PROMPT = """
Extract ONLY visual objects from user request. Ignore greetings, emotions, filler words. Output English words separated by " . ".

CRITICAL RULES:
- Lowercase, no extra text
- Translate to English, use singular
- Extract ONLY objects (nouns) that can be seen in an image
- Specific objects ALWAYS override categories: horse NOT animal, banana NOT fruit, house NOT building
- Skip: greetings, emotions, actions, colors, sizes, "может", "как бы", "хочу", "найти", "помочь"
- Keep multi-word objects: traffic light, fire truck
- If user asks for "everything" -> object
- If no visual objects -> output nothing

Request: {user_prompt}
Answer:
"""


def _parse_query_via_llm(prompt: str) -> Optional[str]:
    """Парсит промпт через LLM HTTP API. Возвращает строку вида 'label1 . label2' или None."""
    try:
        resp = requests.post(
            f"{_LLM_URL}/v1/chat/completions",
            json={
                "messages": [{"role": "user", "content": _QWEN_PROMPT.format(user_prompt=prompt)}],
                "max_tokens": 96,
                "temperature": 0.0,
            },
            timeout=30,
        )
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.warning(f"LLM parse failed: {e}")
        return None

    cleaned = raw.replace("\n", " ").strip()
    if not cleaned or cleaned in {"none", "[]"}:
        return None

    chunks = [c.strip() for c in re.split(r"\s*\.\s*", cleaned) if c.strip()]
    if not chunks:
        return None

    # rule-парсер разбивает по запятым, поэтому используем запятую
    return ", ".join(chunks)


def _stop_llama_server() -> None:
    """Убивает процесс llama-server для освобождения VRAM."""
    logger.info("Stopping llama-server to free VRAM...")
    try:
        if platform.system() == "Windows":
            subprocess.run(
                ["taskkill", "/F", "/IM", "llama-server.exe"],
                capture_output=True,
            )
        else:
            subprocess.run(["pkill", "-f", "llama-server"], capture_output=True)
        time.sleep(1)
        logger.info("llama-server stopped")
    except Exception as e:
        logger.warning(f"Could not stop llama-server: {e}")


def _start_llama_server() -> None:
    """Перезапускает llama-server и ждёт готовности."""
    logger.info("Restarting llama-server...")
    try:
        from services import LlamaServer
        server = LlamaServer()
        if server.start(timeout=120):
            logger.info("llama-server restarted successfully")
        else:
            logger.error("llama-server failed to restart")
    except Exception as e:
        logger.error(f"Could not restart llama-server: {e}")


class ImageDetectionUseCase:
    def execute(
        self,
        query_id: int,
        dir_path: str,
        prompt: str,
    ) -> tuple[str, dict, list[dict]]:
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

        # 1. Парсим запрос через LLM (пока он ещё запущен)
        parsed_text = _parse_query_via_llm(effective_prompt)
        logger.info(f"LLM parsed labels: {parsed_text!r}")

        # 2. Останавливаем llama-server — освобождаем VRAM для DINO+SAM
        _stop_llama_server()

        try:
            # 3. Запускаем пайплайн с готовыми метками (без LLM внутри subprocess)
            self._run_sam_pipeline(
                source_path=source_path,
                save_path=save_path,
                text=parsed_text or "object",
                original_query=effective_prompt,
            )
        finally:
            # 4. Перезапускаем llama-server для следующего запроса
            _start_llama_server()

        counts, instance_infos = self._read_report(save_path / "report.txt")
        return str(save_path), counts, instance_infos

    def _run_sam_pipeline(self, source_path: Path, save_path: Path, text: str, original_query: str = "") -> None:
        script_path = Path(__file__).resolve().parents[1] / "base_pipline" / "detection_pipline.py"
        cmd = [
            sys.executable,
            str(script_path),
            "--images-dir", str(source_path),
            "--text", text,
            "--query-parser", "rule",
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
