# main.py
import sys
import signal
import logging
from pathlib import Path
import subprocess
# Импортируем наши модули
from config import validate_paths, GRPCConfig
from services import LlamaServer

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("orchestrator")


def cleanup(signum, frame):
    """Обработчик сигналов остановки"""
    logger.info("\n🛑 Получен сигнал остановки, завершаем работу...")
    if 'llama_server' in globals():
        llama_server.stop()
    sys.exit(0)


def main():
    """Точка входа в приложение"""
    
    # Заголовок
    print("=" * 60)
    print("🤖 AI PIPELINE ORCHESTRATOR")
    print("=" * 60)
    
    # 1. Валидация путей
    paths_ok = validate_paths()
    if not all(paths_ok.values()):
        logger.error("❌ Проверка путей не пройдена:")
        for name, ok in paths_ok.items():
            status = "✅" if ok else "❌"
            logger.error(f"   {status} {name}")
        return 1
    
    # 2. Запуск LLM сервера
    global llama_server
    llama_server = LlamaServer()
    
    if not llama_server.start(timeout=120):
        logger.error("❌ Не удалось запустить LLM сервер")
        return 1
    
    # 3. Запуск gRPC сервера (блокирующий)
    grpc_module = GRPCConfig.MODULE
    logger.info(f"📡 Запуск gRPC сервера: {grpc_module}")
    
    try:
        result = subprocess.run(  # noqa: F821 (subprocess импортируется в llama_manager)
            [sys.executable, "-m", grpc_module],
            capture_output=False,
            text=True,
            check=False
        )
        if result.returncode != 0:
            logger.warning(f"⚠️ gRPC сервер завершился с кодом: {result.returncode}")
            return result.returncode
            
    except KeyboardInterrupt:
        logger.info("\n🛑 Принудительная остановка пользователем")
        return 130
    except Exception as e:
        logger.error(f"💥 Ошибка gRPC сервера: {e}")
        return 1
    finally:
        # Гарантированная остановка LLM
        llama_server.stop()
    
    logger.info("✅ Приложение завершено штатно")
    return 0


if __name__ == "__main__":
    # Регистрация обработчиков сигналов
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    # Запуск
    sys.exit(main())