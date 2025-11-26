#!/usr/bin/env python3
"""
Файл для управления SQLite базой данных и запуска FastAPI приложения
Принимает параметр --new для пересоздания базы данных
"""

# Настройка кодировки для Windows консоли
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import argparse
import os
import subprocess
from pathlib import Path


def remove_database_file():
    """Удаление файла базы данных SQLite"""
    db_file = Path("SeatReservetion_back/seat_reservation.db")
    if db_file.exists():
        db_file.unlink()
        print(f"🗑️  Файл базы данных {db_file} удален")
        return True
    else:
        print(f"ℹ️  Файл базы данных {db_file} не найден (возможно, уже удален)")
        return False

def recreate_database():
    """Пересоздание базы данных с таблицами и стандартными данными"""
    try:
        # Переходим в директорию SeatReservetion_back и запускаем Python скрипт для создания БД
        script_path = "start.py"
        if os.path.exists(f"SeatReservetion_back/{script_path}"):
            print("🚀 Пересоздание базы данных...")
            print("📊 Создание таблиц и инициализация данных...")
            
            # Запускаем существующий скрипт с параметром --new
            # Не используем capture_output=True чтобы избежать блокировки
            result = subprocess.run([
                sys.executable, script_path, "--new"
            ], cwd="SeatReservetion_back", check=False)
            
            if result.returncode == 0:
                print("✅ База данных успешно пересоздана!")
                return True
            else:
                print(f"❌ Ошибка при пересоздании базы данных (код выхода: {result.returncode})")
                return False
        else:
            print("❌ Файл start.py не найден!")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при пересоздании базы данных: {e}")
        return False

def check_database_exists():
    """Проверка существования файла базы данных"""
    db_file = Path("SeatReservetion_back/seat_reservation.db")
    return db_file.exists()

def start_fastapi_application():
    """Запуск FastAPI приложения"""
    try:
        print("🚀 Запуск FastAPI приложения...")
        print("🌐 Порт: 8000")
        print("🔗 Документация API: http://localhost:8000/docs")
        print("=" * 60)
        
        # Запускаем FastAPI приложение используя uvicorn
        # Используем объединение команд через | для Windows консоли
        cmd = f'cd SeatReservetion_back && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload'
        
        # Для Windows PowerShell используем invoke-expression или просто выполним команду
        subprocess.run(cmd, shell=True, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при запуске приложения: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Приложение остановлено пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Ошибка при запуске приложения: {e}")
        sys.exit(1)

def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description="Файл для управления SQLite базой данных и запуска FastAPI приложения",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python run_server.py                    # Обычный запуск (проверяет наличие БД)
  python run_server.py --new              # Запуск с пересозданием БД
  python run_server.py -n                 # Короткая форма параметра --new
        """
    )
    
    parser.add_argument(
        "--new", 
        "-n",
        action="store_true",
        help="Пересоздать базу данных (удалить существующий файл БД и создать заново)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Seat Reservation Manager v1.0.0"
    )
    
    args = parser.parse_args()
    
    print("🏢 Система бронирования рабочих мест - Менеджер запуска")
    print("=" * 60)
    
    # Проверяем существование директории SeatReservetion_back
    if not os.path.exists("SeatReservetion_back"):
        print("❌ Директория SeatReservetion_back не найдена!")
        sys.exit(1)
    
    # Обрабатываем параметр --new
    if args.new:
        print("🔄 Режим: Пересоздание базы данных")
        
        # Удаляем существующий файл БД
        db_was_deleted = remove_database_file()
        
        # Пересоздаем базу данных с таблицами и данными
        if recreate_database():
            print("-" * 60)
        else:
            print("❌ Не удалось пересоздать базу данных!")
            sys.exit(1)
    
    else:
        print("🔄 Режим: Обычный запуск")
        
        # Проверяем существование БД
        if check_database_exists():
            print("✅ База данных найдена")
        else:
            print("⚠️  База данных не найдена, создается новая...")
            if recreate_database():
                print("-" * 60)
            else:
                print("❌ Не удалось создать базу данных!")
                sys.exit(1)
    
    # Запускаем приложение
    start_fastapi_application()

if __name__ == "__main__":
    main()