"""
Pydantic схемы для уведомлений (Notifications)
Используются для валидации запросов и ответов API
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr


# === Схемы для создания уведомлений ===

class NotificationCreateBase(BaseModel):
    """Базовая схема для создания уведомления"""
    subject: str = Field(..., min_length=1, max_length=255, description="Тема уведомления")
    message: str = Field(..., min_length=1, description="Текст сообщения")


class NotificationScheduleCreate(BaseModel):
    """Схема для создания отложенной рассылки"""
    user_ids: List[int] = Field(..., min_items=1, description="Список ID пользователей для рассылки")
    subject: str = Field(..., min_length=1, max_length=255, description="Тема сообщения")
    message: str = Field(..., min_length=1, description="Текст сообщения")
    scheduled_at: datetime = Field(..., description="Время отправки (UTC)")


# === Схемы для ответов API ===

class NotificationResponse(BaseModel):
    """Схема ответа с данными уведомления"""
    id: int
    notification_type: str
    subject: str
    message: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    created_at: datetime
    status_id: int
    status_name: Optional[str] = None
    user_id: Optional[int] = None
    created_by_id: Optional[int] = None

    class Config:
        """Конфигурация Pydantic модели"""
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Схема ответа со списком уведомлений"""
    notifications: List[NotificationResponse]
    total: int
    page: int
    per_page: int


class NotificationStats(BaseModel):
    """Схема статистики уведомлений"""
    total_notifications: int
    pending_notifications: int
    sent_notifications: int
    failed_notifications: int
    scheduled_notifications: int
    notifications_by_type: Dict[str, int]


# === Схемы для операций с уведомлениями ===

class NotificationResendRequest(BaseModel):
    """Схема для повторной отправки уведомления"""
    pass


class NotificationCancelRequest(BaseModel):
    """Схема для отмены уведомления"""
    pass


# === Схемы для массовых операций ===

class NotificationBulkSendRequest(BaseModel):
    """Схема для массовой отправки уведомлений"""
    user_ids: List[int] = Field(..., min_items=1, description="Список ID пользователей")
    subject: str = Field(..., min_length=1, max_length=255, description="Тема")
    message: str = Field(..., min_length=1, description="Сообщение")
    send_now: bool = Field(default=True, description="Отправить немедленно или запланировать")
    scheduled_at: Optional[datetime] = Field(None, description="Время отправки (если не немедленно)")


# === Схемы для фильтрации ===

class NotificationFilter(BaseModel):
    """Схема для фильтрации уведомлений"""
    notification_type: Optional[str] = Field(None, description="Тип уведомления")
    status_id: Optional[int] = Field(None, description="ID статуса")
    date_from: Optional[datetime] = Field(None, description="Начальная дата")
    date_to: Optional[datetime] = Field(None, description="Конечная дата")
    user_id: Optional[int] = Field(None, description="ID пользователя")


# === Экспорт ===

__all__ = [
    "NotificationCreateBase",
    "NotificationScheduleCreate",
    "NotificationResponse",
    "NotificationListResponse",
    "NotificationStats",
    "NotificationResendRequest",
    "NotificationCancelRequest",
    "NotificationBulkSendRequest",
    "NotificationFilter",
]
