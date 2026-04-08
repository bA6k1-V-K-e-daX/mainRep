# services/llama_manager.py
import subprocess
import sys
import time
import requests
import logging
from typing import Optional
from pathlib import Path

from config import LLMConfig, IS_WINDOWS, IS_DOCKER

logger = logging.getLogger(__name__)


class LlamaServer:
    """
    Менеджер для запуска и управления llama-server процессом.
    
    Пример использования:
        server = LlamaServer()
        if server.start():
            # ... работа с LLM ...
            server.stop()
    """
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self._started = False
    
    def build_command(self) -> list[str]:
        cmd = [
            str(Path(LLMConfig.get_server_path())),
            "-m", str(Path(LLMConfig.get_model_path())),
            "-ngl", str(LLMConfig.NGL),
            "-c", str(LLMConfig.CONTEXT),
            "--host", LLMConfig.HOST,
            "--port", str(LLMConfig.PORT),
            "-t", str(LLMConfig.THREADS),
        ]
        
        # === Flash Attention: проверяем поддержку синтаксиса ===
        if LLMConfig.FLASH_ATTN:
            # Новый синтаксис (llama.cpp после 2024-09)
            cmd.extend(["--flash-attn", "on"])
        else:
            cmd.extend(["--flash-attn", "off"])
        
        # === MMAP ===
        cmd.append("--no-mmap" if LLMConfig.NO_MMAP else "--mmap")
        
        # === Cache reuse ===
        cache_val = str(LLMConfig.CACHE_REUSE).strip()
        if cache_val and cache_val not in ("0", "false", "off"):
            cmd.extend(["--cache-reuse", cache_val])
        
        return cmd
    
    def start(self, timeout: int = 120) -> bool:
        """
        Запускает llama-server и ждёт его готовности.
        
        Args:
            timeout: Максимальное время ожидания в секундах
            
        Returns:
            True если сервер запустился успешно, False иначе
        """
        if self._started:
            logger.warning("LLM сервер уже запущен")
            return True
        
        # Проверка путей
        server_path = Path(LLMConfig.get_server_path())
        model_path = Path(LLMConfig.get_model_path())
        
        if not server_path.exists():
            logger.error(f"llama-server не найден: {server_path}")
            return False
        if not model_path.exists():
            logger.error(f"Модель не найдена: {model_path}")
            return False
        
        cmd = self.build_command()
        logger.info(f"🚀 Запуск LLM сервера: {server_path}")
        logger.info(f"   Модель: {model_path}")
        logger.debug(f"   Команда: {' '.join(cmd)}")
        
        try:
            # Запускаем процесс
            if IS_WINDOWS and not IS_DOCKER:
                # На хосте Windows: отдельное окно для отладки
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
            else:
                # В Docker / Linux: вывод в основной лог
                self.process = subprocess.Popen(
                    cmd,
                    stdout=sys.stdout,
                    stderr=sys.stderr,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
            # После subprocess.Popen(...)
            time.sleep(2)  # Даём процессу 2 секунды на старт/краш

            if self.process.poll() is not None:
                # Процесс уже умер! Читаем вывод
                stdout, _ = self.process.communicate(timeout=5)
                logger.error(f"❌ llama-server упал сразу! Код: {self.process.returncode}")
                logger.error(f"📋 Вывод:\n{stdout}")
                return False
            # Ждём готовности
            if self.wait_for_health(timeout):
                self._started = True
                logger.info("✅ LLM сервер готов к работе")
                return True
            else:
                logger.error("❌ Таймаут ожидания LLM сервера")
                self.stop()
                return False
                
        except FileNotFoundError as e:
            logger.error(f"❌ Не удалось запустить llama-server: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка при запуске LLM: {e}")
            if self.process:
                self.stop()
            return False
    
    def wait_for_health(self, timeout: int = 60) -> bool:
        """Ждёт, пока сервер ответит на /health запрос"""
        logger.info(f"⏳ Ожидание LLM сервера (порт {LLMConfig.PORT})...")
        start = time.time()
        
        while time.time() - start < timeout:
            try:
                resp = requests.get(LLMConfig.get_health_url(), timeout=2)
                if resp.status_code == 200:
                    return True
            except requests.ConnectionError:
                pass  # Сервер ещё не поднялся
            except Exception as e:
                logger.debug(f"Health check error: {e}")
            time.sleep(1)
        
        return False
    
    def stop(self, timeout: int = 5) -> bool:
        """Корректно останавливает сервер"""
        if not self.process or not self._started:
            return True
        
        logger.info("🔄 Остановка LLM сервера...")
        
        try:
            self.process.terminate()
            
            # Для Windows иногда нужен kill
            if IS_WINDOWS:
                time.sleep(0.5)
                if self.process.poll() is None:
                    self.process.kill()
            
            # Ждём завершения
            exit_code = self.process.wait(timeout=timeout)
            logger.info(f"✅ LLM сервер остановлен (код: {exit_code})")
            self._started = False
            return True
            
        except subprocess.TimeoutExpired:
            logger.warning("⚠️ Таймаут остановки, принудительное завершение")
            self.process.kill()
            self._started = False
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка при остановке LLM: {e}")
            return False
    
    def is_running(self) -> bool:
        """Проверяет, запущен ли процесс"""
        if not self.process:
            return False
        return self.process.poll() is None
    
    def __enter__(self):
        """Контекстный менеджер: with LlamaServer() as server:"""
        if not self.start():
            raise RuntimeError("Failed to start LLM server")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Автоматическая остановка при выходе из контекста"""
        self.stop()
        return False  # Не подавляем исключения