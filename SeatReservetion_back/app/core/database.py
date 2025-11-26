"""
Настройка подключения к базе данных
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Импорт базового класса Base
from app.core.base import Base
from .config import settings

# Получаем URL базы данных из настроек
DATABASE_URL = settings.database_url

# Создаем движок SQLAlchemy
# Проверяем тип базы данных и настраиваем движок соответственно
if DATABASE_URL.startswith("sqlite"):
    # Для SQLite
    engine = create_engine(
        DATABASE_URL,
        echo=False,  # Отключаем логирование для SQLite
        future=True,
        connect_args={"check_same_thread": False}
    )
else:
    # Для PostgreSQL и других БД
    engine = create_engine(
        DATABASE_URL,
        poolclass=StaticPool,
        echo=False,  # Отключаем логирование
        future=True
    )

# Создаем SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Функция для получения сессии БД
def get_db():
    """Функция зависимости для получения сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Функция для создания всех таблиц
def create_tables():
    """Создание всех таблиц в базе данных"""
    try:
        # Импортируем модели здесь, чтобы избежать циклических импортов
        from app.models import Account, Status, Room, Workspace, Booking
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Ошибка при создании таблиц: {e}")
        # Если таблицы уже существуют, игнорируем ошибку
        if "already exists" in str(e).lower():
            print("Таблицы уже существуют, продолжаем...")
        else:
            raise

# Функция для удаления всех таблиц
def drop_tables():
    """Удаление всех таблиц из базы данных"""
    # Импортируем модели здесь, чтобы избежать циклических импортов
    from app.models import Account, Status, Room, Workspace, Booking
    Base.metadata.drop_all(bind=engine)

# Функция для заполнения стандартных данных
def initialize_data():
    """Заполнение базы данных стандартными данными (статусы и др.)"""
    from app.models import Status
    from app.core.config import AppConstants
    
    db = SessionLocal()
    try:
        # Проверяем, есть ли уже статусы
        existing_statuses = db.query(Status).count()
        if existing_statuses > 0:
            print(f"ℹ️  В базе данных уже есть {existing_statuses} статусов, пропускаем инициализацию")
            return
        
        # Создаем стандартные статусы
        default_statuses = AppConstants.DEFAULT_STATUSES
        created_count = 0
        
        for status_key, status_name in default_statuses.items():
            # Проверяем, существует ли уже такой статус
            existing = db.query(Status).filter(Status.name == status_key).first()
            if not existing:
                new_status = Status(
                    name=status_key,
                    description=status_name
                )
                db.add(new_status)
                created_count += 1
        
        if created_count > 0:
            db.commit()
            print(f"✅ Создано {created_count} стандартных статусов")
        else:
            print("✅ Стандартные статусы уже существуют")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при инициализации данных: {e}")
    finally:
        db.close()

# Функция для создания и инициализации всех таблиц
def create_and_initialize_tables():
    """Создание всех таблиц и инициализация стандартных данных"""
    try:
        print("🚀 Создание таблиц базы данных...")
        create_tables()
        
        print("📊 Инициализация стандартных данных...")
        initialize_data()
        
        print("👤 Создание тестового администратора...")
        create_default_admin()
        
        print("✅ Инициализация базы данных завершена успешно")
    except Exception as e:
        print(f"❌ Ошибка при инициализации БД: {e}")
        raise

# Функция для создания админа по умолчанию
def create_default_admin():
    """Создание тестового администратора по умолчанию"""
    from app.models import Account, Status
    
    db = SessionLocal()
    try:
        # Проверяем, существует ли уже администратор и удаляем его для пересоздания с новым хешем
        existing_admin = db.query(Account).filter(Account.is_admin == True).first()
        if existing_admin:
            print(f"🔄 Удаляем существующего администратора для пересоздания (login: {existing_admin.login})")
            db.delete(existing_admin)
            db.commit()
        
        # Находим или создаем статус "active"
        active_status = db.query(Status).filter(Status.name == "active").first()
        if not active_status:
            active_status = Status(name="active", description="Активный")
            db.add(active_status)
            db.commit()
            db.refresh(active_status)
        
        # Хешируем пароль с bcrypt
        from app.core.security import get_password_hash
        hashed_password = get_password_hash("admin123")
        
        # Создаем администратора
        admin_account = Account(
            login="admin",
            password_hash=hashed_password,
            is_admin=True,
            status_id=active_status.id,
            # Персональные данные
            first_name="Администратор",
            last_name="Системы",
            email="admin@example.com"
        )
        db.add(admin_account)
        db.commit()
        db.refresh(admin_account)
        
        print("✅ Тестовый администратор пересоздан успешно!")
        print("📧 Login/Email: admin@example.com")
        print("🔑 Пароль: admin123")
        print("👤 Роль: Администратор")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при создании администратора: {e}")
        # Не прерываем выполнение, если не удалось создать админа
        print("⚠️  Продолжаем без администратора...")
    finally:
        db.close()

# Функция для очистки данных (используйте с осторожностью!)
def clear_data():
    """Очистка всех данных из таблиц (кроме структуры)"""
    from app.models import Account, Status, Room, Workspace, Booking
    
    db = SessionLocal()
    try:
        print("🗑️  Очистка данных из всех таблиц...")
        
        # Удаляем данные в порядке зависимостей (чтобы избежать ошибок внешних ключей)
        db.query(Booking).delete()
        db.query(Account).delete()
        db.query(Workspace).delete()
        db.query(Room).delete()
        db.query(Status).delete()
        
        db.commit()
        print("✅ Все данные очищены")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при очистке данных: {e}")
    finally:
        db.close()

# Функция для полной переинициализации БД
def reset_database():
    """Полная переинициализация базы данных (DROP + CREATE + INIT)"""
    try:
        print("⚠️  ВНИМАНИЕ: Это удалит ВСЕ данные!")
        print("🔄 Начинаем полную переинициализацию...")
        
        # Удаляем таблицы
        print("🗑️  Удаляем таблицы...")
        drop_tables()
        
        # Создаем заново и инициализируем
        create_and_initialize_tables()
        
        print("🎉 База данных полностью переинициализирована")
        
    except Exception as e:
        print(f"❌ Ошибка при переинициализации: {e}")
        raise
