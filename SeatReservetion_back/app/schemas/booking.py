"""
Pydantic схемы для модели Booking (бронирования)
Определяют структуру данных для API запросов и ответов, связанных с бронированием рабочих мест
"""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.core.config import AppConstants


class BookingBase(BaseModel):
    """Базовая схема бронирования"""
    booking_date: date = Field(
        description="Дата бронирования"
    )
    status_id: int = Field(
        description="ID статуса бронирования"
    )
    account_id: int = Field(
        description="ID аккаунта, который бронирует"
    )
    workspace_id: int = Field(
        description="ID бронируемого рабочего места"
    )


class BookingCreate(BookingBase):
    """Схема для создания нового бронирования"""
    pass


class BookingUpdate(BaseModel):
    """Схема для обновления бронирования"""
    booking_date: Optional[date] = Field(
        default=None,
        description="Дата бронирования"
    )
    status_id: Optional[int] = Field(
        default=None,
        description="ID статуса бронирования"
    )
    workspace_id: Optional[int] = Field(
        default=None,
        description="ID рабочего места"
    )


class BookingResponse(BookingBase):
    """Схема ответа с данными бронирования"""
    id: int
    created_at: datetime
    
    # Данные связанного аккаунта (пользователя)
    account_login: Optional[str] = None
    account_first_name: Optional[str] = None
    account_last_name: Optional[str] = None
    account_email: Optional[str] = None
    
    # Данные связанного рабочего места
    workspace_name: Optional[str] = None
    workspace_room_name: Optional[str] = None
    workspace_room_address: Optional[str] = None
    
    # Данные статуса
    status_name: Optional[str] = None
    status_description: Optional[str] = None
    
    class Config:
        """Конфигурация для сериализации"""
        from_attributes = True


class BookingWithDetails(BookingResponse):
    """Схема бронирования с детальной информацией"""
    # Информация о сотруднике
    worker_full_name: Optional[str] = Field(
        default=None,
        description="Полное имя сотрудника"
    )
    
    # Информация о помещении
    room_details: Optional[dict] = Field(
        default=None,
        description="Детальная информация о помещении"
    )
    
    # Статусные поля
    can_cancel: bool = Field(
        default=False,
        description="Можно ли отменить бронирование"
    )
    can_modify: bool = Field(
        default=False,
        description="Можно ли изменить бронирование"
    )
    is_past: bool = Field(
        default=False,
        description="Относится ли бронирование к прошлому"
    )
    is_today: bool = Field(
        default=False,
        description="Бронирование на сегодня"
    )


class BookingSearchParams(BaseModel):
    """Параметры поиска бронирований"""
    search: Optional[str] = Field(
        default=None,
        description="Поиск по логину пользователя, названию рабочего места"
    )
    account_id: Optional[int] = Field(
        default=None,
        description="Фильтр по ID пользователя"
    )
    workspace_id: Optional[int] = Field(
        default=None,
        description="Фильтр по ID рабочего места"
    )
    status_id: Optional[int] = Field(
        default=None,
        description="Фильтр по ID статуса"
    )
    date_from: Optional[date] = Field(
        default=None,
        description="Начальная дата диапазона"
    )
    date_to: Optional[date] = Field(
        default=None,
        description="Конечная дата диапазона"
    )
    only_upcoming: bool = Field(
        default=False,
        description="Только предстоящие бронирования"
    )
    only_today: bool = Field(
        default=False,
        description="Только на сегодня"
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
        default="booking_date",
        description="Поле для сортировки"
    )
    sort_order: str = Field(
        default="asc",
        description="Порядок сортировки (asc/desc)"
    )


class BookingAvailability(BaseModel):
    """Схема для проверки доступности"""
    workspace_id: int
    date: date
    is_available: bool = Field(
        description="Доступно ли рабочее место"
    )
    existing_booking: Optional[BookingResponse] = Field(
        default=None,
        description="Существующее бронирование (если есть)"
    )
    alternative_suggestions: List[dict] = Field(
        default_factory=list,
        description="Альтернативные предложения"
    )


class BookingConflict(BaseModel):
    """Схема для конфликта бронирования"""
    conflict_type: str = Field(
        description="Тип конфликта"
    )
    conflicting_booking: BookingResponse = Field(
        description="Конфликтующее бронирование"
    )
    suggested_alternatives: List[dict] = Field(
        default_factory=list,
        description="Предложенные альтернативы"
    )


class BookingStats(BaseModel):
    """Статистика по бронированиям"""
    total_bookings: int = Field(
        description="Общее количество бронирований"
    )
    upcoming_bookings: int = Field(
        description="Предстоящие бронирования"
    )
    today_bookings: int = Field(
        description="Бронирования на сегодня"
    )
    past_bookings: int = Field(
        description="Прошедшие бронирования"
    )
    cancelled_bookings: int = Field(
        description="Отмененные бронирования"
    )
    bookings_by_status: dict = Field(
        description="Распределение по статусам"
    )
    bookings_by_workspace: dict = Field(
        description="Распределение по рабочим местам"
    )
    utilization_rate: float = Field(
        description="Коэффициент использования"
    )


class BookingCalendar(BaseModel):
    """Календарь бронирований"""
    date: date
    bookings: List[BookingResponse] = Field(
        default_factory=list,
        description="Бронирования на дату"
    )
    total_workspaces: int = Field(
        description="Общее количество рабочих мест"
    )
    booked_workspaces: int = Field(
        description="Забронированные рабочие места"
    )
    available_workspaces: int = Field(
        description="Доступные рабочие места"
    )
    utilization_percentage: float = Field(
        description="Процент использования"
    )


class BookingCreateRequest(BaseModel):
    """Запрос на создание бронирования с валидацией"""
    workspace_id: int = Field(
        description="ID рабочего места"
    )
    booking_date: date = Field(
        description="Дата бронирования"
    )
    validate_availability: bool = Field(
        default=True,
        description="Проверять доступность перед созданием"
    )


class BookingBulkAction(BaseModel):
    """Массовые операции с бронированиями"""
    booking_ids: List[int] = Field(
        description="Список ID бронирований"
    )
    new_status_id: Optional[int] = Field(
        default=None,
        description="Новый статус (для массового изменения)"
    )
    reason: Optional[str] = Field(
        default=None,
        description="Причина массовой операции"
    )