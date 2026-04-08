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


# === LLM Сервер (llama.cpp) ===
# === LLM Сервер (llama.cpp) ===
class LLMConfig:
    """Настройки llama-server — работают в Docker и на хосте"""
    
    # Пути для Windows (хост)
    _DEFAULT_SERVER_WIN = r"C:\llama.cpp\llama-server.exe"
    _DEFAULT_MODEL_WIN = r"C:\llama.cpp\models\Qwen2.5-3B-Instruct-Q8_0.gguf"
    
    # Пути для Docker (контейнер) — ✅ ИСПРАВЛЕНО!
    _DEFAULT_SERVER_DOCKER = "/app/llama-bin/llama-server"
    _DEFAULT_MODEL_DOCKER = "/app/models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf"
    
    # Пути для Linux (хост)
    _DEFAULT_SERVER_LINUX = "/opt/llama.cpp/llama-server"
    _DEFAULT_MODEL_LINUX = "/opt/llama.cpp/models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf"
    
    @classmethod
    def get_server_path(cls) -> str:
        """Возвращает путь к llama-server с приоритетом env-переменной"""
        if IS_DOCKER:
            default = cls._DEFAULT_SERVER_DOCKER
        elif IS_WINDOWS:
            default = cls._DEFAULT_SERVER_WIN
        else:
            default = cls._DEFAULT_SERVER_LINUX
        # Env-переменная всегда имеет приоритет
        return os.getenv("LLAMA_SERVER_PATH", default)
    
    @classmethod
    def get_model_path(cls) -> str:
        """Возвращает путь к модели с приоритетом env-переменной"""
        if IS_DOCKER:
            default = cls._DEFAULT_MODEL_DOCKER
        elif IS_WINDOWS:
            default = cls._DEFAULT_MODEL_WIN
        else:
            default = cls._DEFAULT_MODEL_LINUX
        # Env-переменная всегда имеет приоритет
        return os.getenv("LLAMA_MODEL_PATH", default)
    
    # === Остальные настройки (без изменений) ===
    PORT = int(os.getenv("LLAMA_PORT", "8081"))  # ← 8081, а не 8080!
    HOST = os.getenv("LLAMA_HOST", "127.0.0.1")
    NGL = os.getenv("LLAMA_NGL", "99")
    CONTEXT = int(os.getenv("LLAMA_CONTEXT", "2048"))
    THREADS = os.getenv("LLAMA_THREADS", "4")
    
    FLASH_ATTN = os.getenv("LLAMA_FLASH_ATTN", "on")
    CACHE_REUSE = os.getenv("LLAMA_CACHE_REUSE", "256")
    NO_MMAP = os.getenv("LLAMA_NO_MMAP", "true").lower() == "true"
    
    @classmethod
    def get_base_url(cls) -> str:
        return f"http://{cls.HOST}:{cls.PORT}"
    
    @classmethod
    def get_health_url(cls) -> str:
        return f"{cls.get_base_url()}/health"
    
    @classmethod
    def get_chat_url(cls) -> str:
        return f"{cls.get_base_url()}/v1/chat/completions"

# === Vision модели (DINO, SAM) ===
class VisionConfig:
    """Настройки для Grounding DINO и SAM"""
    
    DINO_MODEL_ID = os.getenv("DINO_MODEL_ID", "IDEA-Research/grounding-dino-tiny")
    SAM_MODEL_ID = os.getenv("SAM_MODEL_ID", "facebook/sam-vit-base")
    
    # ✅ Теперь torch_available() видна, так как она на уровне модуля
    DEVICE = os.getenv("VISION_DEVICE", "cuda" if torch_available() else "cpu")
    
    MAX_IMAGE_SIDE = int(os.getenv("VISION_MAX_SIDE", "640"))
    BOX_THRESHOLD = float(os.getenv("DINO_BOX_THRESHOLD", "0.25"))
    TEXT_THRESHOLD = float(os.getenv("DINO_TEXT_THRESHOLD", "0.20"))
    
    USE_TORCH_COMPILE = os.getenv("VISION_TORCH_COMPILE", "true").lower() == "true"
    USE_XFORMERS = os.getenv("VISION_XFORMERS", "true").lower() == "true"
    USE_FLASH_ATTN = os.getenv("VISION_FLASH_ATTN", "true").lower() == "true"


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
    
    # Отладочный вывод (попадает в docker logs)
    print(f"[DEBUG] validate_paths: server={server_path}", file=sys.stderr)
    print(f"[DEBUG] validate_paths: model={model_path}", file=sys.stderr)
    
    checks = {
        "llama_server": Path(server_path).exists() and os.access(server_path, os.X_OK),
        "llama_model": Path(model_path).exists() and Path(model_path).stat().st_size > 100_000_000,  # >100MB
        "grpc_module": _check_grpc_module(),  # вынесли в отдельную функцию
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