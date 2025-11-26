#!/usr/bin/env python3
"""
Скрипт для запуска backend системы бронирования рабочих мест
Поддерживает параметр --new для пересоздания базы данных
"""

# Настройка кодировки для Windows консоли
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import argparse
import os
import sys
import uvicorn
from pathlib import Path

# Добавляем текущую директорию в sys.path для импорта модулей приложения
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def remove_database_file():
    """Удаление файла базы данных SQLite"""
    db_file = Path("seat_reservation.db")
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
        # Импортируем функции для работы с БД
        from app.core.database import create_and_initialize_tables
        
        print("🚀 Пересоздание базы данных...")
        print("📊 Создание таблиц и инициализация данных...")
        
        # Создаем таблицы и заполняем стандартными данными
        create_and_initialize_tables()
        
        print("✅ База данных успешно пересоздана!")
        
    except Exception as e:
        print(f"❌ Ошибка при пересоздании базы данных: {e}")
        sys.exit(1)

def check_database_exists():
    """Проверка существования файла базы данных"""
    db_file = Path("seat_reservation.db")
    return db_file.exists()

def start_application():
    """Запуск FastAPI приложения"""
    try:
        # Импортируем настройки для проверки конфигурации
        from app.core.config import settings
        
        print(f"🚀 Запуск {settings.app_name} v{settings.app_version}")
        print(f"🌐 Порт: 8000")
        print(f"🔗 Документация API: http://localhost:8000/docs")
        print("=" * 60)
        
        # Запускаем uvicorn сервер
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=settings.debug,
            log_level="info"
        )
        
    except Exception as e:
        print(f"❌ Ошибка при запуске приложения: {e}")
        sys.exit(1)

def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description="Скрипт запуска backend системы бронирования рабочих мест",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python start.py                    # Обычный запуск (проверяет наличие БД)
  python start.py --new              # Запуск с пересозданием БД
  python start.py -n                 # Короткая форма параметра --new
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
        version="Seat Reservation Backend v1.0.0"
    )
    
    args = parser.parse_args()
    
    print("🏢 Система бронирования рабочих мест - Backend")
    print("=" * 60)
    
    # Проверяем наличие переменных окружения
    if not os.path.exists(".env"):
        print("⚠️  ВНИМАНИЕ: Файл .env не найден!")
        print("📝 Скопируйте .env.example в .env или создайте файл .env с настройками")
        print("💡 Будут использованы настройки по умолчанию")
        print("-" * 60)
    
    # Обрабатываем параметр --new
    if args.new:
        print("🔄 Режим: Пересоздание базы данных")
        
        # Удаляем существующий файл БД
        db_was_deleted = remove_database_file()
        
        # Пересоздаем базу данных с таблицами и данными
        recreate_database()
        
        print("-" * 60)
    
    else:
        print("🔄 Режим: Обычный запуск")
        
        # Проверяем существование БД
        if check_database_exists():
            print("✅ База данных найдена")
        else:
            print("⚠️  База данных не найдена, создается новая...")
            recreate_database()
            print("-" * 60)
    
    # Запускаем приложение
    start_application()

if __name__ == "__main__":
    main()