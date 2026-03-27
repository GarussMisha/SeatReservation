"""
Pydantic схемы для модели Room (помещения/комнаты)
Определяют структуру данных для API запросов и ответов, связанных с помещениями
"""
from typing import Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime
from app.core.status_constants import RoomStatuses


class RoomBase(BaseModel):
    """Базовая схема помещения"""
    name: str = Field(
        max_length=200,
        description="Название помещения"
    )
    address: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Адрес помещения"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Описание помещения"
    )
    status_id: int = Field(
        description="ID статуса помещения (1=active, 2=inactive)"
    )
    
    @validator('status_id')
    def validate_status_id(cls, v):
        """Проверка что статус разрешён для помещения"""
        if v not in RoomStatuses.ALLOWED:
            allowed_names = [RoomStatuses.NAMES.get(s) for s in RoomStatuses.ALLOWED]
            raise ValueError(f"Недопустимый статус помещения: {v}. Разрешены: {allowed_names}")
        return v


class RoomCreate(RoomBase):
    """Схема для создания нового помещения"""
    pass


class RoomUpdate(BaseModel):
    """Схема для обновления помещения"""
    name: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Название помещения"
    )
    address: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Адрес помещения"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Описание помещения"
    )
    status_id: Optional[int] = Field(
        default=None,
        description="ID статуса помещения (1=active, 2=inactive)"
    )
    
    @validator('status_id')
    def validate_status_id(cls, v):
        """Проверка что статус разрешён для помещения"""
        if v is not None and v not in RoomStatuses.ALLOWED:
            allowed_names = [RoomStatuses.NAMES.get(s) for s in RoomStatuses.ALLOWED]
            raise ValueError(f"Недопустимый статус помещения: {v}. Разрешены: {allowed_names}")
        return v


class RoomResponse(RoomBase):
    """Схема ответа с данными помещения"""
    id: int
    created_at: datetime
    
    # Данные связанного статуса
    status_name: Optional[str] = None
    status_color: Optional[str] = None
    
    # Статистика
    total_workspaces: int = Field(
        default=0,
        description="Общее количество рабочих мест"
    )
    active_workspaces: int = Field(
        default=0,
        description="Количество активных рабочих мест"
    )
    inactive_workspaces: int = Field(
        default=0,
        description="Количество неактивных рабочих мест"
    )
    
    class Config:
        """Конфигурация для сериализации"""
        from_attributes = True


class RoomWithDetails(RoomResponse):
    """Схема помещения с детальной информацией"""
    workspaces: list = Field(
        default_factory=list,
        description="Список рабочих мест в помещении"
    )
    latest_bookings: list = Field(
        default_factory=list,
        description="Последние бронирования в помещении"
    )


class RoomSearchParams(BaseModel):
    """Параметры поиска помещений"""
    search: Optional[str] = Field(
        default=None,
        description="Поиск по названию, адресу или описанию"
    )
    status_id: Optional[int] = Field(
        default=None,
        description="Фильтр по ID статуса"
    )
    has_workspaces: Optional[bool] = Field(
        default=None,
        description="Фильтр по наличию рабочих мест"
    )
    page: int = Field(
        default=1,
        ge=1,
        description="Номер страницы"
    )
    per_page: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Количество записей на странице"
    )
    sort_by: str = Field(
        default="name",
        description="Поле для сортировки"
    )
    sort_order: str = Field(
        default="asc",
        description="Порядок сортировки (asc/desc)"
    )


class RoomStats(BaseModel):
    """Статистика по помещениям"""
    total_rooms: int = Field(
        description="Общее количество помещений"
    )
    active_rooms: int = Field(
        description="Количество активных помещений"
    )
    inactive_rooms: int = Field(
        description="Количество неактивных помещений"
    )
    total_workspaces: int = Field(
        description="Общее количество рабочих мест"
    )
    active_workspaces: int = Field(
        description="Количество активных рабочих мест"
    )
    inactive_workspaces: int = Field(
        description="Количество неактивных рабочих мест"
    )
    rooms_by_status: dict = Field(
        description="Распределение помещений по статусам"
    )
    average_workspaces_per_room: float = Field(
        description="Среднее количество рабочих мест на помещение"
    )
    utilization_rate: float = Field(
        description="Средний коэффициент использования (0-1)"
    )


class RoomBulkUpdate(BaseModel):
    """Схема для массового обновления помещений"""
    room_ids: list[int] = Field(
        description="Список ID помещений для обновления"
    )
    status_id: Optional[int] = Field(
        default=None,
        description="Новый статус помещения"
    )
    address: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Новый адрес"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Новое описание"
    )