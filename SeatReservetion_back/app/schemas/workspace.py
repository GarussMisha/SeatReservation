"""
Pydantic схемы для модели Workspace (рабочие места)
Определяют структуру данных для API запросов и ответов, связанных с рабочими местами
"""
from typing import Optional
from pydantic import BaseModel, Field
from app.core.config import AppConstants


class WorkspaceBase(BaseModel):
    """Базовая схема рабочего места"""
    name: str = Field(
        max_length=200,
        description="Название рабочего места"
    )
    is_active: bool = Field(
        default=True,
        description="Активно ли рабочее место"
    )
    room_id: int = Field(
        description="ID помещения, в котором находится рабочее место"
    )


class WorkspaceCreate(WorkspaceBase):
    """Схема для создания нового рабочего места"""
    pass


class WorkspaceUpdate(BaseModel):
    """Схема для обновления рабочего места"""
    name: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Название рабочего места"
    )
    is_active: Optional[bool] = Field(
        default=None,
        description="Активно ли рабочее место"
    )
    room_id: Optional[int] = Field(
        default=None,
        description="ID помещения"
    )


class WorkspaceResponse(WorkspaceBase):
    """Схема ответа с данными рабочего места"""
    id: int
    created_at: str
    
    # Данные связанного помещения
    room_name: Optional[str] = None
    room_address: Optional[str] = None
    room_description: Optional[str] = None
    
    # Данные статуса помещения
    room_status_name: Optional[str] = None
    
    # Статистика
    total_bookings: int = Field(
        default=0,
        description="Общее количество бронирований"
    )
    active_bookings: int = Field(
        default=0,
        description="Количество активных бронирований"
    )
    
    class Config:
        """Конфигурация для сериализации"""
        from_attributes = True


class WorkspaceWithBookings(WorkspaceResponse):
    """Схема рабочего места с деталями бронирований"""
    current_booking: Optional[dict] = Field(
        default=None,
        description="Текущее бронирование (если есть)"
    )
    upcoming_bookings: list = Field(
        default_factory=list,
        description="Предстоящие бронирования"
    )


class WorkspaceAvailability(BaseModel):
    """Схема для проверки доступности рабочего места"""
    workspace_id: int
    date: str
    is_available: bool = Field(
        description="Доступно ли рабочее место в указанную дату"
    )
    current_booking: Optional[dict] = None


class WorkspaceSearchParams(BaseModel):
    """Параметры поиска рабочих мест"""
    search: Optional[str] = Field(
        default=None,
        description="Поиск по названию рабочего места или помещения"
    )
    room_id: Optional[int] = Field(
        default=None,
        description="Фильтр по ID помещения"
    )
    is_active: Optional[bool] = Field(
        default=None,
        description="Фильтр по активности"
    )
    date: Optional[str] = Field(
        default=None,
        description="Проверка доступности на определенную дату"
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
        default="name",
        description="Поле для сортировки"
    )
    sort_order: str = Field(
        default="asc",
        description="Порядок сортировки (asc/desc)"
    )


class WorkspaceStats(BaseModel):
    """Статистика по рабочим местам"""
    total_workspaces: int = Field(
        description="Общее количество рабочих мест"
    )
    active_workspaces: int = Field(
        description="Количество активных рабочих мест"
    )
    inactive_workspaces: int = Field(
        description="Количество неактивных рабочих мест"
    )
    workspaces_by_room: dict = Field(
        description="Распределение рабочих мест по помещениям"
    )
    utilization_rate: float = Field(
        description="Средний коэффициент использования (0-1)"
    )


class WorkspaceCreateMany(BaseModel):
    """Схема для массового создания рабочих мест"""
    workspaces: list[WorkspaceCreate] = Field(
        description="Список рабочих мест для создания"
    )
    room_id: int = Field(
        description="ID помещения (если не указан в отдельных местах)"
    )


class WorkspaceBulkUpdate(BaseModel):
    """Схема для массового обновления рабочих мест"""
    workspace_ids: list[int] = Field(
        description="Список ID рабочих мест для обновления"
    )
    is_active: Optional[bool] = Field(
        default=None,
        description="Новый статус активности"
    )
    room_id: Optional[int] = Field(
        default=None,
        description="Новое помещение"
    )