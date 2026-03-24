"""
модель Workspace (рабочее место)
Отдельные рабочие места в помещениях компании, которые можно бронировать.
Каждое место привязано к конкретной комнате и имеет статус активности.
"""
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.base import BaseModel


class Workspace(BaseModel):
    """Модель рабочих мест"""
    __tablename__ = "workspaces"

    name = Column(String(200), nullable=False, comment="Название рабочего места")
    is_active = Column(Boolean, default=True, comment="Активное ли место (устаревшее поле, используется status_id)")
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False, comment="ID помещения")
    status_id = Column(Integer, ForeignKey("statuses.id"), nullable=True, comment="ID статуса рабочего места (free, occupied, inactive)")

    # Отношение к помещению (многие к одному)
    room = relationship("Room", back_populates="workspaces")

    # Отношение к статусу
    status = relationship("Status", back_populates="workspaces")

    # Отношение к бронированиям
    bookings = relationship("Booking", back_populates="workspace", cascade="all, delete-orphan")

    # Уникальный индекс на название рабочего места в рамках помещения
    __table_args__ = (
        UniqueConstraint('name', 'room_id', name='uq_workspaces_name_room_id'),
    )