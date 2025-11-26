"""
Модель Account - аккаунты пользователей
Содержит данные аутентификации и персональную информацию пользователей.
Учетные записи для входа в систему и персональные данные пользователей.
"""
from datetime import datetime, date
from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, UniqueConstraint, Date
from sqlalchemy.orm import relationship
from app.core.base import BaseModel


class Account(BaseModel):
    """Модель аккаунтов пользователей"""
    __tablename__ = "accounts"
    
    # Данные аутентификации
    login = Column(String(100), unique=True, nullable=False, comment="Логин для входа")
    password_hash = Column(String(255), nullable=False, comment="Хеш пароля")
    password_set_at = Column(DateTime, default=datetime.utcnow, comment="Дата установки пароля")
    is_admin = Column(Boolean, default=False, comment="Является ли администратором")
    
    # Персональные данные
    first_name = Column(String(100), nullable=False, comment="Имя")
    last_name = Column(String(100), nullable=False, comment="Фамилия")
    middle_name = Column(String(100), nullable=True, comment="Отчество")
    birth_date = Column(Date, nullable=True, comment="Дата рождения")
    phone = Column(String(20), nullable=True, comment="Телефон")
    email = Column(String(255), nullable=True, comment="Бизнес-почта")
    
    # Связи
    status_id = Column(Integer, ForeignKey("statuses.id"), nullable=False, comment="ID статуса пользователя")
    
    # Отношения
    status = relationship("Status", back_populates="accounts")
    
    # Отношение к бронированиям
    bookings = relationship("Booking", back_populates="account", cascade="all, delete-orphan")
    
    # Ограничения
    __table_args__ = (
        UniqueConstraint('login', name='uq_accounts_login'),
    )