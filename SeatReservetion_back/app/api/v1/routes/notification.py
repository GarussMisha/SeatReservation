"""
API роуты для управления уведомлениями
Предоставляет endpoints для создания, чтения и управления уведомлениями пользователей
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_admin_user
from app.models.account import Account
from app.models.notification import Notification
from app.models.status import Status
from app.schemas.notification import (
    NotificationScheduleCreate,
    NotificationResponse,
    NotificationListResponse,
    NotificationStats,
    NotificationBulkSendRequest,
    NotificationFilter,
)
from app.services.notification_service import NotificationService, get_notification_service

router = APIRouter(tags=["notifications"])


def format_notification_response(notification: Notification) -> Dict[str, Any]:
    """
    Форматирование ответа с данными уведомления

    Args:
        notification: Объект уведомления из БД

    Returns:
        Словарь с отформатированными данными
    """
    from datetime import timezone
    
    return {
        "id": notification.id,
        "notification_type": notification.notification_type,
        "subject": notification.subject,
        "message": notification.message,
        "scheduled_at": notification.scheduled_at.replace(tzinfo=timezone.utc).isoformat() if notification.scheduled_at else None,
        "sent_at": notification.sent_at.replace(tzinfo=timezone.utc).isoformat() if notification.sent_at else None,
        "created_at": notification.created_at.replace(tzinfo=timezone.utc).isoformat() if notification.created_at else None,
        "status_id": notification.status_id,
        "status_name": notification.status.name if notification.status else None,
        "user_id": notification.user_id,
        "created_by_id": notification.created_by_id,
        "recipient_name": f"{notification.user.first_name} {notification.user.last_name}" if notification.user else None,
        "creator_name": f"{notification.creator.first_name} {notification.creator.last_name}" if notification.creator else None,
    }


@router.get("/my", response_model=Dict[str, Any])
async def get_my_notifications(
    current_user: Account = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100, description="Лимит записей"),
    skip: int = Query(0, ge=0, description="Пропуск записей")
):
    """
    Получить мои уведомления

    Args:
        current_user: Текущий пользователь
        db: Сессия базы данных
        limit: Лимит записей
        skip: Пропуск записей

    Returns:
        Список уведомлений пользователя
    """
    try:
        notification_service = get_notification_service(db)
        notifications = notification_service.get_user_notifications(
            user_id=current_user.id,
            limit=limit,
            skip=skip
        )

        total = db.query(Notification).filter(Notification.user_id == current_user.id).count()

        return {
            "notifications": notifications,
            "total": total,
            "page": (skip // limit) + 1,
            "per_page": limit
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении уведомлений: {str(e)}"
        )


@router.get("/", response_model=Dict[str, Any])
async def get_all_notifications(
    current_user: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    notification_type: Optional[str] = Query(None, description="Тип уведомления"),
    status_id: Optional[int] = Query(None, description="ID статуса"),
    user_id: Optional[int] = Query(None, description="ID пользователя"),
    limit: int = Query(100, ge=1, le=200, description="Лимит записей"),
    skip: int = Query(0, ge=0, description="Пропуск записей")
):
    """
    Получить все уведомления (только для админов)

    Args:
        current_user: Текущий администратор
        db: Сессия базы данных
        notification_type: Фильтр по типу
        status_id: Фильтр по статусу
        user_id: Фильтр по пользователю
        limit: Лимит записей
        skip: Пропуск записей

    Returns:
        Список всех уведомлений с фильтрацией
    """
    try:
        query = db.query(Notification)

        # Применяем фильтры
        if notification_type:
            query = query.filter(Notification.notification_type == notification_type)
        if status_id:
            query = query.filter(Notification.status_id == status_id)
        if user_id:
            query = query.filter(Notification.user_id == user_id)

        total = query.count()
        notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

        result = [format_notification_response(n) for n in notifications]

        return {
            "notifications": result,
            "total": total,
            "page": (skip // limit) + 1,
            "per_page": limit
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении уведомлений: {str(e)}"
        )


@router.get("/{notification_id}", response_model=Dict[str, Any])
async def get_notification(
    notification_id: int,
    current_user: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Получить уведомление по ID (только для админов)

    Args:
        notification_id: ID уведомления
        current_user: Текущий администратор
        db: Сессия базы данных

    Returns:
        Данные уведомления
    """
    try:
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Уведомление с ID {notification_id} не найдено"
            )

        return format_notification_response(notification)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении уведомления: {str(e)}"
        )


@router.post("/schedule", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def schedule_notification(
    notification_data: NotificationScheduleCreate,
    current_user: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Запланировать рассылку уведомлений (только для админов)

    Args:
        notification_data: Данные для создания рассылки
        current_user: Текущий администратор
        db: Сессия базы данных

    Returns:
        Результат создания рассылки
    """
    try:
        # Проверяем, что все пользователи существуют
        users = db.query(Account).filter(Account.id.in_(notification_data.user_ids)).all()
        if len(users) != len(notification_data.user_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Некоторые пользователи не найдены"
            )

        # Проверяем, что время в будущем
        if notification_data.scheduled_at <= datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Время отправки должно быть в будущем"
            )

        # Создаем рассылку
        notification_service = get_notification_service(db)
        result = notification_service.create_scheduled_notification(
            user_ids=notification_data.user_ids,
            subject=notification_data.subject,
            message=notification_data.message,
            scheduled_at=notification_data.scheduled_at,
            created_by_id=current_user.id
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )

        return {
            "message": result["message"],
            "notifications_created": result["notifications_created"],
            "notification_ids": result["notification_ids"],
            "scheduled_at": notification_data.scheduled_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании рассылки: {str(e)}"
        )


@router.post("/bulk-send", response_model=Dict[str, Any])
async def bulk_send_notifications(
    bulk_data: NotificationBulkSendRequest,
    current_user: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Массовая отправка уведомлений (только для админов)

    Args:
        bulk_data: Данные для массовой отправки
        current_user: Текущий администратор
        db: Сессия базы данных

    Returns:
        Результат отправки
    """
    try:
        # Проверяем, что все пользователи существуют
        users = db.query(Account).filter(Account.id.in_(bulk_data.user_ids)).all()
        if len(users) != len(bulk_data.user_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Некоторые пользователи не найдены"
            )

        notification_service = get_notification_service(db)

        if bulk_data.send_now:
            # Отправляем немедленно
            result = notification_service.create_scheduled_notification(
                user_ids=bulk_data.user_ids,
                subject=bulk_data.subject,
                message=bulk_data.message,
                scheduled_at=datetime.utcnow(),
                created_by_id=current_user.id
            )
        else:
            # Планируем отложенную отправку
            if not bulk_data.scheduled_at:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Необходимо указать scheduled_at для отложенной отправки"
                )

            result = notification_service.create_scheduled_notification(
                user_ids=bulk_data.user_ids,
                subject=bulk_data.subject,
                message=bulk_data.message,
                scheduled_at=bulk_data.scheduled_at,
                created_by_id=current_user.id
            )

        return {
            "message": result["message"],
            "notifications_created": result["notifications_created"],
            "notification_ids": result["notification_ids"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при массовой отправке: {str(e)}"
        )


@router.post("/{notification_id}/resend", response_model=Dict[str, Any])
async def resend_notification(
    notification_id: int,
    current_user: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Повторная отправка уведомления (только для админов)

    Args:
        notification_id: ID уведомления
        current_user: Текущий администратор
        db: Сессия базы данных

    Returns:
        Результат повторной отправки
    """
    try:
        from app.services.email_service import email_service

        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Уведомление с ID {notification_id} не найдено"
            )

        user = db.query(Account).filter(Account.id == notification.user_id).first()
        if not user or not user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="У пользователя нет email для отправки"
            )

        # Отправляем email
        email_result = email_service.send_email(
            to_email=user.email,
            subject=notification.subject,
            html_content=notification.message
        )

        if email_result["success"]:
            # Обновляем статус
            sent_status = db.query(Status).filter(Status.name == "sent").first()
            if sent_status:
                notification.status_id = sent_status.id
                notification.sent_at = datetime.utcnow()
                db.commit()

            return {
                "message": "Уведомление успешно отправлено повторно",
                "sent_at": notification.sent_at.isoformat() if notification.sent_at else None
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка отправки: {email_result['message']}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при повторной отправке: {str(e)}"
        )


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_notification(
    notification_id: int,
    current_user: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Отменить уведомление (только для админов)

    Args:
        notification_id: ID уведомления
        current_user: Текущий администратор
        db: Сессия базы данных

    Raises:
        HTTPException: 404 если уведомление не найдено
        HTTPException: 400 если уведомление уже отправлено
    """
    try:
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Уведомление с ID {notification_id} не найдено"
            )

        # Проверяем, что уведомление еще не отправлено
        sent_status = db.query(Status).filter(Status.name == "sent").first()
        if notification.status_id == sent_status.id if sent_status else False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя отменить уже отправленное уведомление"
            )

        # Обновляем статус на cancelled
        cancelled_status = db.query(Status).filter(Status.name == "cancelled").first()
        if not cancelled_status:
            cancelled_status = Status(name="cancelled", description="Отменено")
            db.add(cancelled_status)
            db.commit()
            db.refresh(cancelled_status)

        notification.status_id = cancelled_status.id
        db.commit()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при отмене уведомления: {str(e)}"
        )


@router.get("/stats/overview", response_model=Dict[str, Any])
async def get_notifications_stats(
    current_user: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Получить статистику по уведомлениям (только для админов)

    Args:
        current_user: Текущий администратор
        db: Сессия базы данных

    Returns:
        Статистика по уведомлениям
    """
    try:
        # Общая статистика
        total_notifications = db.query(Notification).count()

        # Получаем статусы
        pending_status = db.query(Status).filter(Status.name == "pending").first()
        sent_status = db.query(Status).filter(Status.name == "sent").first()
        failed_status = db.query(Status).filter(Status.name == "failed").first()

        pending_count = 0
        sent_count = 0
        failed_count = 0
        scheduled_count = 0

        if pending_status:
            pending_count = db.query(Notification).filter(Notification.status_id == pending_status.id).count()
            #Scheduled (pending но с будущим временем)
            now = datetime.utcnow()
            scheduled_count = db.query(Notification).filter(
                Notification.status_id == pending_status.id,
                Notification.scheduled_at > now
            ).count()

        if sent_status:
            sent_count = db.query(Notification).filter(Notification.status_id == sent_status.id).count()

        if failed_status:
            failed_count = db.query(Notification).filter(Notification.status_id == failed_status.id).count()

        # Статистика по типам
        notifications_by_type = {}
        types = db.query(Notification.notification_type).distinct().all()
        for (notif_type,) in types:
            count = db.query(Notification).filter(Notification.notification_type == notif_type).count()
            notifications_by_type[notif_type] = count

        return {
            "total_notifications": total_notifications,
            "pending_notifications": pending_count,
            "sent_notifications": sent_count,
            "failed_notifications": failed_count,
            "scheduled_notifications": scheduled_count,
            "notifications_by_type": notifications_by_type
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статистики: {str(e)}"
        )


@router.post("/send-pending", response_model=Dict[str, Any])
async def send_pending_notifications_endpoint(
    current_user: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Отправить все ожидающие уведомления (только для админов)
    Ручной запуск отправки запланированных уведомлений

    Args:
        current_user: Текущий администратор
        db: Сессия базы данных

    Returns:
        Результат отправки
    """
    try:
        notification_service = get_notification_service(db)
        result = notification_service.send_pending_notifications()

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при отправке уведомлений: {str(e)}"
        )
