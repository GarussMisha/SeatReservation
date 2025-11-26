"""
Pydantic схемы для модели Account (аккаунты)
Определяют структуру данных для API запросов и ответов, связанных с аккаунтами пользователей
"""
from datetime import datetime, date
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.core.config import AppConstants


class AccountBase(BaseModel):
    """Базовая схема аккаунта"""
    login: str = Field(
        max_length=AppConstants.MAX_LOGIN_LENGTH,
        description="Логин аккаунта для входа в систему"
    )
    is_admin: bool = Field(
        default=False,
        description="Является ли пользователь администратором"
    )
    status_id: int = Field(
        description="ID статуса аккаунта"
    )
    
    # Персональные данные (из объединенной модели)
    first_name: str = Field(description="Имя пользователя")
    last_name: str = Field(description="Фамилия пользователя")
    middle_name: Optional[str] = Field(default=None, description="Отчество")
    birth_date: Optional[date] = Field(default=None, description="Дата рождения")
    phone: Optional[str] = Field(default=None, description="Телефон")
    email: str = Field(description="Бизнес-почта")


class AccountCreate(AccountBase):
    """Схема для создания нового аккаунта"""
    password: str = Field(
        min_length=AppConstants.MIN_PASSWORD_LENGTH,
        description="Пароль аккаунта (минимум 6 символов)"
    )


class AccountUpdate(BaseModel):
    """Схема для обновления аккаунта"""
    login: Optional[str] = Field(
        default=None,
        max_length=AppConstants.MAX_LOGIN_LENGTH,
        description="Логин аккаунта"
    )
    password: Optional[str] = Field(
        default=None,
        min_length=AppConstants.MIN_PASSWORD_LENGTH,
        description="Пароль аккаунта"
    )
    is_admin: Optional[bool] = Field(
        default=None,
        description="Является ли пользователь администратором"
    )
    status_id: Optional[int] = Field(
        default=None,
        description="ID статуса аккаунта"
    )
    # Персональные данные (опциональные для обновления)
    first_name: Optional[str] = Field(default=None, description="Имя пользователя")
    last_name: Optional[str] = Field(default=None, description="Фамилия пользователя")
    middle_name: Optional[str] = Field(default=None, description="Отчество")
    birth_date: Optional[date] = Field(default=None, description="Дата рождения")
    phone: Optional[str] = Field(default=None, description="Телефон")
    email: Optional[str] = Field(default=None, description="Бизнес-почта")


class AccountResponse(AccountBase):
    """Схема ответа с данными аккаунта"""
    id: int
    password_set_at: datetime
    created_at: datetime
    
    # Данные статуса
    status_name: Optional[str] = None
    
    class Config:
        """Конфигурация для сериализации"""
        from_attributes = True


class AccountLogin(BaseModel):
    """Схема для входа аккаунта в систему"""
    login: str = Field(
        description="Логин пользователя"
    )
    password: str = Field(
        description="Пароль аккаунта"
    )

class AccountLoginResponse(BaseModel):
    """Схема ответа при аутентификации"""
    access_token: str = Field(
        description="JWT токен для доступа"
    )
    token_type: str = Field(
        default="bearer",
        description="Тип токена"
    )
    user: Dict[str, Any] = Field(
        description="Данные пользователя"
    )
    message: str = Field(
        description="Сообщение о результате"
    )

class CurrentUserResponse(BaseModel):
    """Схема ответа с данными текущего пользователя"""
    id: int
    login: str
    is_admin: bool
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    email: Optional[str] = None
    status_name: Optional[str] = None
    booking_count: int = 0
    last_booking_date: Optional[datetime] = None
    
    class Config:
        """Конфигурация для сериализации"""
        from_attributes = True


class AccountWithStats(AccountResponse):
    """Схема аккаунта со статистикой"""
    booking_count: int = Field(
        default=0,
        description="Количество активных бронирований"
    )
    last_booking_date: Optional[datetime] = Field(
        default=None,
        description="Дата последнего бронирования"
    )


class AccountSearchParams(BaseModel):
    """Параметры поиска аккаунтов"""
    search: Optional[str] = Field(
        default=None,
        description="Поиск по логину, имени или фамилии"
    )
    status_id: Optional[int] = Field(
        default=None,
        description="Фильтр по ID статуса"
    )
    is_admin: Optional[bool] = Field(
        default=None,
        description="Фильтр по типу аккаунта (админ/обычный)"
    )
    page: int = Field(
        default=1,
        ge=1,
        description="Номер страницы"
    )
    per_page: int = Field(
        default=AppConstants.DEFAULT_PAGE_SIZE,
        ge=1,
        le=AppConstants.MAX_PAGE_SIZE,
        description="Количество записей на странице"
    )
    sort_by: str = Field(
        default="created_at",
        description="Поле для сортировки"
    )
    sort_order: str = Field(
        default="desc",
        description="Порядок сортировки (asc/desc)"
    )