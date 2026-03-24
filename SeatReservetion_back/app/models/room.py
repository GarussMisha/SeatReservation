"""
модель Room - помещения/комнаты
Физические локации компании, где располагаются рабочие места.
Может содержать описание, адрес и привязку к статусу.
"""
from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.base import BaseModel


class Room(BaseModel):
    """Модель помещений/комнат"""
    __tablename__ = "rooms"

    name = Column(String(200), nullable=False, unique=True, comment="Название помещения")
    address = Column(String(500), nullable=True, comment="Адрес помещения")
    description = Column(String(1000), nullable=True, comment="Описание помещения")
    status_id = Column(Integer, ForeignKey("statuses.id"), nullable=False, comment="ID статуса помещения")

    # Отношение к рабочим местам
    workspaces = relationship("Workspace", back_populates="room", cascade="all, delete-orphan")

    # Отношение к статусу
    status = relationship("Status", back_populates="rooms")

    # Уникальный индекс на название помещения
    __table_args__ = (
        UniqueConstraint('name', name='uq_rooms_name'),
    )