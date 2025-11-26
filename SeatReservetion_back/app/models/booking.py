"""
модель Booking (бронирование)
Записи о бронировании рабочих мест на определенную дату.
Связывает аккаунт пользователя, рабочее место и статус бронирования.
"""
from datetime import date
from sqlalchemy import Column, Date, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.base import BaseModel


class Booking(BaseModel):
    """Модель бронирований"""
    __tablename__ = "bookings"
    
    booking_date = Column(Date, nullable=False, comment="Дата бронирования")
    status_id = Column(Integer, ForeignKey("statuses.id"), nullable=False, comment="ID статуса бронирования")
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, comment="ID аккаунта")
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False, comment="ID рабочего места")
    
    # Отношения
    account = relationship("Account", back_populates="bookings")
    workspace = relationship("Workspace", back_populates="bookings")
    status = relationship("Status", back_populates="bookings")