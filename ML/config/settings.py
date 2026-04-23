# config/settings.py
import os
import platform
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Определяем среду выполнения
IS_WINDOWS = platform.system() == "Windows"
IS_DOCKER = os.getenv("RUNNING_IN_DOCKER", "false").lower() == "true"
IS_LINUX = platform.system() == "Linux"

# === Утилиты (вынесены за пределы классов) ===
def torch_available() -> bool:
    """Проверяет доступность CUDA без импорта torch в глобальной области"""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False
    except Exception as e:
        logger.debug(f"CUDA check failed: {e}")
        return False


# === LLM Сервер (llama.cpp) — Gemma 4 Vision ===
class LLMConfig:
    """Настройки llama-server для Gemma 4 Vision (multimodal GGUF + mmproj)"""

    _MODEL_FILENAME = "google_gemma-4-E4B-it-Q4_K_M.gguf"
    _MMPROJ_FILENAME = "mmproj-google_gemma-4-E4B-it-f16.gguf"

    # Пути для Windows (хост)
    _DEFAULT_SERVER_WIN = r"C:\llama.cpp\llama-server.exe"
    _DEFAULT_MODEL_WIN = rf"C:\llama.cpp\models\{_MODEL_FILENAME}"
    _DEFAULT_MMPROJ_WIN = rf"C:\llama.cpp\models\{_MMPROJ_FILENAME}"

    # Пути для Docker
    _DEFAULT_SERVER_DOCKER = "/app/llama-bin/llama-server"
    _DEFAULT_MODEL_DOCKER = f"/app/models/{_MODEL_FILENAME}"
    _DEFAULT_MMPROJ_DOCKER = f"/app/models/{_MMPROJ_FILENAME}"

    # Пути для Linux (хост)
    _DEFAULT_SERVER_LINUX = "/opt/llama.cpp/llama-server"
    _DEFAULT_MODEL_LINUX = f"/opt/llama.cpp/models/{_MODEL_FILENAME}"
    _DEFAULT_MMPROJ_LINUX = f"/opt/llama.cpp/models/{_MMPROJ_FILENAME}"

    @classmethod
    def get_server_path(cls) -> str:
        if IS_DOCKER:
            default = cls._DEFAULT_SERVER_DOCKER
        elif IS_WINDOWS:
            default = cls._DEFAULT_SERVER_WIN
        else:
            default = cls._DEFAULT_SERVER_LINUX
        return os.getenv("LLAMA_SERVER_PATH", default)

    @classmethod
    def get_model_path(cls) -> str:
        if IS_DOCKER:
            default = cls._DEFAULT_MODEL_DOCKER
        elif IS_WINDOWS:
            default = cls._DEFAULT_MODEL_WIN
        else:
            default = cls._DEFAULT_MODEL_LINUX
        return os.getenv("LLAMA_MODEL_PATH", default)

    @classmethod
    def get_mmproj_path(cls) -> str:
        """Путь к multimodal projector (mmproj) — обязателен для Gemma Vision"""
        if IS_DOCKER:
            default = cls._DEFAULT_MMPROJ_DOCKER
        elif IS_WINDOWS:
            default = cls._DEFAULT_MMPROJ_WIN
        else:
            default = cls._DEFAULT_MMPROJ_LINUX
        return os.getenv("LLAMA_MMPROJ_PATH", default)

    # === Параметры запуска Gemma (под конкретную команду) ===
    PORT = int(os.getenv("LLAMA_PORT", "8000"))
    HOST = os.getenv("LLAMA_HOST", "127.0.0.1")
    NGL = os.getenv("LLAMA_NGL", "20")
    CONTEXT = int(os.getenv("LLAMA_CONTEXT", "8192"))
    BATCH_SIZE = int(os.getenv("LLAMA_BATCH_SIZE", "256"))
    UBATCH_SIZE = int(os.getenv("LLAMA_UBATCH_SIZE", "256"))
    PARALLEL = int(os.getenv("LLAMA_PARALLEL", "1"))
    NO_KV_OFFLOAD = os.getenv("LLAMA_NO_KV_OFFLOAD", "true").lower() == "true"
    FLASH_ATTN = os.getenv("LLAMA_FLASH_ATTN", "on").lower() in ("true", "1", "on", "yes")

    # === Фильтрация меток от Gemma (как в test_gemma) ===
    MIN_GEMMA_CONFIDENCE = float(os.getenv("GEMMA_MIN_CONFIDENCE", "0.6"))
    USE_RELEVANCE_FILTER = os.getenv("GEMMA_USE_RELEVANCE_FILTER", "true").lower() == "true"

    @classmethod
    def get_base_url(cls) -> str:
        return f"http://{cls.HOST}:{cls.PORT}"

    @classmethod
    def get_health_url(cls) -> str:
        return f"{cls.get_base_url()}/health"

    @classmethod
    def get_chat_url(cls) -> str:
        return f"{cls.get_base_url()}/v1/chat/completions"

# === Vision модели (SAM3) ===
class VisionConfig:
    """Настройки для SAM3 (detection + segmentation в одной модели)"""

    # Путь к папке с весами SAM3 (содержит model.safetensors + config.json)
    _DEFAULT_CHECKPOINT_WIN = r"C:\models\sam3"
    _DEFAULT_CHECKPOINT_DOCKER = "/app/models/sam3"
    _DEFAULT_CHECKPOINT_LINUX = "/opt/models/sam3"

    @classmethod
    def get_checkpoint_path(cls) -> str:
        if IS_DOCKER:
            default = cls._DEFAULT_CHECKPOINT_DOCKER
        elif IS_WINDOWS:
            default = cls._DEFAULT_CHECKPOINT_WIN
        else:
            default = cls._DEFAULT_CHECKPOINT_LINUX
        return os.getenv("SAM3_CHECKPOINT_PATH", default)

    DEVICE = os.getenv("VISION_DEVICE", "cuda" if torch_available() else "cpu")

    # Порог уверенности для детекций SAM3
    SCORE_THRESHOLD = float(os.getenv("SAM3_SCORE_THRESHOLD", "0.30"))
    MAX_BOXES = int(os.getenv("SAM3_MAX_BOXES", "20"))
    MAX_IMAGE_SIZE = int(os.getenv("SAM3_MAX_IMAGE_SIZE", "512"))
    IMAGE_BATCH_SIZE = int(os.getenv("SAM3_IMAGE_BATCH_SIZE", "2"))


# === gRPC Сервер ===
class GRPCConfig:
    """Настройки gRPC сервера"""
    
    MODULE = os.getenv("GRPC_SERVER_MODULE", "app.grps.server")
    PORT = int(os.getenv("GRPC_PORT", "50051"))
    HOST = os.getenv("GRPC_HOST", "0.0.0.0")
    MAX_WORKERS = int(os.getenv("GRPC_MAX_WORKERS", "4"))


# === Общие настройки PyTorch ===
def setup_pytorch_env():
    """Применяет оптимизации PyTorch через переменные окружения"""
    os.environ['PYTORCH_CUDA_ALLOC_CONF'] = os.getenv(
        'PYTORCH_CUDA_ALLOC_CONF', 
        'max_split_size_mb:512'
    )
    os.environ['CUDA_VISIBLE_DEVICES'] = os.getenv('CUDA_VISIBLE_DEVICES', '0')


# === Утилиты ===
def validate_paths() -> dict[str, bool]:
    """Проверяет существование критических файлов с логированием"""
    import sys
    
    server_path = LLMConfig.get_server_path()
    model_path = LLMConfig.get_model_path()
    mmproj_path = LLMConfig.get_mmproj_path()

    print(f"[DEBUG] validate_paths: server={server_path}", file=sys.stderr)
    print(f"[DEBUG] validate_paths: model={model_path}", file=sys.stderr)
    print(f"[DEBUG] validate_paths: mmproj={mmproj_path}", file=sys.stderr)

    checks = {
        "llama_server": Path(server_path).exists() and os.access(server_path, os.X_OK),
        "llama_model": Path(model_path).exists() and Path(model_path).stat().st_size > 100_000_000,
        "llama_mmproj": Path(mmproj_path).exists() and Path(mmproj_path).stat().st_size > 10_000_000,
        "grpc_module": _check_grpc_module(),
    }
    
    # Лог результатов
    for name, ok in checks.items():
        status = "✅" if ok else "❌"
        print(f"[DEBUG] {status} {name}", file=sys.stderr)
    
    return checks


def _check_grpc_module() -> bool:
    """Проверяет доступность gRPC модуля"""
    try:
        # Пробуем найти файл относительно /app (Docker) или cwd (хост)
        module_path = Path(*GRPCConfig.MODULE.split('.')).with_suffix('.py')
        
        # Проверяем несколько возможных путей
        if module_path.exists():
            return True
        if (Path("app") / module_path).exists():  # ← Исправлено: скобки!
            return True
        if (Path("/app") / module_path).exists():  # Для Docker
            return True
            
        # Если файл не нашли — пробуем импортировать
        __import__(GRPCConfig.MODULE)
        return True
    except Exception:
        return False