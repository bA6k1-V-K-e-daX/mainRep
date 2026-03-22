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
class LLMConfig:
    """Настройки llama-server"""
    
    _DEFAULT_SERVER_WIN = r"C:\llama.cpp\llama-server.exe"
    _DEFAULT_SERVER_DOCKER = "/host-llama/llama-server"
    _DEFAULT_SERVER_LINUX = "/opt/llama.cpp/llama-server"
    
    _DEFAULT_MODEL_WIN = r"C:\llama.cpp\models\Qwen2.5-1.5B-Instruct-Q4_K_M.gguf"
    _DEFAULT_MODEL_DOCKER = "/host-llama/models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf"
    _DEFAULT_MODEL_LINUX = "/opt/llama.cpp/models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf"
    
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
    
    PORT = int(os.getenv("LLAMA_PORT", "8080"))
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
    """Проверяет существование критических файлов"""
    return {
        "llama_server": Path(LLMConfig.get_server_path()).exists(),
        "llama_model": Path(LLMConfig.get_model_path()).exists(),
        "grpc_module": Path(*GRPCConfig.MODULE.split('.')).with_suffix('.py').exists(),
    }