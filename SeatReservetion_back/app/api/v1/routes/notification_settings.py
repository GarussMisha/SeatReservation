"""
API роуты для управления настройками уведомлений
Предоставляет endpoints для получения и обновления настроек
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_admin_user
from app.models.account import Account
from app.models.user_notification_settings import UserNotificationSettings
from app.models.notification_settings import NotificationSettings
from app.schemas.notification_settings import (
    UserNotificationSettingsResponse,
    UserNotificationSettingsUpdate,
    NotificationSettingsResponse,
    NotificationSettingsUpdate,
    NotificationSettingsTestRequest
)
from app.services.email_service import EmailService

router = APIRouter(tags=["notification-settings"])


# =============================================================================
# НАСТРОЙКИ ПОЛЬЗОВАТЕЛЯ
# =============================================================================

@router.get("/my/settings", response_model=UserNotificationSettingsResponse)
async def get_my_notification_settings(
    current_user: Account = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить мои настройки уведомлений

    Args:
        current_user: Текущий пользователь
        db: Сессия базы данных

    Returns:
        Настройки уведомлений пользователя
    """
    try:
        # Получаем настройки пользователя
        settings = db.query(UserNotificationSettings).filter(
            UserNotificationSettings.user_id == current_user.id
        ).first()

        # Если настроек нет, создаём по умолчанию
        if not settings:
            settings = UserNotificationSettings(
                user_id=current_user.id,
                email_enabled=True,
                site_enabled=True
            )
            db.add(settings)
            db.commit()
            db.refresh(settings)

        return settings

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении настроек: {str(e)}"
        )


@router.put("/my/settings", response_model=UserNotificationSettingsResponse)
async def update_my_notification_settings(
    settings_data: UserNotificationSettingsUpdate,
    current_user: Account = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Обновить мои настройки уведомлений

    Args:
        settings_data: Данные для обновления
        current_user: Текущий пользователь
        db: Сессия базы данных

    Returns:
        Обновлённые настройки
    """
    try:
        # Получаем настройки пользователя
        settings = db.query(UserNotificationSettings).filter(
            UserNotificationSettings.user_id == current_user.id
        ).first()

        # Если настроек нет, создаём
        if not settings:
            settings = UserNotificationSettings(
                user_id=current_user.id,
                email_enabled=True,
                site_enabled=True
            )
            db.add(settings)

        # Обновляем поля
        if settings_data.email_enabled is not None:
            settings.email_enabled = settings_data.email_enabled
        if settings_data.site_enabled is not None:
            settings.site_enabled = settings_data.site_enabled

        db.commit()
        db.refresh(settings)

        return settings

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении настроек: {str(e)}"
        )


# =============================================================================
# ГЛОБАЛЬНЫЕ НАСТРОЙКИ (АДМИН)
# =============================================================================

@router.get("/admin/notification-settings", response_model=NotificationSettingsResponse)
async def get_notification_settings(
    current_user: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Получить глобальные настройки уведомлений (только для админа)

    Args:
        current_user: Текущий администратор
        db: Сессия базы данных

    Returns:
        Глобальные настройки уведомлений
    """
    try:
        # Получаем настройки
        settings = db.query(NotificationSettings).first()

        # Если настроек нет, возвращаем настройки по умолчанию
        if not settings:
            return NotificationSettingsResponse(
                id=0,
                smtp_host="smtp.resend.com",
                smtp_port=465,
                smtp_user="resend",
                smtp_from_email="onboarding@resend.dev",
                smtp_from_name="Seat Reservation System",
                smtp_use_tls=True,
                email_notifications_enabled=True
            )

        return settings

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении настроек: {str(e)}"
        )


@router.put("/admin/notification-settings", response_model=NotificationSettingsResponse)
async def update_notification_settings(
    settings_data: NotificationSettingsUpdate,
    current_user: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Обновить глобальные настройки уведомлений (только для админа)

    Args:
        settings_data: Данные для обновления
        current_user: Текущий администратор
        db: Сессия базы данных

    Returns:
        Обновлённые настройки
    """
    try:
        # Получаем настройки
        settings = db.query(NotificationSettings).first()

        # Если настроек нет, создаём
        if not settings:
            settings = NotificationSettings()
            db.add(settings)

        # Обновляем поля
        update_dict = settings_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(settings, field, value)

        db.commit()
        db.refresh(settings)

        return settings

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении настроек: {str(e)}"
        )


@router.post("/admin/notification-settings/test")
async def test_notification_settings(
    test_data: NotificationSettingsTestRequest,
    current_user: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Протестировать SMTP настройки отправкой тестового письма (только для админа)

    Args:
        test_data: Email для тестового письма
        current_user: Текущий администратор
        db: Сессия базы данных

    Returns:
        Результат тестирования
    """
    try:
        # Получаем текущие настройки
        settings = db.query(NotificationSettings).first()

        if not settings:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Настройки уведомлений не найдены"
            )

        # Создаем тестовый email сервис с текущими настройками
        email_service = EmailService()
        email_service.smtp_host = settings.smtp_host or "smtp.resend.com"
        email_service.smtp_port = settings.smtp_port or 465
        email_service.smtp_user = settings.smtp_user or "resend"
        email_service.smtp_password = settings.smtp_password or ""
        email_service.from_email = settings.smtp_from_email or "onboarding@resend.dev"
        email_service.from_name = settings.smtp_from_name or "Seat Reservation System"
        email_service.use_tls = settings.smtp_use_tls

        # Проверяем настройки
        if not email_service.is_configured():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SMTP не настроен. Проверьте настройки."
            )

        # Создаем тестовое HTML письмо
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #22c55e; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background-color: #f9f9f9; padding: 20px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Тестовое письмо</h1>
                </div>
                <div class="content">
                    <p>Здравствуйте!</p>
                    <p>Это тестовое письмо от системы уведомлений Seat Reservation.</p>
                    <p>Если вы получили это письмо, значит SMTP настройки работают корректно.</p>
                    <p>Время отправки: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                <div class="footer">
                    <p>Это автоматическое тестовое письмо.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Отправляем тестовое письмо
        result = email_service.send_email(
            to_email=test_data.test_email,
            subject="🧪 Тестовое письмо от Seat Reservation",
            html_content=html_content
        )

        if result["success"]:
            return {
                "success": True,
                "message": "Тестовое письмо успешно отправлено!",
                "sent_at": result["sent_at"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при отправке: {result['message']}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при тестировании: {str(e)}"
        )
