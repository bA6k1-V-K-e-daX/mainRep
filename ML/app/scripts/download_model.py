import requests
from pathlib import Path
from tqdm import tqdm

def download_model():
    # Путь к папке models
    PROJECT_ROOT = Path(__file__).parent.parent  # Projects/ImageClassifer
    MODEL_DIR = PROJECT_ROOT / "models"
    MODEL_DIR.mkdir(exist_ok=True, parents=True)
    
    # Путь куда сохранить модель
    model_path = MODEL_DIR / "yolov8n.pt"
    
    # Если модель уже есть - пропускаем
    if model_path.exists():
        print(f"✅ Модель уже существует: {model_path}")
        return str(model_path)
    
    # URL для скачивания YOLOv8n
    url = "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt"
    
    print(f"Скачиваю модель в: {model_path}")
    
    # Скачиваем с прогресс-баром
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    # Получаем размер файла
    total_size = int(response.headers.get('content-length', 0))
    
    # Сохраняем файл
    with open(model_path, 'wb') as f, tqdm(
        desc=model_path.name,
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            bar.update(len(chunk))
    
    print(f"✅ Модель скачана: {model_path}")
    return str(model_path)

# Использование
if __name__ == "__main__":
    model_file = download_model()
    
    # Теперь загружаем модель через YOLO
    from ultralytics import YOLO
    model = YOLO(model_file)
    print("Модель готова к использованию!")