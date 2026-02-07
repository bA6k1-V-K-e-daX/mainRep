# main.py
import subprocess
import sys
import os

def main():
    print("🚀 Запускаю gRPC сервер...")
    
    if not os.path.exists("app/grps/server.py"):
        print("❌ Файл server.py не найден")
        return

    try:
        # Запускаем как модуль И захватываем вывод
        result = subprocess.run(
            [sys.executable, "-m", "app.grps.server"],
            capture_output=False,  # Выводим всё в консоль напрямую
            text=True,
            check=False  # Не выбрасываем исключение автоматически
        )
        
        if result.returncode != 0:
            print(f"\n⚠️ Сервер завершился с кодом: {result.returncode}")
        else:
            print("\n✅ Сервер остановлен штатно")
            
    except KeyboardInterrupt:
        print("\n🛑 Принудительная остановка")
    except Exception as e:
        print(f"💥 Аварийная ошибка: {e}")

if __name__ == "__main__":
    main()