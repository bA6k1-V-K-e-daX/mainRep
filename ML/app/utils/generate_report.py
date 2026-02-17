from ultralytics.engine.results import Results
import json
from pathlib import Path
def save_summary_report(
    results: list[Results],
    model_names: dict,
    output_txt_path: str
) -> None:
    """
    Сохраняет сводный TXT-отчёт по всем обработанным изображениям.
    
    Формат отчёта:
        image1.jpg
        {"person": 2, "car": 1}
        ---
        image2.jpg
        {"dog": 1}
        ---
        ...
    
    Args:
        results (list[Results]): Список результатов от YOLO-модели (результат вызова model(...))
        model_names (dict): Словарь {class_id: "class_name"}, обычно model.names
        output_txt_path (str): Путь к итоговому .txt файлу (например, "results/detect/query_123/summary.txt")
    """
    output_path = Path(output_txt_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        for result in results:
            # Получаем путь к исходному изображению
            img_path = getattr(result, 'path', 'unknown_image.jpg')
            img_name = Path(img_path).name

            # Считаем объекты по классам
            counts = {}
            if hasattr(result, 'boxes') and result.boxes is not None:
                for cls_id in result.boxes.cls.cpu().numpy():
                    cls_name = model_names[int(cls_id)]
                    counts[cls_name] = counts.get(cls_name, 0) + 1

            # Записываем в файл
            f.write(f"{img_name}\n")
            f.write(json.dumps(counts, ensure_ascii=False, indent=0))
            f.write("\n---\n")
    
    print(f"📄 Сводный отчёт сохранён: {output_path}")