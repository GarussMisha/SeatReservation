"""
Общие зависимости для FastAPI приложения
Определяет базовые функции и классы, используемые в API
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.models.account import Account
from app.core.security import verify_jwt_token


# Схема безопасности для API
security = HTTPBearer()


def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[Account]:
    """
    Получение текущего пользователя из токена
    """
    # Обычная аутентификация
    try:
        token = credentials.credentials
        
        if not token:
            if settings.debug:
                # В debug режиме без токена возвращаем None
                return None
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен не предоставлен"
            )
        
        token_data = verify_jwt_token(token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный токен"
            )
        
        user_id = token_data.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен не содержит ID пользователя"
            )
        
        user = db.query(Account).filter(Account.id == int(user_id)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден"
            )
        
        # Проверяем статус: только active (id=1) может использовать API
        if getattr(user, 'status_id', 0) != 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Аккаунт неактивен или заблокирован"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Ошибка аутентификации: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Ошибка аутентификации: {str(e)}"
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Account:
    """
    Получение текущего пользователя (алиас для обратной совместимости)
    """
    return get_current_user_from_token(credentials, db)


def get_current_admin_user(
    current_user: Account = Depends(get_current_user)
) -> Account:
    """
    Получение текущего администратора
    """
    if not getattr(current_user, 'is_admin', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав доступа"
        )
    return current_user


def verify_database_connection() -> bool:
    """
    Проверка подключения к базе данных
    """
    try:
        from app.core.database import engine
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception:
        return False


class DatabaseService:
    """Сервис для работы с базой данных"""
    
    @staticmethod
    def health_check() -> dict:
        """Проверка состояния базы данных"""
        return {
            "database": "connected" if verify_database_connection() else "disconnected",
            "settings": {
                "debug": settings.debug,
                "app_name": settings.app_name,
                "version": settings.app_version
            }
        }


# Экспорт основных зависимостей
__all__ = [
    "get_db",
    "get_current_user", 
    "get_current_admin_user",
    "security",
    "DatabaseService",
    "verify_database_connection"
]