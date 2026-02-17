from app.core.coco_classes import COCO_CLASS_NAMES_TO_IDS
def class_names_to_ids(target_classes):
    """Преобразует список имён классов в ID из COCO."""
    if not target_classes:
        return None
    class_ids = []
    for cls_name in target_classes:
        if cls_name in COCO_CLASS_NAMES_TO_IDS:
            class_ids.append(COCO_CLASS_NAMES_TO_IDS[cls_name])
        # Игнорируем неизвестные классы (можно изменить на ошибку)
    return class_ids if class_ids else None