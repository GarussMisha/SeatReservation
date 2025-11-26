"""
Модуль для работы с безопасностью и аутентификацией
Упрощенная реализация для тестирования
"""
import hashlib
import secrets
import base64
import json
from datetime import datetime, timedelta
from typing import Optional, Union, Dict
from passlib.context import CryptContext

# Временное хранилище токенов для извлечения данных пользователя
# В продакшене здесь была бы база данных или Redis
token_store: Dict[str, Dict] = {}

def create_access_token(
    subject: Union[str, int], 
    expires_delta: Optional[timedelta] = None,
    is_admin: bool = False
) -> str:
    """
    Создание простого токена (заглушка для JWT)
    
    Args:
        subject: ID пользователя
        expires_delta: Время жизни токена
        is_admin: Является ли пользователь администратором
    
    Returns:
        Простой токен
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    
    # Создаем уникальный ID токена
    token_id = secrets.token_hex(16)
    
    # Создаем hash токена
    token_hash = hashlib.sha256(token_id.encode()).hexdigest()[:32]
    
    # Создаем данные токена
    token_data = {
        "user_id": str(subject),
        "is_admin": is_admin,
        "exp": expire.timestamp(),
        "iat": datetime.utcnow().timestamp(),
        "token_id": token_id,
        "token_hash": token_hash
    }
    
    # Сохраняем данные в временное хранилище по hash
    token_store[token_hash] = token_data
    
    return f"sr_{token_hash}"  # Возвращаем токен

def verify_token(token: str) -> Optional[dict]:
    """
    Проверка токена и извлечение данных пользователя
    
    Args:
        token: Токен
    
    Returns:
        Данные пользователя или None, если токен недействителен
    """
    if not token or not token.startswith("sr_"):
        return None
    
    try:
        # Извлекаем hash из токена
        token_hash = token[3:]  # Убираем префикс "sr_"
        
        # Проверяем длину hash
        if len(token_hash) != 32:
            return None
        
        # Ищем данные токена в хранилище
        token_data = token_store.get(token_hash)
        if not token_data:
            return None
        
        # Проверяем срок действия токена
        current_time = datetime.utcnow().timestamp()
        if token_data.get("exp", 0) < current_time:
            # Удаляем просроченный токен
            del token_store[token_hash]
            return None
        
        return token_data
        
    except Exception:
        return None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверка пароля с bcrypt
    
    Args:
        plain_password: Обычный пароль
        hashed_password: Хешированный пароль
    
    Returns:
        True если пароль верный, False иначе
    """
    # Truncate for bcrypt compatibility
    pwd_bytes = plain_password.encode('utf-8')[:72]
    pwd_str = pwd_bytes.decode('utf-8')
    return pwd_context.verify(pwd_str, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Хеширование пароля с bcrypt
    
    Args:
        password: Обычный пароль
    
    Returns:
        Хешированный пароль
    """
    # Bcrypt limit: 72 bytes, truncate safely
    pwd_bytes = password.encode('utf-8')[:72]
    pwd_str = pwd_bytes.decode('utf-8')
    return pwd_context.hash(pwd_str)

def verify_jwt_token(token: str) -> Optional[dict]:
    """
    Универсальная функция для проверки JWT токена
    
    Args:
        token: JWT токен
    
    Returns:
        Данные пользователя или None
    """
    payload = verify_token(token)
    
    if not payload:
        return None
    
    return {
        "user_id": payload.get("user_id"),
        "is_admin": payload.get("is_admin", False)
    }