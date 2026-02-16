from ultralytics import YOLO
from pathlib import Path
from app.utils.generate_report import save_summary_report




def detect_image(source_path: str, save_path: str, target_ids=None, min_confidence=0.5, model: YOLO = None):
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
