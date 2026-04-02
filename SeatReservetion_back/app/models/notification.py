"""
Модель Notification - уведомления пользователей
Система уведомлений о событиях в системе бронирования рабочих мест.
Поддерживает немедленные и отложенные уведомления по email.
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from app.core.base import BaseModel


class Notification(BaseModel):
    """Модель уведомлений пользователей"""
    __tablename__ = "notifications"

    # Тип уведомления
    notification_type = Column(String(50), nullable=False, comment="Тип уведомления: booking_cancelled, workspace_disabled, room_disabled, custom")
    
    # Тема и текст сообщения
    subject = Column(String(255), nullable=False, comment="Тема уведомления")
    message = Column(Text, nullable=False, comment="Текст сообщения")
    
    # Планирование отправки
    scheduled_at = Column(DateTime, nullable=True, comment="Запланированное время отправки (NULL = немедленно)")
    sent_at = Column(DateTime, nullable=True, comment="Фактическое время отправки")
    
    # Статус отправки
    status_id = Column(Integer, ForeignKey("statuses.id"), nullable=False, comment="ID статуса уведомления")
    
    # Получатель (NULL = массовая рассылка)
    user_id = Column(Integer, ForeignKey("accounts.id"), nullable=True, comment="ID получателя (NULL для массовой рассылки)")
    
    # Автор создания (для ручной рассылки от админа)
    created_by_id = Column(Integer, ForeignKey("accounts.id"), nullable=True, comment="ID создателя уведомления (админ)")
    
    # Отношения
    user = relationship("Account", back_populates="notifications", foreign_keys=[user_id])
    creator = relationship("Account", back_populates="created_notifications", foreign_keys=[created_by_id])
    status = relationship("Status", back_populates="notifications")
    user_settings = relationship("UserNotificationSettings", back_populates="user", foreign_keys=[user_id], viewonly=True)

    def __repr__(self):
        return f"<Notification(id={self.id}, type={self.notification_type}, status={self.status.name if self.status else 'N/A'})>"
