#!/bin/bash
# scripts/entrypoint.sh
set -e

echo "🚀 AI Pipeline Container Starting..."

# Проверка наличия модели
if [ ! -f "$LLAMA_MODEL_PATH" ]; then
    echo "⚠️  Модель не найдена: $LLAMA_MODEL_PATH"
    echo "💡 Скачиваю модель (может занять время)..."
    
    mkdir -p "$(dirname "$LLAMA_MODEL_PATH")"
    wget -q --show-progress \
        https://huggingface.co/bartowski/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf \
        -O "$LLAMA_MODEL_PATH"
    
    echo "✅ Модель скачана"
fi

# Проверка llama-server
if [ ! -x "$LLAMA_SERVER_PATH" ]; then
    echo "❌ llama-server не найден или не исполняемый: $LLAMA_SERVER_PATH"
    exit 1
fi

echo "✅ Контейнер готов к запуску"
exec "$@"