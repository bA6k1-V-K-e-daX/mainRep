# CLAUDE.md

Этот файл содержит руководство для Claude Code (claude.ai/code) при работе с этим репозиторием.

## Что делает этот проект

Пайплайн для детекции и сегментации объектов на изображениях. Принимает запросы на естественном языке (включая русский), анализирует каждое изображение через локальную Gemma 4 Vision (GGUF через llama.cpp), применяет confidence и relevance-фильтры, затем запускает SAM3 для детекции + сегментации. Предоставляет gRPC-сервис.

## Команды

### Локальная разработка
```bash
# Установка
python -m venv venv && source venv/Scripts/activate  # Windows: venv\Scripts\activate.bat
pip install -r requirements.txt

# Запуск сервиса (запускает llama-server Gemma на :8000 + gRPC на :50051)
python main.py

# Тестирование gRPC-эндпоинта
python test_client.py

# Проверка путей до llama-server, основной модели и mmproj
python -m app.check_paths
```

### Docker
```bash
docker build --no-cache -t ml_service .
docker run -p 8000:8000 -p 50051:50051 --name ml_service_container ml_service

# Извлечь папку с результатами из контейнера (PowerShell)
.\scripts\extract_volume.ps1
```

При первом запуске `entrypoint.sh` скачает 2 файла Gemma (Q4_K_M + mmproj) и SAM3.

### Перегенерация gRPC-стабов (при изменении detector.proto)
```bash
python -m grpc_tools.protoc -I app/grps/protos \
    --python_out=app/grps/protos \
    --grpc_python_out=app/grps/protos \
    app/grps/protos/detector.proto
```

## Архитектура

### Запуск сервиса (main.py)
1. Проверяет пути до бинарника llama-server, GGUF-модели Gemma и mmproj
2. Запускает `LlamaServer` как подпроцесс (services/llama_manager.py) — опрашивает `/health` на порту 8000
3. Запускает gRPC-сервер как подпроцесс (`app.grps.server`)

Команда запуска llama-server:
```
llama-server -m <model>.gguf --mmproj <mmproj>.gguf -c 8192 \
  --host 127.0.0.1 --port 8000 -ngl 20 \
  --batch-size 256 --ubatch-size 256 \
  --no-kv-offload --parallel 1 --flash-attn on
```

### Поток обработки запроса
```
gRPC DetectionRequest (query_id, dir_path, prompt)
  → DetectorService (app/grps/server.py)
  → ImageDetectionUseCase.execute() (app/scenaries/detect_image.py)
      │
      │ ─── Gemma 4 Vision работает ───
      │ для каждой картинки в source/:
      │   1. POST /v1/chat/completions с картинкой → [{"label","confidence"}]
      │   2. Confidence-фильтр (>=0.6)
      │   3. Relevance-фильтр: текстовый вызов Gemma без картинки
      │ → {image_name: [final_labels]}
      │
      │ ─── Остановка llama-server (освобождение VRAM) ───
      │
      │ ─── SAM3 subprocess ───
      │ detection_pipline.py --labels-json → per-image детекция + сегментация
      │
      │ ─── Перезапуск llama-server ───
      │
  → Чтение report.txt → возврат DetectionResponse
```

### Ключевые файлы
| Файл | Роль |
|------|------|
| `main.py` | Точка входа, оркестратор |
| `config/settings.py` | LLMConfig (Gemma), VisionConfig (SAM3), GRPCConfig |
| `services/llama_manager.py` | Управление процессом llama-server (Gemma команда запуска) |
| `app/grps/server.py` | Реализация gRPC DetectorService |
| `app/base_pipline/gemma_client.py` | Gemma Vision + relevance filter (портировано из test_gemma.py) |
| `app/scenaries/detect_image.py` | Per-image Gemma анализ → SAM3 subprocess |
| `app/base_pipline/detection_pipline.py` | SAM3 subprocess (принимает `--labels-json`) |
| `app/base_pipline/sam_pipline.py` | Утилиты SAM3 |
| `app/grps/protos/detector.proto` | Схема gRPC |
| `tests/test_gemma.py` | Экспериментальный скрипт — референс для промптов и фильтров |

### Конфигурация
Настройки берутся из переменных окружения (файл `.env`). Ключевые:

- `LLAMA_SERVER_PATH` — путь к бинарнику llama-server
- `LLAMA_MODEL_PATH` — путь к `google_gemma-4-E4B-it-Q4_K_M.gguf`
- `LLAMA_MMPROJ_PATH` — путь к `mmproj-google_gemma-4-E4B-it-f16.gguf` (обязательно!)
- `LLAMA_PORT=8000` / `GRPC_PORT=50051`
- `GEMMA_MIN_CONFIDENCE=0.6` — порог уверенности Gemma до SAM3
- `GEMMA_USE_RELEVANCE_FILTER=true` — текстовый пост-фильтр релевантности
- `RUNNING_IN_DOCKER=true` — переключает пути по умолчанию на Docker
- `VISION_DEVICE=cuda` — устройство для SAM3

Скопируй `.env.example` в `.env` и пропиши пути перед локальным запуском.

### Структура данных
Входные изображения: `volume/<query_id>/source/`. Результаты: `volume/<query_id>/result/`:
- `gemma_analysis.json` — сырой вывод Gemma с confidence и фильтрами
- `labels_per_image.json` — финальные метки per-image (передаётся в SAM3)
- `report.txt` — сводка для gRPC-ответа
- `<image>_<ext>/` — папка на каждое изображение: маски, overlay, боксы, JSON

### gRPC-контракт
- Сервис: `Detector` → RPC `ImageDetection`
- Запрос: `query_id` (int64), `dir_path` (string), `prompt` (string)
- Ответ: `query_id`, `result_path`, `success`, `instance_info[]`, `error_message`, `total_objects`
