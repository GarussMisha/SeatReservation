"""
Pydantic схемы для настроек уведомлений
"""
from pydantic import BaseModel, Field
from typing import Optional


# =============================================================================
# НАСТРОЙКИ ПОЛЬЗОВАТЕЛЯ
# =============================================================================

class UserNotificationSettingsResponse(BaseModel):
    """Ответ с настройками уведомлений пользователя"""
    user_id: int = Field(..., description="ID пользователя")
    email_enabled: bool = Field(True, description="Включены ли email уведомления")
    site_enabled: bool = Field(True, description="Включены ли уведомления на сайте")

    class Config:
        from_attributes = True


class UserNotificationSettingsUpdate(BaseModel):
    """Данные для обновления настроек пользователя"""
    email_enabled: Optional[bool] = Field(None, description="Включены ли email уведомления")
    site_enabled: Optional[bool] = Field(None, description="Включены ли уведомления на сайте")


# =============================================================================
# ГЛОБАЛЬНЫЕ НАСТРОЙКИ (SMTP)
# =============================================================================

class NotificationSettingsResponse(BaseModel):
    """Ответ с глобальными настройками уведомлений"""
    id: int = Field(..., description="ID настроек")
    smtp_host: Optional[str] = Field(None, description="SMTP хост")
    smtp_port: Optional[int] = Field(None, description="SMTP порт")
    smtp_user: Optional[str] = Field(None, description="SMTP пользователь")
    smtp_from_email: Optional[str] = Field(None, description="Email отправителя")
    smtp_from_name: Optional[str] = Field(None, description="Имя отправителя")
    smtp_use_tls: bool = Field(True, description="Использовать TLS")
    email_notifications_enabled: bool = Field(True, description="Глобально включены ли email уведомления")

    class Config:
        from_attributes = True


class NotificationSettingsUpdate(BaseModel):
    """Данные для обновления настроек SMTP"""
    smtp_host: Optional[str] = Field(None, description="SMTP хост")
    smtp_port: Optional[int] = Field(None, description="SMTP порт")
    smtp_user: Optional[str] = Field(None, description="SMTP пользователь")
    smtp_password: Optional[str] = Field(None, description="SMTP пароль")
    smtp_from_email: Optional[str] = Field(None, description="Email отправителя")
    smtp_from_name: Optional[str] = Field(None, description="Имя отправителя")
    smtp_use_tls: Optional[bool] = Field(None, description="Использовать TLS")
    email_notifications_enabled: Optional[bool] = Field(None, description="Глобально включены ли email уведомления")


class NotificationSettingsTestRequest(BaseModel):
    """Запрос для тестирования SMTP настроек"""
    test_email: str = Field(..., description="Email для тестового письма")
