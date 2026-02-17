# app/services/container.py
from app.services.model_loader import ModelLoader

class ServiceContainer:
    """Простой контейнер зависимостей"""

    def __init__(self):
        self._file_manager = None
        self._model_loader = None

    @property
    def model_loader(self):
        if self._model_loader is None:
            self._model_loader = ModelLoader(
                model_filename="yolov8n.pt",
                device="cpu"  # или "cuda", если есть GPU
            )
        return self._model_loader