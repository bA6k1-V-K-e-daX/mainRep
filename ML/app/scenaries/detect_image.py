from ultralytics import YOLO
from pathlib import Path
from app.utils.generate_report import save_summary_report
from pathlib import Path
from typing import List
from app.utils.names_to_ids import class_names_to_ids
from app.core.di_container import ServiceContainer

class ImageDetectionUseCase:
    def __init__(self):
        container = ServiceContainer()
        self.model_loader = container.model_loader

    def execute(
        self,
        query_id: int,
        dir_path: str,
        targets: List[str],
        min_confidence: float = 0.5
    ):
        # Валидация
        if not dir_path:
            raise ValueError("dir_path cannot be empty")
        if not Path(dir_path).exists():
            raise FileNotFoundError(f"Path does not exist: {dir_path}")

        # Подготовка путей
        base = Path(dir_path)
        source_path = str(base / "detect" / f"query_{query_id}" / "source")
        save_path = str(base / "detect" / f"query_{query_id}" / "result")

        # Загрузка модели и преобразование целей
        model = self.model_loader.get_model()
        target_ids = class_names_to_ids(targets) if targets else None

        # Запуск детекции
        detection_result = self._detect_image(
            source_path=source_path,
            save_path=save_path,
            target_ids=target_ids,
            min_confidence=min_confidence,
            model=model
        )
        return save_path, detection_result
           

    def _detect_image(self, source_path: str, save_path: str, target_ids=None, min_confidence=0.5, model: YOLO = None):
        """
        Выполняет детекцию на одном изображении,
        а также сохраняет результат в папку results
        """
        results = model(
            source_path,
            conf=min_confidence,
            classes=target_ids,      # ← фильтрация на уровне модели
            save=True,
            project=Path(save_path).parent, 
            name=Path(save_path).name, 
            exist_ok=True,
            verbose=False,
        )
        
        if results:
            print(f"💾 Файл сохранён в: {results[0].save_dir}")
            print(f"📦 Найдено боксов: {len(results[0].boxes)}")
        else:
            print("⚠️ Нет результатов")

        # Собираем результаты — без фильтрации!
        counts = {}
        names = model.names
        
        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls.item())
                cls_name = names[cls_id]
                counts[cls_name] = counts.get(cls_name, 0) + 1
        if results:
            report_file = Path(save_path) / "detection_summary.txt"
            save_summary_report(results, model.names, str(report_file))
        else:
            print("⚠️ Нет обработанных изображений — отчёт не создан")
                
        return counts
