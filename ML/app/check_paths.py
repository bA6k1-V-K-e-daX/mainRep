# ML/check_paths.py
import os
from pathlib import Path


def main():
    server = os.getenv("LLAMA_SERVER_PATH", "/app/llama-bin/llama-server")
    model = os.getenv("LLAMA_MODEL_PATH", "/app/models/google_gemma-4-E4B-it-Q4_K_M.gguf")
    mmproj = os.getenv("LLAMA_MMPROJ_PATH", "/app/models/mmproj-google_gemma-4-E4B-it-f16.gguf")

    print(f"[CHECK] Server: {server}")
    print(f"[CHECK] Server exists: {Path(server).exists()}")
    print(f"[CHECK] Server executable: {os.access(server, os.X_OK)}")

    print(f"[CHECK] Model: {model}")
    if Path(model).exists():
        print(f"[CHECK] Model size: {Path(model).stat().st_size / 1024**2:.1f} MB")
    else:
        print("[CHECK] Model exists: False")

    print(f"[CHECK] mmproj: {mmproj}")
    if Path(mmproj).exists():
        print(f"[CHECK] mmproj size: {Path(mmproj).stat().st_size / 1024**2:.1f} MB")
    else:
        print("[CHECK] mmproj exists: False")


if __name__ == "__main__":
    main()
