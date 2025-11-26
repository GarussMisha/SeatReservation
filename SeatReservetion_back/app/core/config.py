"""
Конфигурация приложения
Настройки базы данных, аутентификации, безопасности и другие параметры системы
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Класс настроек приложения"""
    
    # === НАСТРОЙКИ БАЗЫ ДАННЫХ ===
    database_url: str = Field(
        default="sqlite:///./seat_reservation.db",
        description="URL подключения к базе данных SQLite"
    )
    
    # === НАСТРОЙКИ БЕЗОПАСНОСТИ ===
    secret_key: str = Field(
        default="your-secret-key-here-change-in-production",
        description="Секретный ключ для JWT токенов"
    )
    
    algorithm: str = Field(
        default="HS256",
        description="Алгоритм подписи JWT токенов"
    )
    
    access_token_expire_minutes: int = Field(
        default=30,
        description="Время жизни access токена в минутах"
    )
    
    # === НАСТРОЙКИ ПРИЛОЖЕНИЯ ===
    app_name: str = Field(
        default="Seat Reservation API",
        description="Название приложения"
    )
    
    app_version: str = Field(
        default="1.0.0",
        description="Версия приложения"
    )
    
    debug: bool = Field(
        default=True,
        description="Режим отладки"
    )
    
    # === НАСТРОЙКИ CORS ===
    allowed_origins: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],
        description="Разрешенные источники для CORS"
    )
    
    # === НАСТРОЙКИ ЛОГИРОВАНИЯ ===
    log_level: str = Field(
        default="INFO",
        description="Уровень логирования"
    )
    
    # === НАСТРОЙКИ ВРЕМЕНИ ===
    timezone: str = Field(
        default="UTC",
        description="Часовой пояс приложения"
    )
    
    class Config:
        """Конфигурация Pydantic Settings"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Экземпляр настроек для использования в приложении
settings = Settings()


# === ПРОВЕРКА ОБЯЗАТЕЛЬНЫХ НАСТРОЕК ===
def validate_required_settings() -> bool:
    """Проверка обязательных настроек для корректной работы"""
    required_settings = {
        "DATABASE_URL": settings.database_url,
        "SECRET_KEY": settings.secret_key,
    }
    
    # Проверяем, что секретный ключ изменен в продакшене
    if not settings.debug and settings.secret_key == "your-secret-key-here-change-in-production":
        raise ValueError(
            "SECRET_KEY не должен быть дефолтным в продакшене! "
            "Измените его в переменных окружения или .env файле"
        )
    
    # Проверяем базу данных
    if not settings.database_url:
        raise ValueError("DATABASE_URL обязателен для подключения к базе данных")
    
    return True


# === ИНИЦИАЛИЗАЦИЯ ===
# Проверяем настройки при импорте
try:
    validate_required_settings()
except ValueError as e:
    if settings.debug:
        print(f"⚠️  Предупреждение: {e}")
    else:
        raise


# === КОНСТАНТЫ ПРИЛОЖЕНИЯ ===
class AppConstants:
    """Константы приложения"""
    
    # Названия статусов по умолчанию
    DEFAULT_STATUSES = {
        "active": "Активный",
        "inactive": "Неактивный", 
        "blocked": "Заблокированный",
        "pending": "Ожидает подтверждения",
        "confirmed": "Подтверждено",
        "cancelled": "Отменено",
        "completed": "Завершено",
    }
    
    # Максимальные длины полей
    MAX_LOGIN_LENGTH = 100
    MAX_NAME_LENGTH = 100
    MAX_EMAIL_LENGTH = 255
    MAX_DESCRIPTION_LENGTH = 1000
    
    # Ограничения на значения
    MIN_PASSWORD_LENGTH = 6
    MAX_WORKSPACES_PER_ROOM = 100
    MAX_BOOKINGS_PER_DAY = 50
    
    # Лимиты запросов
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # Настройки валидации
    PHONE_REGEX = r'^\+?[\d\s\-\(\)]+$'
    EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
