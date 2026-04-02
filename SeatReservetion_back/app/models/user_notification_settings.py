"""
Модель UserNotificationSettings - настройки уведомлений пользователя
Позволяет пользователю управлять способами получения уведомлений
"""
from sqlalchemy import Column, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.base import BaseModel


class UserNotificationSettings(BaseModel):
    """Модель настроек уведомлений пользователя"""
    __tablename__ = "user_notification_settings"

    user_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, unique=True, comment="ID пользователя")
    email_enabled = Column(Boolean, default=True, nullable=False, comment="Включены ли email уведомления")
    site_enabled = Column(Boolean, default=True, nullable=False, comment="Включены ли уведомления на сайте")

    # Отношение к пользователю
    user = relationship("Account", back_populates="notification_settings")

    def __repr__(self):
        return f"<UserNotificationSettings(user_id={self.user_id}, email={self.email_enabled}, site={self.site_enabled})>"
