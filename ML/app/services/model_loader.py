
from ultralytics import YOLO
from pathlib import Path

__all__ = ['ModelLoader', 'public_function']

class ModelLoader:
    def __init__(self, model_filename="yolov8n.pt", device="cpu"):
        self.model_filename = model_filename
        self.device = device
        self.model = None
        self.models_dir = self.__get_models_dir()

    def __get_models_dir(self) -> str:
        """Определяет папку с моделями"""
        current_dir = Path(__file__).parent.parent
        models_dir = current_dir / "models"
        
        if not models_dir.exists():
            models_dir = Path.cwd() / "models"
            models_dir.mkdir(exist_ok=True)
        
        return models_dir
    
    def __load_model(self) -> bool:
        """Загрузка модели из папки models"""
        try:
            model_path = self.models_dir / self.model_filename

            if not model_path.exists():
                raise FileNotFoundError(
                    f"Модель '{self.model_filename}' не найдена в папке {self.models_dir}\n"
                    f"Убедитесь, что файл модели находится в папке 'models'"
                )
            
            self.model = YOLO(model_path)
            
            self.model.to(self.device)
            
            return True
            
        except FileNotFoundError as e:
            raise
        except Exception as e:
            raise

    def get_model(self) -> YOLO:
        if self.model is None:
            try:
                self.__load_model()
            except:
                raise RuntimeError(f"Ошибка во время загрузки {self.model_filename} в {self.device}")
        return self.model
         

        

    
