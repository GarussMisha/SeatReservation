"""
Модель Status - статусы
Универсальная модель для хранения статусов всех сущностей в системе.
Используется для управления состоянием аккаунтов, помещений и бронирований.
"""
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.core.base import BaseModel


class Status(BaseModel):
    """Модель статусов"""
    __tablename__ = "statuses"
    
    name = Column(String(50), unique=True, nullable=False, comment="Название статуса")
    description = Column(String(255), nullable=True, comment="Описание статуса")
    
    # Отношение к аккаунтам
    accounts = relationship("Account", back_populates="status", cascade="all, delete-orphan")
    
    # Отношение к помещениям
    rooms = relationship("Room", back_populates="status", cascade="all, delete-orphan")
    
    # Отношение к бронированиям
    bookings = relationship("Booking", back_populates="status", cascade="all, delete-orphan")