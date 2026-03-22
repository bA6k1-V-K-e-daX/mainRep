# main.py
import subprocess
import sys
import os
import time
import requests
import platform
from pathlib import Path
import signal

# --- КОНФИГУРАЦИЯ ЧЕРЕЗ ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ ---
IS_WINDOWS = platform.system() == "Windows"
IS_DOCKER = os.getenv("RUNNING_IN_DOCKER", "false").lower() == "true"

# Пути к llama-server
DEFAULT_LLAMA_SERVER = (
    r"C:\llama.cpp\llama-server.exe" if IS_WINDOWS 
    else "/host-llama/llama-server"
)
LLAMA_SERVER_PATH = os.getenv("LLAMA_SERVER_PATH", DEFAULT_LLAMA_SERVER)

# Пути к модели
DEFAULT_MODEL_PATH = (
    r"C:\llama.cpp\models\Qwen2.5-1.5B-Instruct-Q4_K_M.gguf" if IS_WINDOWS
    else "/host-llama/models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf"
)
LLAMA_MODEL_PATH = os.getenv("LLAMA_MODEL_PATH", DEFAULT_MODEL_PATH)

# Порт и модуль
LLAMA_PORT = int(os.getenv("LLAMA_PORT", "8080"))
GRPC_SERVER_MODULE = os.getenv("GRPC_SERVER_MODULE", "app.grps.server")

# Оптимизации для PyTorch
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:512'
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

llama_process = None

def cleanup(signum, frame):
    """Корректная остановка всех процессов"""
    print("\n🛑 Остановка сервисов...")
    if llama_process:
        try:
            llama_process.terminate()
            if IS_WINDOWS:
                llama_process.kill()
            llama_process.wait(timeout=5)
            print("✅ LLM сервер остановлен")
        except:
            pass
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

def wait_for_llm(timeout=60):
    """Ждет, пока llama-server не станет доступен"""
    print(f"⏳ Ожидание LLM сервера (порт {LLAMA_PORT})...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = requests.get(f"http://127.0.0.1:{LLAMA_PORT}/health", timeout=2)
            if resp.status_code == 200:
                print("✅ LLM сервер готов!")
                return True
        except:
            time.sleep(1)
    return False

def start_llama_server():
    """Запускает llama-server с оптимизациями"""
    cmd = [
        LLAMA_SERVER_PATH,
        "-m", LLAMA_MODEL_PATH,
        "-ngl", os.getenv("LLAMA_NGL", "99"),
        "-c", os.getenv("LLAMA_CONTEXT", "2048"),
        "--host", "127.0.0.1",
        "--port", str(LLAMA_PORT),
        "-t", os.getenv("LLAMA_THREADS", "4"),
        "--flash-attn", os.getenv("LLAMA_FLASH_ATTN", "on"),
        "--cache-reuse", os.getenv("LLAMA_CACHE_REUSE", "256"),
        "--no-mmap" if os.getenv("LLAMA_NO_MMAP", "true").lower() == "true" else "--mmap"
    ]
    
    print(f"🚀 Запуск LLM сервера: {LLAMA_SERVER_PATH}")
    print(f"   Модель: {LLAMA_MODEL_PATH}")
    
    if IS_WINDOWS and not IS_DOCKER:
        process = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        process = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)
    return process

def main():
    print("="*60)
    print("🤖 AI PIPELINE ORCHESTRATOR")
    print(f"   Platform: {platform.system()}")
    print(f"   Docker: {IS_DOCKER}")
    print("="*60)

    # Проверка путей
    if not Path(LLAMA_SERVER_PATH).exists():
        print(f"❌ llama-server не найден: {LLAMA_SERVER_PATH}")
        return
    if not Path(LLAMA_MODEL_PATH).exists():
        print(f"❌ Модель не найдена: {LLAMA_MODEL_PATH}")
        return
    grpc_module_path = Path(*GRPC_SERVER_MODULE.split('.'))
    if not (grpc_module_path.with_suffix('.py').exists() or grpc_module_path.exists()):
        print(f"❌ gRPC сервер не найден: {GRPC_SERVER_MODULE}")
        return

    # Запуск LLM
    global llama_process
    llama_process = start_llama_server()
    
    if not wait_for_llm(timeout=120):
        print("❌ LLM сервер не запустился вовремя!")
        if llama_process:
            llama_process.terminate()
        return

    # Запуск gRPC сервера
    print(f"\n📡 Запуск gRPC сервера: {GRPC_SERVER_MODULE}")
    try:
        result = subprocess.run(
            [sys.executable, "-m", GRPC_SERVER_MODULE],
            capture_output=False,
            text=True,
            check=False
        )
        if result.returncode != 0:
            print(f"\n⚠️ gRPC сервер завершился с кодом: {result.returncode}")
    except KeyboardInterrupt:
        print("\n🛑 Принудительная остановка")
    finally:
        if llama_process:
            print("🔄 Остановка LLM сервера...")
            llama_process.terminate()
            try:
                llama_process.wait(timeout=5)
            except:
                llama_process.kill()

if __name__ == "__main__":
    main()