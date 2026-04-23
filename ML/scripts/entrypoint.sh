#!/bin/bash
# scripts/entrypoint.sh
set -e

echo "AI Pipeline Container Starting..."

# === Gemma 4 Vision GGUF (основная модель) ===
: "${LLAMA_MODEL_URL:=https://huggingface.co/bartowski/google_gemma-4-E4B-it-GGUF/resolve/main/google_gemma-4-E4B-it-Q4_K_M.gguf}"
: "${LLAMA_MMPROJ_URL:=https://huggingface.co/bartowski/google_gemma-4-E4B-it-GGUF/resolve/main/mmproj-google_gemma-4-E4B-it-f16.gguf}"

if [ ! -f "$LLAMA_MODEL_PATH" ]; then
    echo "LLM model not found: $LLAMA_MODEL_PATH"
    echo "Downloading google_gemma-4-E4B-it-Q4_K_M.gguf ..."
    mkdir -p "$(dirname "$LLAMA_MODEL_PATH")"
    wget -q --show-progress "$LLAMA_MODEL_URL" -O "$LLAMA_MODEL_PATH"
    echo "LLM model downloaded"
fi

# === Gemma mmproj (multimodal projector) ===
if [ ! -f "$LLAMA_MMPROJ_PATH" ]; then
    echo "mmproj not found: $LLAMA_MMPROJ_PATH"
    echo "Downloading mmproj-google_gemma-4-E4B-it-f16.gguf ..."
    mkdir -p "$(dirname "$LLAMA_MMPROJ_PATH")"
    wget -q --show-progress "$LLAMA_MMPROJ_URL" -O "$LLAMA_MMPROJ_PATH"
    echo "mmproj downloaded"
fi

# === SAM3 (vision) ===
SAM3_DIR="${SAM3_CHECKPOINT_PATH:-/app/models/sam3}"
if [ ! -f "$SAM3_DIR/model.safetensors" ]; then
    echo "SAM3 not found at: $SAM3_DIR"
    echo "Downloading SAM3 from ModelScope ..."
    mkdir -p "$SAM3_DIR"
    python3 - <<PYEOF
import os, sys
try:
    from modelscope import snapshot_download
    sam3_dir = os.environ.get("SAM3_CHECKPOINT_PATH", "/app/models/sam3")
    snapshot_download("facebook/sam3", local_dir=sam3_dir)
    print(f"SAM3 downloaded to {sam3_dir}")
except Exception as e:
    print(f"ERROR: Could not download SAM3: {e}", file=sys.stderr)
    sys.exit(1)
PYEOF
    echo "SAM3 downloaded"
fi

# === llama-server ===
if [ ! -x "$LLAMA_SERVER_PATH" ]; then
    echo "ERROR: llama-server not found or not executable: $LLAMA_SERVER_PATH"
    exit 1
fi

echo "Container ready"
exec "$@"
