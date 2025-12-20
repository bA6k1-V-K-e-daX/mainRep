from fastapi import APIRouter, UploadFile, File, Depends, Request
import cv2
import numpy as np
import os
from pathlib import Path

router = APIRouter(prefix="/predict")

# Создаем папку если нет
Path("results").mkdir(exist_ok=True)

# Функция-зависимость для получения модели из app.state
def get_model(request: Request):
    """Достает модель из app.state"""
    return request.app.state.model

@router.post("/predict_image_class/")
async def predict_image_class(
    file: UploadFile = File(...),
    model = Depends(get_model)  # инжектим модель через зависимость
):
    """
    Принимает изображение, обрабатывает моделью из app.state
    """
    if not file.content_type.startswith("image/"):
        return {"error": "Только изображения"}
    
    # Читаем изображение
    image_bytes = await file.read()
    image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), 1)
    
    if image is None:
        return {"error": "Не удалось загрузить изображение"}
    
    # Используем модель из app.state
    results = model(image)
    annotated = results[0].plot()
    
    # Сохраняем результат
    cv2.imwrite(f"results/{file.filename}", annotated)
    
    return {
        "результат": f"results/{file.filename}",
        "статус": "готово",
        "объектов_найдено": len(results[0].boxes) if results[0].boxes is not None else 0
    }