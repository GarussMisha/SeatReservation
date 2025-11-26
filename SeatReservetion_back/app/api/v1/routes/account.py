"""
API роуты для управления аккаунтами пользователей
Предоставляет CRUD операции для создания, чтения, обновления и удаления аккаунтов
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.api.deps import get_current_user_from_token, get_current_admin_user
from app.models.account import Account
from app.models.status import Status
from app.schemas.account import (
    AccountCreate,
    AccountUpdate,
    AccountResponse,
    AccountSearchParams,
    AccountLogin,
    AccountLoginResponse
)
from app.core.security import create_access_token, verify_password, get_password_hash
from app.core.config import settings

router = APIRouter(tags=["accounts"])


def format_account_response(account: Account, db: Session, is_admin_view: bool = False) -> Dict[str, Any]:
    """
    Форматирование ответа с данными аккаунта
    
    Args:
        account: Объект аккаунта из БД
        db: Сессия базы данных
        is_admin_view: Показывать ли полные PII данные (для админов)
    
    Returns:
        Словарь с отформатированными данными
    """
    # Получаем связанные данные статуса
    status_obj = db.query(Status).filter(Status.id == account.status_id).first()
    
    # Подсчитываем бронирования
    booking_count = len(account.bookings) if account.bookings else 0
    last_booking = None
    if account.bookings:
        # Берем последнее бронирование по дате
        last_booking = max(account.bookings, key=lambda b: b.created_at)
    
    # Безопасное получение дат
    password_set_at = getattr(account, 'password_set_at', None)
    created_at = getattr(account, 'created_at', None)
    
    password_set_at_str = password_set_at.isoformat() if password_set_at else None
    created_at_str = created_at.isoformat() if created_at else None
    last_booking_str = last_booking.created_at.isoformat() if last_booking else None
    
    return {
        "id": getattr(account, 'id', None),
        "login": getattr(account, 'login', None),
        "is_admin": getattr(account, 'is_admin', False),
        "status_id": getattr(account, 'status_id', None),
        "password_set_at": password_set_at_str,
        "created_at": created_at_str,
        # Персональные данные (из объединенной модели Account)
        "first_name": getattr(account, 'first_name', None),
        "last_name": getattr(account, 'last_name', None),
        "middle_name": getattr(account, 'middle_name', None) if is_admin_view else None,
        "birth_date": getattr(account, 'birth_date', None) if is_admin_view else None,
        "phone": getattr(account, 'phone', None) if is_admin_view else None,
        "email": getattr(account, 'email', None) if is_admin_view else None,
        # Данные статуса
        "status_name": getattr(status_obj, 'name', None) if status_obj else None,
        # Статистика
        "booking_count": booking_count,
        "last_booking_date": last_booking_str
    }


@router.get("/me")
async def get_current_user(
    current_user: Account = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """
    Получить данные текущего пользователя
    
    Args:
        current_user: Аутентифицированный пользователь
        db: Сессия базы данных
    
    Returns:
        Данные текущего пользователя
    """
    try:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не аутентифицирован"
            )
        
        result = format_account_response(current_user, db, is_admin_view=True)
        result["message"] = "Данные пользователя получены"
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении данных пользователя: {str(e)}"
        )


@router.get("/{account_id}", response_model=Dict[str, Any])
async def get_account(
    account_id: int,
    current_user: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Получить конкретный аккаунт по ID
    
    Args:
        account_id: ID аккаунта
        db: Сессия базы данных
    
    Returns:
        Данные аккаунта с связанной информацией
    
    Raises:
        HTTPException: 404 если аккаунт не найден
    """
    try:
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Аккаунт с ID {account_id} не найден"
            )
        
        return format_account_response(account, db, is_admin_view=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении аккаунта: {str(e)}"
        )


@router.get("/", response_model=List[Dict[str, Any]])
async def get_all_accounts(
    skip: int = 0,
    limit: int = 100,
    current_user: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Получить список всех аккаунтов с пагинацией
    
    Args:
        skip: Количество пропускаемых записей
        limit: Максимальное количество возвращаемых записей
        db: Сессия базы данных
    
    Returns:
        Список аккаунтов с связанными данными
    """
    try:
        accounts = db.query(Account).offset(skip).limit(limit).all()
        result = []
        
        for account in accounts:
            result.append(format_account_response(account, db, is_admin_view=True))
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении аккаунтов: {str(e)}"
        )


@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_account(
    account_data: AccountCreate,
    current_user: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Создать новый аккаунт
    
    Args:
        account_data: Данные для создания аккаунта
        db: Сессия базы данных
    
    Returns:
        Созданный аккаунт с полными данными
    
    Raises:
        HTTPException: 400 если статус не найден
        HTTPException: 400 если логин уже существует
    """
    try:
        # Проверяем существование статуса
        status_obj = db.query(Status).filter(Status.id == account_data.status_id).first()
        if not status_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Статус с ID {account_data.status_id} не найден"
            )
        
        # Проверяем уникальность логина
        existing_account = db.query(Account).filter(Account.login == account_data.login).first()
        if existing_account:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Аккаунт с логином '{account_data.login}' уже существует"
            )
        
        # Создаем аккаунт с использованием стандартного хэширования
        password_hash = get_password_hash(account_data.password)
        
        new_account = Account(
            login=account_data.login,
            password_hash=password_hash,
            password_set_at=datetime.utcnow(),
            is_admin=account_data.is_admin,
            status_id=account_data.status_id,
            # Персональные данные из объединенной модели
            first_name=account_data.first_name,
            last_name=account_data.last_name,
            middle_name=account_data.middle_name,
            birth_date=account_data.birth_date,
            phone=account_data.phone,
            email=account_data.email
        )
        
        db.add(new_account)
        db.commit()
        db.refresh(new_account)
        
        # Форматируем ответ
        result = format_account_response(new_account, db, is_admin_view=True)
        result["message"] = "Аккаунт успешно создан"
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании аккаунта: {str(e)}"
        )


@router.put("/{account_id}", response_model=Dict[str, Any])
async def update_account(
    account_id: int,
    account_data: AccountUpdate,
    current_user: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Обновить данные аккаунта
    
    Args:
        account_id: ID аккаунта
        account_data: Данные для обновления
        db: Сессия базы данных
    
    Returns:
        Обновленный аккаунт
    
    Raises:
        HTTPException: 404 если аккаунт не найден
        HTTPException: 400 если логин уже существует
    """
    try:
        # Проверяем существование аккаунта
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Аккаунт с ID {account_id} не найден"
            )
        
        # Проверяем уникальность логина, если он изменяется
        if account_data.login and account_data.login != account.login:
            existing_account = db.query(Account).filter(
                Account.login == account_data.login,
                Account.id != account_id
            ).first()
            if existing_account:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Аккаунт с логином '{account_data.login}' уже существует"
                )
        
        # Обновляем поля
        update_data = account_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == "password" and value:
                # Хешируем новый пароль
                setattr(account, "password_hash", get_password_hash(value))
                setattr(account, "password_set_at", datetime.utcnow())
            else:
                setattr(account, field, value)
        
        db.commit()
        db.refresh(account)
        
        # Форматируем ответ
        result = format_account_response(account, db, is_admin_view=True)
        result["message"] = "Аккаунт успешно обновлен"
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении аккаунта: {str(e)}"
        )


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: int,
    current_user: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Удалить аккаунт
    
    Args:
        account_id: ID аккаунта
        db: Сессия базы данных
    
    Raises:
        HTTPException: 404 если аккаунт не найден
    """
    try:
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Аккаунт с ID {account_id} не найден"
            )
        
        db.delete(account)
        db.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении аккаунта: {str(e)}"
        )



@router.post("/auth/login", response_model=AccountLoginResponse)
async def login_user(
    login_data: AccountLogin,
    db: Session = Depends(get_db)
):
    """
    Полная реализация аутентификации пользователя
    
    Authenticate a user with login and password, returning an access token and user information.
    
    Args:
        login_data: Данные для входа (login - логин или email, password - пароль)
        db: Сессия базы данных
    
    Returns:
        Результат аутентификации с токеном доступа и данными пользователя
    
    Raises:
        HTTPException: 401 если неверные данные для входа
        HTTPException: 500 при внутренней ошибке сервера
    """
    try:
        # Находим аккаунт по логину или email
        from sqlalchemy import or_
        account = db.query(Account).filter(
            or_(Account.login == login_data.login, Account.email == login_data.login)
        ).first()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный логин, email или пароль"
            )
        
        # Проверяем пароль
        password_hash_value = getattr(account, 'password_hash', '')
        if not verify_password(login_data.password, password_hash_value):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный логин или пароль"
            )
        
        # Проверяем статус аккаунта: только status_id == 1 (active) может войти
        if getattr(account, 'status_id', 0) != 1:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Аккаунт неактивен или заблокирован"
            )
        
        # Создаем токен доступа
        is_admin_value = bool(getattr(account, 'is_admin', False))
        access_token = create_access_token(
            subject=str(account.id),
            is_admin=is_admin_value
        )
        
        # Форматируем ответ
        result = format_account_response(account, db, is_admin_view=True)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": result,
            "message": "Успешный вход в систему"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при аутентификации: {str(e)}"
        )


@router.get("/stats/overview", response_model=Dict[str, Any])
async def get_accounts_stats(
    current_user: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Получить статистику по аккаунтам
    
    Args:
        db: Сессия базы данных
    
    Returns:
        Статистика по аккаунтам
    """
    try:
        # Общая статистика
        total_accounts = db.query(Account).count()
        admin_accounts = db.query(Account).filter(Account.is_admin == True).count()
        user_accounts = total_accounts - admin_accounts
        
        # Распределение по статусам
        accounts_by_status = {}
        all_statuses = db.query(Status).all()
        for status in all_statuses:
            count = db.query(Account).filter(Account.status_id == status.id).count()
            accounts_by_status[status.name] = count
        
        return {
            "total_accounts": total_accounts,
            "admin_accounts": admin_accounts,
            "user_accounts": user_accounts,
            "accounts_by_status": accounts_by_status
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении статистики: {str(e)}"
        )