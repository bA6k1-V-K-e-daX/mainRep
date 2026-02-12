# app/services/container.py
from app.services.model_loader import ModelLoader
from app.services.file_manager import FileManager

class ServiceContainer:
    """Простой контейнер зависимостей"""

    def __init__(self):
        self._file_manager = None
        self._model_loader = None

    @property
    def file_manager(self):
        if self._file_manager is None:
            self._file_manager = FileManager()
        return self._file_manager

    @property
    def model_loader(self):
        if self._model_loader is None:
            self._model_loader = ModelLoader(
                model_filename="yolov8n.pt",
                device="cpu"  # или "cuda", если есть GPU
            )
        return self._model_loader