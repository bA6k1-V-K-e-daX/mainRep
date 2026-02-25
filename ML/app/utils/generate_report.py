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


def save_summary_report_v2(
    results: list[Results],
    model_names: dict,
    output_txt_path: str
) -> None:
    """
    Расширенный TXT-отчёт: отдельная запись для каждой найденной сущности
    с указанием класса, уверенности и координат bounding box.

    Формат отчёта:
        image1.jpg
        [
          {"class": "person", "confidence": 0.92, "bbox": [x1, y1, x2, y2]},
          {"class": "car", "confidence": 0.81, "bbox": [x1, y1, x2, y2]}
        ]
        ---
        image2.jpg
        []
        ---
    """
    output_path = Path(output_txt_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        for result in results:
            img_path = getattr(result, 'path', 'unknown_image.jpg')
            img_name = Path(img_path).name

            detections: list[dict] = []

            if hasattr(result, 'boxes') and result.boxes is not None:
                boxes = result.boxes

                cls_ids = boxes.cls.cpu().tolist() if hasattr(boxes, "cls") else []
                confs = boxes.conf.cpu().tolist() if hasattr(boxes, "conf") else []
                xyxy = boxes.xyxy.cpu().tolist() if hasattr(boxes, "xyxy") else []

                for idx, cls_id in enumerate(cls_ids):
                    record: dict = {
                        "class": model_names.get(int(cls_id), str(int(cls_id))),
                    }

                    if idx < len(confs):
                        record["confidence"] = float(confs[idx])

                    if idx < len(xyxy):
                        # x1, y1, x2, y2
                        record["bbox"] = [float(v) for v in xyxy[idx]]

                    detections.append(record)

            f.write(f"{img_name}\n")
            f.write(json.dumps(detections, ensure_ascii=False))
            f.write("\n---\n")

    print(f"📄 Детализированный отчёт (v2) сохранён: {output_path}")