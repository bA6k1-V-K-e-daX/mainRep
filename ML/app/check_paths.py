# ML/check_paths.py
import os
from pathlib import Path

def main():
    server = os.getenv("LLAMA_SERVER_PATH", "/app/llama-bin/llama-server")
    model = os.getenv("LLAMA_MODEL_PATH", "/app/models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf")

    print(f"[CHECK] Server: {server}")
    print(f"[CHECK] Server exists: {Path(server).exists()}")
    print(f"[CHECK] Server executable: {os.access(server, os.X_OK)}")
    print(f"[CHECK] Model: {model}")
    print(f"[CHECK] Model exists: {Path(model).exists()}")
    print(f"[CHECK] Model size: {Path(model).stat().st_size / 1024**2:.1f} MB")

if __name__ == "__main__":
    main()