# config/__init__.py
from .settings import (
    LLMConfig,
    VisionConfig,
    GRPCConfig,
    setup_pytorch_env,
    validate_paths,
    IS_WINDOWS,
    IS_DOCKER,
    IS_LINUX,
)

__all__ = [
    "LLMConfig",
    "VisionConfig", 
    "GRPCConfig",
    "setup_pytorch_env",
    "validate_paths",
    "IS_WINDOWS",
    "IS_DOCKER",
    "IS_LINUX",
]

# Автоматически применяем настройки PyTorch при импорте
setup_pytorch_env()