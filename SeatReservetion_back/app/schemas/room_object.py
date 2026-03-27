"""
Pydantic схемы для объектов помещения
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# === Базовые схемы ===

class RoomObjectBase(BaseModel):
    """Базовая схема для объекта помещения"""
    object_type: str = Field(..., description="Тип объекта", example="workspace")
    x: float = Field(default=0.0, description="Координата X", example=100.0)
    y: float = Field(default=0.0, description="Координата Y", example=200.0)
    rotation: int = Field(default=0, description="Угол поворота", example=90)
    width: float = Field(default=100.0, description="Ширина", example=100.0)
    height: float = Field(default=50.0, description="Высота", example=50.0)
    name: Optional[str] = Field(None, description="Имя объекта", example="Рабочее место 1")
    description: Optional[str] = Field(None, description="Описание", example="Описание объекта")
    is_active: bool = Field(default=True, description="Активен ли объект")
    properties: Optional[Dict[str, Any]] = Field(None, description="Дополнительные свойства JSON")


class RoomObjectCreate(RoomObjectBase):
    """Схема для создания объекта"""
    room_id: int = Field(..., description="ID помещения")


class RoomObjectUpdate(BaseModel):
    """Схема для обновления объекта"""
    x: Optional[float] = None
    y: Optional[float] = None
    rotation: Optional[int] = None
    width: Optional[float] = None
    height: Optional[float] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    properties: Optional[Dict[str, Any]] = None


class RoomObjectResponse(RoomObjectBase):
    """Схема ответа объекта"""
    id: int
    room_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# === Схемы для стен ===

class WallBase(BaseModel):
    """Базовая схема для стены"""
    wall_type: str = Field(default="horizontal", description="Тип стены", example="horizontal")
    length: int = Field(default=200, description="Длина", example=200)
    thickness: int = Field(default=10, description="Толщина", example=10)
    has_window: bool = Field(default=False, description="Есть ли окно")
    has_door: bool = Field(default=False, description="Есть ли дверь")


class WallCreate(WallBase):
    """Схема для создания стены"""
    room_object_id: int


class WallResponse(WallBase):
    """Схема ответа стены"""
    id: int
    room_object_id: int

    class Config:
        from_attributes = True


# === Схемы для дверей ===

class DoorBase(BaseModel):
    """Базовая схема для двери"""
    door_type: str = Field(default="single", description="Тип двери", example="single")
    swing_direction: str = Field(default="left", description="Направление открытия", example="left")
    is_open: bool = Field(default=False, description="Открыта ли дверь")
    width: int = Field(default=80, description="Ширина", example=80)


class DoorCreate(DoorBase):
    """Схема для создания двери"""
    room_object_id: int


class DoorResponse(DoorBase):
    """Схема ответа двери"""
    id: int
    room_object_id: int

    class Config:
        from_attributes = True


# === Схемы для окон ===

class WindowBase(BaseModel):
    """Базовая схема для окна"""
    width: int = Field(default=100, description="Ширина", example=100)
    height: int = Field(default=60, description="Высота", example=60)
    is_open: bool = Field(default=False, description="Открыто ли окно")
    window_type: str = Field(default="single", description="Тип окна", example="single")


class WindowCreate(WindowBase):
    """Схема для создания окна"""
    room_object_id: int


class WindowResponse(WindowBase):
    """Схема ответа окна"""
    id: int
    room_object_id: int

    class Config:
        from_attributes = True


# === Схемы для рабочих мест на плане ===

class WorkspaceOnPlanBase(BaseModel):
    """Базовая схема для рабочего места на плане"""
    workspace_id: Optional[int] = Field(None, description="ID рабочего места")
    status_id: int = Field(default=1, description="ID статуса")
    workspace_number: Optional[int] = Field(None, description="Номер рабочего места")


class WorkspaceOnPlanCreate(WorkspaceOnPlanBase):
    """Схема для создания рабочего места на плане"""
    room_object_id: int


class WorkspaceOnPlanUpdate(BaseModel):
    """Схема для обновления рабочего места"""
    workspace_id: Optional[int] = None
    status_id: Optional[int] = None
    workspace_number: Optional[int] = None


class WorkspaceOnPlanResponse(WorkspaceOnPlanBase):
    """Схема ответа рабочего места"""
    id: int
    room_object_id: int

    class Config:
        from_attributes = True


# === Схемы для плана помещения ===

class RoomPlanCreate(BaseModel):
    """Схема для создания всего плана помещения"""
    objects: List[Dict[str, Any]] = Field(..., description="Список всех объектов плана")


class RoomPlanResponse(BaseModel):
    """Схема ответа плана помещения"""
    room_id: int
    objects: List[RoomObjectResponse]
    total_objects: int
