#!/usr/bin/env python3
"""
Скрипт для создания тестового администратора
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models import Account, Status
from app.core.security import get_password_hash

def create_test_user():
    """Создание тестового администратора"""
    db = SessionLocal()
    try:
        # Проверяем, существует ли уже тестовый пользователь
        existing_user = db.query(Account).filter(Account.login == "admin@example.com").first()
        if existing_user:
            print("⚠️  Тестовый пользователь уже существует!")
            return
        
        # Находим или создаем статус "active"
        active_status = db.query(Status).filter(Status.name == "active").first()
        if not active_status:
            active_status = Status(name="active", description="Активный")
            db.add(active_status)
            db.commit()
            db.refresh(active_status)
        
        # Хешируем пароль с bcrypt
        hashed_password = get_password_hash("admin123")
        
        # Создаем тестовый аккаунт с персональными данными
        test_account = Account(
            login="admin",
            password_hash=hashed_password,
            is_admin=True,
            status_id=active_status.id,
            # Персональные данные из объединенной модели
            first_name="Администратор",
            last_name="Системы",
            email="admin@example.com"
        )
        db.add(test_account)
        db.commit()
        
        print("✅ Тестовый администратор создан успешно!")
        print("📧 Email: admin@example.com")
        print("🔑 Пароль: admin123")
        print("👤 Роль: Администратор")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при создании тестового пользователя: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()