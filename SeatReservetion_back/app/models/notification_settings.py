"""
Модель NotificationSettings - глобальные настройки системы уведомлений
Хранит конфигурацию SMTP сервера и другие параметры
"""
from sqlalchemy import Column, String, Boolean, Integer
from app.core.base import BaseModel


class NotificationSettings(BaseModel):
    """Модель глобальных настроек уведомлений"""
    __tablename__ = "notification_settings"

    # SMTP настройки
    smtp_host = Column(String(255), nullable=True, comment="SMTP хост")
    smtp_port = Column(Integer, nullable=True, comment="SMTP порт")
    smtp_user = Column(String(255), nullable=True, comment="SMTP пользователь")
    smtp_password = Column(String(255), nullable=True, comment="SMTP пароль")
    smtp_from_email = Column(String(255), nullable=True, comment="Email отправителя")
    smtp_from_name = Column(String(255), nullable=True, comment="Имя отправителя")
    smtp_use_tls = Column(Boolean, default=True, nullable=False, comment="Использовать TLS")

    # Общие настройки
    email_notifications_enabled = Column(Boolean, default=True, nullable=False, comment="Глобально включены ли email уведомления")

    def __repr__(self):
        return f"<NotificationSettings(smtp_host={self.smtp_host}, email_enabled={self.email_notifications_enabled})>"
