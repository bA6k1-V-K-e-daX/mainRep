#!/bin/bash
# scripts/entrypoint.sh
set -e

echo "AI Pipeline Container Starting..."

# --- Скачивание моделей (только если volume пустой при первом запуске) ---
if [ ! -f "$LLAMA_MODEL_PATH" ]; then
    echo "Downloading Gemma GGUF model (first run)..."
    wget --progress=dot:giga \
        -O "$LLAMA_MODEL_PATH" \
        https://huggingface.co/bartowski/google_gemma-4-E4B-it-GGUF/resolve/main/google_gemma-4-E4B-it-Q4_K_M.gguf
fi

if [ ! -f "$LLAMA_MMPROJ_PATH" ]; then
    echo "Downloading mmproj (first run)..."
    wget --progress=dot:giga \
        -O "$LLAMA_MMPROJ_PATH" \
        https://huggingface.co/bartowski/google_gemma-4-E4B-it-GGUF/resolve/main/mmproj-google_gemma-4-E4B-it-f16.gguf
fi

SAM3_DIR="${SAM3_CHECKPOINT_PATH:-/app/models/sam3}"
if [ ! -f "$SAM3_DIR/model.safetensors" ]; then
    echo "Downloading SAM3 (first run)..."
    python3 -c "from modelscope import snapshot_download; snapshot_download('facebook/sam3', local_dir='$SAM3_DIR')"
fi

# --- Валидация ---
if [ ! -f "$LLAMA_MODEL_PATH" ]; then
    echo "ERROR: LLM model missing in volume: $LLAMA_MODEL_PATH"
    exit 1
fi

if [ ! -f "$LLAMA_MMPROJ_PATH" ]; then
    echo "ERROR: mmproj missing in volume: $LLAMA_MMPROJ_PATH"
    exit 1
fi

if [ ! -f "$SAM3_DIR/model.safetensors" ]; then
    echo "ERROR: SAM3 weights missing in volume: $SAM3_DIR"
    exit 1
fi

if [ ! -x "$LLAMA_SERVER_PATH" ]; then
    echo "ERROR: llama-server not found or not executable: $LLAMA_SERVER_PATH"
    exit 1
fi

echo "Container ready"
exec "$@"
