# CLAUDE.md

Этот файл содержит руководство для Claude Code (claude.ai/code) при работе с этим репозиторием.

## Что делает этот проект

Пайплайн для детекции и сегментации объектов на изображениях. Принимает запросы на естественном языке (включая русский), парсит их через локальную LLM (Qwen2.5-1.5B через llama.cpp), затем запускает Grounding DINO для детекции объектов и SAM для сегментации. Предоставляет gRPC-сервис.

## Команды

### Локальная разработка
```bash
# Установка
python -m venv venv && source venv/Scripts/activate  # Windows: venv\Scripts\activate.bat
pip install -r requirements.txt

# Запуск сервиса (запускает LLM-сервер на :8081 + gRPC-сервер на :50051)
python main.py

# Тестирование gRPC-эндпоинта
python test_client.py

# Проверка путей до llama-server и модели
python -m app.check_paths
```

### Docker
```bash
docker build --no-cache -t ml_service .
docker run -p 8081:8081 -p 50051:50051 --name ml_service_container ml_service

# Извлечь папку с результатами из контейнера (PowerShell)
.\scripts\extract_volume.ps1
```

### Перегенерация gRPC-стабов (при изменении detector.proto)
```bash
python -m grpc_tools.protoc -I app/grps/protos \
    --python_out=app/grps/protos \
    --grpc_python_out=app/grps/protos \
    app/grps/protos/detector.proto
```

## Архитектура

### Запуск сервиса (main.py)
1. Проверяет пути до бинарника llama-server и GGUF-модели
2. Запускает `LlamaServer` как подпроцесс (services/llama_manager.py) — опрашивает `/health` на порту 8081
3. Запускает gRPC-сервер как подпроцесс (`app.grps.server`)

### Поток обработки запроса
```
gRPC DetectionRequest
  → DetectorService (app/grps/server.py)
  → ImageDetectionUseCase.execute() (app/scenaries/detect_image.py)
  → подпроцесс detection_pipline.py (app/base_pipline/detection_pipline.py)
      1. POST к Qwen2.5 (порт 8081) → извлечение названий классов из запроса
      2. Grounding DINO → ограничивающие рамки для каждого класса
      3. SAM → маски сегментации для каждой рамки
      4. Сохранение результатов в volume/<query_id>/result/
  → Чтение report.txt → возврат DetectionResponse
```

### Ключевые файлы
| Файл | Роль |
|------|------|
| `main.py` | Точка входа, оркестратор |
| `config/settings.py` | Вся конфигурация (LLMConfig, VisionConfig, GRPCConfig) |
| `services/llama_manager.py` | Управление процессом llama-server |
| `app/grps/server.py` | Реализация gRPC DetectorService |
| `app/scenaries/detect_image.py` | Обработчик сценария, запускает подпроцесс пайплайна |
| `app/base_pipline/detection_pipline.py` | Полный ML-пайплайн (LLM → DINO → SAM) |
| `app/base_pipline/sam_pipline.py` | Утилиты сегментации SAM |
| `app/grps/protos/detector.proto` | Схема gRPC-сервиса и сообщений |

### Конфигурация
Настройки берутся из переменных окружения (файл `.env`). Ключевые переменные:

- `LLAMA_SERVER_PATH` / `LLAMA_MODEL_PATH` — обязательны при запуске не в Docker
- `RUNNING_IN_DOCKER=true` — переключает пути по умолчанию на Docker-пути
- `VISION_DEVICE=cuda` — выбор CUDA-устройства
- `DINO_BOX_THRESHOLD=0.25` / `DINO_TEXT_THRESHOLD=0.20` — пороги уверенности детекции
- `GRPC_PORT=50051` / `LLAMA_PORT=8081`

Скопируй `.env.example` в `.env` и пропиши пути перед локальным запуском.

### Структура данных
Входные изображения помещаются в `volume/<query_id>/source/`. Результаты записываются в `volume/<query_id>/result/`:
- `report.txt` — сводка: количество объектов и ограничивающие рамки
- `mask_*.png` — цветные маски сегментации
- `detections_*.json` — детали детекции для каждого изображения

### gRPC-контракт
- Сервис: `Detector` → RPC `ImageDetection`
- Запрос: `query_id` (int64), `dir_path` (string), `prompt` (string)
- Ответ: `query_id`, `result_path`, `success`, `instance_info[]`, `error_message`, `total_objects`
