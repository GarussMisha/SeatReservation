"""
Notification Service - сервис управления уведомлениями пользователей
Обрабатывает создание, планирование и отправку уведомлений
"""
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import logging
import json

from app.models.notification import Notification
from app.models.account import Account
from app.models.booking import Booking
from app.models.workspace import Workspace
from app.models.room import Room
from app.models.status import Status
from app.services.notification_templates import (
    get_booking_cancelled_data,
    get_workspace_disabled_data,
    get_room_disabled_data,
    get_booking_reminder_data,
    create_booking_cancelled_html,
    create_workspace_disabled_html,
    create_room_disabled_html,
    create_booking_reminder_html
)

logger = logging.getLogger(__name__)


class NotificationService:
    """Сервис для управления уведомлениями пользователей"""

    # Типы уведомлений
    TYPE_BOOKING_CANCELLED = "booking_cancelled"
    TYPE_WORKSPACE_DISABLED = "workspace_disabled"
    TYPE_ROOM_DISABLED = "room_disabled"
    TYPE_CUSTOM = "custom"
    TYPE_BOOKING_REMINDER = "booking_reminder"

    def __init__(self, db: Session):
        self.db = db
        from app.services.email_service import email_service
        self.email_service = email_service

    def _get_status_by_name(self, name: str) -> Optional[Status]:
        """Получение статуса по названию"""
        return self.db.query(Status).filter(Status.name == name).first()

    def _get_or_create_pending_status(self) -> Status:
        """Получить или создать статус 'pending'"""
        pending_status = self._get_status_by_name("pending")
        if not pending_status:
            pending_status = Status(name="pending", description="Ожидает отправки")
            self.db.add(pending_status)
            self.db.commit()
            self.db.refresh(pending_status)
        return pending_status

    def _get_user_name(self, user: Account) -> str:
        """Получение имени пользователя для отображения"""
        return f"{user.first_name} {user.last_name}"

    def send_booking_cancelled_notification(self, booking_id: int, reason: str = "Ручная отмена") -> Dict[str, Any]:
        """
        Отправка уведомления об отмене бронирования

        Args:
            booking_id: ID бронирования
            reason: Причина отмены

        Returns:
            Результат отправки
        """
        result = {
            "success": False,
            "message": "",
            "notification_id": None,
            "email_sent": False
        }

        try:
            # Получаем бронирование
            booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
            if not booking:
                result["message"] = f"Бронирование {booking_id} не найдено"
                return result

            # Получаем связанные данные
            user = self.db.query(Account).filter(Account.id == booking.account_id).first()
            workspace = self.db.query(Workspace).filter(Workspace.id == booking.workspace_id).first()
            room = self.db.query(Room).filter(Room.id == workspace.room_id).first() if workspace else None

            if not user or not workspace or not room:
                result["message"] = "Недостаточно данных для отправки уведомления"
                return result

            if not user.email:
                result["message"] = "У пользователя нет email"
                logger.warning(f"У пользователя {user.id} нет email для уведомления")
                return result

            # Получаем статус "pending"
            pending_status = self._get_or_create_pending_status()

            # Создаем данные для frontend (JSON)
            notification_data = get_booking_cancelled_data(
                user_name=self._get_user_name(user),
                workspace_name=workspace.name,
                room_address=room.address or "Не указан",
                booking_date=booking.booking_date.isoformat() if booking.booking_date else "Н/Д",
                reason=reason
            )

            # Создаем HTML для email
            html_content = create_booking_cancelled_html(
                user_name=self._get_user_name(user),
                workspace_name=workspace.name,
                room_address=room.address or "Не указан",
                booking_date=booking.booking_date.isoformat() if booking.booking_date else "Н/Д",
                reason=reason
            )

            subject = f"Бронирование отменено: {workspace.name}"

            # Создаем уведомление (сохраняем JSON в БД)
            notification = Notification(
                notification_type=self.TYPE_BOOKING_CANCELLED,
                subject=subject,
                message=json.dumps(notification_data, ensure_ascii=False),  # JSON вместо HTML
                scheduled_at=None,
                status_id=pending_status.id,
                user_id=user.id,
                created_by_id=None
            )

            self.db.add(notification)
            self.db.commit()
            self.db.refresh(notification)

            result["notification_id"] = notification.id

            # Отправляем email
            email_result = self.email_service.send_email(
                to_email=user.email,
                subject=subject,
                html_content=html_content
            )

            if email_result["success"]:
                result["email_sent"] = True
                sent_status = self._get_status_by_name("sent")
                if sent_status:
                    notification.status_id = sent_status.id
                    notification.sent_at = datetime.now()
                    self.db.commit()

            result["success"] = True
            result["message"] = "Уведомление обработано"
            logger.info(f"Уведомление об отмене бронирования {booking_id} отправлено пользователю {user.id}")

        except Exception as e:
            self.db.rollback()
            result["message"] = f"Ошибка: {str(e)}"
            logger.error(f"Ошибка при отправке уведомления об отмене бронирования: {e}")

        return result

    def send_booking_reminder_notification(self, booking_id: int) -> Dict[str, Any]:
        """
        Отправка напоминания о предстоящем бронировании

        Args:
            booking_id: ID бронирования

        Returns:
            Результат отправки
        """
        result = {
            "success": False,
            "message": "",
            "notification_id": None,
            "email_sent": False
        }

        try:
            # Получаем бронирование
            booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
            if not booking:
                result["message"] = f"Бронирование {booking_id} не найдено"
                return result

            # Получаем связанные данные
            user = self.db.query(Account).filter(Account.id == booking.account_id).first()
            workspace = self.db.query(Workspace).filter(Workspace.id == booking.workspace_id).first()
            room = self.db.query(Room).filter(Room.id == workspace.room_id).first() if workspace else None

            if not user or not workspace or not room:
                result["message"] = "Недостаточно данных для отправки уведомления"
                return result

            if not user.email:
                result["message"] = "У пользователя нет email"
                logger.warning(f"У пользователя {user.id} нет email для напоминания")
                return result

            # Получаем статус "pending"
            pending_status = self._get_or_create_pending_status()

            # Создаем HTML письмо
            html_content = self.email_service.create_booking_reminder_html(
                user_name=self._get_user_name(user),
                workspace_name=workspace.name,
                room_name=room.name,
                room_address=room.address or "Не указан",
                booking_date=booking.booking_date.isoformat() if booking.booking_date else "Н/Д"
            )

            subject = f"Напоминание: бронирование на {booking.booking_date}"

            # Создаем уведомление
            notification = Notification(
                notification_type="booking_reminder",
                subject=subject,
                message=html_content,
                scheduled_at=None,
                status_id=pending_status.id,
                user_id=user.id,
                created_by_id=None
            )

            self.db.add(notification)
            self.db.commit()
            self.db.refresh(notification)

            result["notification_id"] = notification.id

            # Отправляем email
            email_result = self.email_service.send_email(
                to_email=user.email,
                subject=subject,
                html_content=html_content
            )

            if email_result["success"]:
                result["email_sent"] = True
                sent_status = self._get_status_by_name("sent")
                if sent_status:
                    notification.status_id = sent_status.id
                    notification.sent_at = datetime.now()
                    self.db.commit()

            result["success"] = True
            result["message"] = "Напоминание отправлено"
            logger.info(f"Напоминание о бронировании {booking_id} отправлено пользователю {user.id}")

        except Exception as e:
            self.db.rollback()
            result["message"] = f"Ошибка: {str(e)}"
            logger.error(f"Ошибка при отправке напоминания: {e}")

        return result

    def send_workspace_disabled_notification(
        self,
        workspace_id: int,
        affected_booking_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Отправка уведомлений при отключении рабочего места

        Args:
            workspace_id: ID рабочего места
            affected_booking_ids: Список ID затронутых бронирований (если None, будут найдены автоматически)

        Returns:
            Результат отправки
        """
        result = {
            "success": False,
            "message": "",
            "workspace_id": workspace_id,
            "notifications_sent": 0,
            "notifications_failed": 0,
            "details": []
        }

        try:
            # Получаем рабочее место
            workspace = self.db.query(Workspace).filter(Workspace.id == workspace_id).first()
            if not workspace:
                result["message"] = f"Рабочее место {workspace_id} не найдено"
                return result

            room = self.db.query(Room).filter(Room.id == workspace.room_id).first()

            # Находим все активные бронирования этого места
            if affected_booking_ids:
                bookings = self.db.query(Booking).filter(
                    Booking.id.in_(affected_booking_ids)
                ).all()
            else:
                # Получаем статус "cancelled" чтобы исключить отмененные
                cancelled_status = self._get_status_by_name("cancelled")
                cancelled_status_id = cancelled_status.id if cancelled_status else None

                query = self.db.query(Booking).filter(
                    Booking.workspace_id == workspace_id
                )
                if cancelled_status_id:
                    query = query.filter(Booking.status_id != cancelled_status_id)
                bookings = query.all()

            if not bookings:
                result["success"] = True
                result["message"] = "Нет активных бронирований для уведомления"
                return result

            # Отправляем уведомления всем пользователям
            for booking in bookings:
                user = self.db.query(Account).filter(Account.id == booking.account_id).first()
                if not user or not user.email:
                    result["notifications_failed"] += 1
                    result["details"].append({
                        "booking_id": booking.id,
                        "user_id": user.id if user else None,
                        "success": False,
                        "reason": "Нет email"
                    })
                    continue

                # Создаем HTML письмо
                html_content = self.email_service.create_workspace_disabled_html(
                    user_name=self._get_user_name(user),
                    workspace_name=workspace.name,
                    room_name=room.name if room else "Н/Д",
                    room_address=room.address if room else "Не указан",
                    booking_date=booking.booking_date.isoformat() if booking.booking_date else "Н/Д"
                )

                subject = f"Рабочее место недоступно: {workspace.name} на {booking.booking_date}"

                # Получаем статус "pending"
                pending_status = self._get_status_by_name("pending")
                if not pending_status:
                    pending_status = Status(name="pending", description="Ожидает отправки")
                    self.db.add(pending_status)
                    self.db.commit()
                    self.db.refresh(pending_status)

                # Создаем уведомление
                notification = Notification(
                    notification_type=self.TYPE_WORKSPACE_DISABLED,
                    subject=subject,
                    message=html_content,
                    scheduled_at=None,
                    status_id=pending_status.id,
                    user_id=user.id,
                    created_by_id=None
                )

                self.db.add(notification)
                self.db.commit()
                self.db.refresh(notification)

                # Отправляем email
                email_result = self.email_service.send_email(
                    to_email=user.email,
                    subject=subject,
                    html_content=html_content
                )

                if email_result["success"]:
                    result["notifications_sent"] += 1
                    # Обновляем статус
                    sent_status = self._get_status_by_name("sent")
                    if sent_status:
                        notification.status_id = sent_status.id
                        notification.sent_at = datetime.now()
                        self.db.commit()

                    result["details"].append({
                        "booking_id": booking.id,
                        "user_id": user.id,
                        "notification_id": notification.id,
                        "success": True
                    })
                else:
                    result["notifications_failed"] += 1
                    failed_status = self._get_status_by_name("failed")
                    if failed_status:
                        notification.status_id = failed_status.id
                        self.db.commit()

                    result["details"].append({
                        "booking_id": booking.id,
                        "user_id": user.id,
                        "notification_id": notification.id,
                        "success": False,
                        "reason": email_result["message"]
                    })

            result["success"] = True
            result["message"] = f"Обработано уведомлений: {result['notifications_sent'] + result['notifications_failed']}"
            logger.info(f"Уведомления об отключении рабочего места {workspace_id}: отправлено={result['notifications_sent']}, неудачно={result['notifications_failed']}")

        except Exception as e:
            self.db.rollback()
            result["message"] = f"Ошибка: {str(e)}"
            logger.error(f"Ошибка при отправке уведомлений об отключении рабочего места: {e}")

        return result

    def send_room_disabled_notification(
        self,
        room_id: int,
        affected_booking_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Отправка уведомлений при отключении помещения

        Args:
            room_id: ID помещения
            affected_booking_ids: Список ID затронутых бронирований

        Returns:
            Результат отправки
        """
        result = {
            "success": False,
            "message": "",
            "room_id": room_id,
            "notifications_sent": 0,
            "notifications_failed": 0,
            "details": []
        }

        try:
            # Получаем помещение
            room = self.db.query(Room).filter(Room.id == room_id).first()
            if not room:
                result["message"] = f"Помещение {room_id} не найдено"
                return result

            # Находим все рабочие места в помещении
            workspaces = self.db.query(Workspace).filter(Workspace.room_id == room_id).all()
            workspace_ids = [ws.id for ws in workspaces]

            if not workspace_ids:
                result["success"] = True
                result["message"] = "В помещении нет рабочих мест"
                return result

            # Находим все активные бронирования
            if affected_booking_ids:
                bookings = self.db.query(Booking).filter(
                    Booking.id.in_(affected_booking_ids)
                ).all()
            else:
                cancelled_status = self._get_status_by_name("cancelled")
                cancelled_status_id = cancelled_status.id if cancelled_status else None

                query = self.db.query(Booking).filter(
                    Booking.workspace_id.in_(workspace_ids)
                )
                if cancelled_status_id:
                    query = query.filter(Booking.status_id != cancelled_status_id)
                bookings = query.all()

            if not bookings:
                result["success"] = True
                result["message"] = "Нет активных бронирований для уведомления"
                return result

            # Группируем бронирования по пользователям
            user_bookings: Dict[int, List[Booking]] = {}
            for booking in bookings:
                if booking.account_id not in user_bookings:
                    user_bookings[booking.account_id] = []
                user_bookings[booking.account_id].append(booking)

            # Отправляем уведомления каждому пользователю
            for user_id, user_booking_list in user_bookings.items():
                user = self.db.query(Account).filter(Account.id == user_id).first()
                if not user or not user.email:
                    result["notifications_failed"] += 1
                    result["details"].append({
                        "user_id": user_id,
                        "success": False,
                        "reason": "Нет email"
                    })
                    continue

                # Формируем список затронутых бронирований
                affected_bookings = []
                for b in user_booking_list:
                    ws = self.db.query(Workspace).filter(Workspace.id == b.workspace_id).first()
                    affected_bookings.append({
                        "workspace_name": ws.name if ws else "Н/Д",
                        "booking_date": b.booking_date.isoformat() if b.booking_date else "Н/Д"
                    })

                # Создаем HTML письмо
                html_content = self.email_service.create_room_disabled_html(
                    user_name=self._get_user_name(user),
                    room_name=room.name,
                    room_address=room.address or "Не указан",
                    affected_bookings=affected_bookings
                )

                subject = f"Помещение недоступно: {room.name}"

                # Получаем статус "pending"
                pending_status = self._get_status_by_name("pending")
                if not pending_status:
                    pending_status = Status(name="pending", description="Ожидает отправки")
                    self.db.add(pending_status)
                    self.db.commit()
                    self.db.refresh(pending_status)

                # Создаем уведомление
                notification = Notification(
                    notification_type=self.TYPE_ROOM_DISABLED,
                    subject=subject,
                    message=html_content,
                    scheduled_at=None,
                    status_id=pending_status.id,
                    user_id=user.id,
                    created_by_id=None
                )

                self.db.add(notification)
                self.db.commit()
                self.db.refresh(notification)

                # Отправляем email
                email_result = self.email_service.send_email(
                    to_email=user.email,
                    subject=subject,
                    html_content=html_content
                )

                if email_result["success"]:
                    result["notifications_sent"] += 1
                    sent_status = self._get_status_by_name("sent")
                    if sent_status:
                        notification.status_id = sent_status.id
                        notification.sent_at = datetime.now()
                        self.db.commit()

                    result["details"].append({
                        "user_id": user.id,
                        "notification_id": notification.id,
                        "success": True
                    })
                else:
                    result["notifications_failed"] += 1
                    failed_status = self._get_status_by_name("failed")
                    if failed_status:
                        notification.status_id = failed_status.id
                        self.db.commit()

                    result["details"].append({
                        "user_id": user.id,
                        "notification_id": notification.id,
                        "success": False,
                        "reason": email_result["message"]
                    })

            result["success"] = True
            result["message"] = f"Обработано уведомлений: {result['notifications_sent'] + result['notifications_failed']}"
            logger.info(f"Уведомления об отключении помещения {room_id}: отправлено={result['notifications_sent']}, неудачно={result['notifications_failed']}")

        except Exception as e:
            self.db.rollback()
            result["message"] = f"Ошибка: {str(e)}"
            logger.error(f"Ошибка при отправке уведомлений об отключении помещения: {e}")

        return result

    def create_scheduled_notification(
        self,
        user_ids: List[int],
        subject: str,
        message: str,
        scheduled_at: datetime,
        created_by_id: int
    ) -> Dict[str, Any]:
        """
        Создание отложенного уведомления (рассылки)

        Args:
            user_ids: Список ID пользователей
            subject: Тема сообщения
            message: Текст сообщения
            scheduled_at: Время отправки
            created_by_id: ID создателя (админ)

        Returns:
            Результат создания
        """
        result = {
            "success": False,
            "message": "",
            "notifications_created": 0,
            "notification_ids": []
        }

        try:
            # Получаем статус "pending"
            pending_status = self._get_status_by_name("pending")
            if not pending_status:
                pending_status = Status(name="pending", description="Ожидает отправки")
                self.db.add(pending_status)
                self.db.commit()
                self.db.refresh(pending_status)

            # Создаем уведомление для каждого пользователя
            for user_id in user_ids:
                user = self.db.query(Account).filter(Account.id == user_id).first()
                if not user:
                    continue

                # Создаем HTML для кастомного уведомления
                html_content = self.email_service.create_custom_notification_html(
                    user_name=self._get_user_name(user) if user else "Пользователь",
                    subject=subject,
                    message=message,
                    sender_name="Администратор"
                )

                notification = Notification(
                    notification_type=self.TYPE_CUSTOM,
                    subject=subject,
                    message=html_content,
                    scheduled_at=scheduled_at,
                    status_id=pending_status.id,
                    user_id=user.id,
                    created_by_id=created_by_id
                )

                self.db.add(notification)
                result["notifications_created"] += 1
                result["notification_ids"].append(notification.id)

            self.db.commit()

            result["success"] = True
            result["message"] = f"Создано {result['notifications_created']} отложенных уведомлений"
            logger.info(f"Создана рассылка: {result['notifications_created']} уведомлений на {scheduled_at}")

        except Exception as e:
            self.db.rollback()
            result["message"] = f"Ошибка: {str(e)}"
            logger.error(f"Ошибка при создании отложенной рассылки: {e}")

        return result

    def send_pending_notifications(self) -> Dict[str, Any]:
        """
        Отправка всех запланированных уведомлений, время которых пришло

        Returns:
            Результат отправки
        """
        result = {
            "success": True,
            "message": "",
            "processed": 0,
            "sent": 0,
            "failed": 0,
            "skipped": 0
        }

        try:
            now = datetime.now()

            # Получаем статусы
            pending_status = self._get_status_by_name("pending")
            sent_status = self._get_status_by_name("sent")
            failed_status = self._get_status_by_name("failed")

            if not pending_status:
                result["message"] = "Статус 'pending' не найден"
                return result

            # Находим уведомления, которые нужно отправить
            notifications = self.db.query(Notification).filter(
                Notification.status_id == pending_status.id,
                Notification.scheduled_at <= now
            ).all()

            result["processed"] = len(notifications)

            for notification in notifications:
                user = self.db.query(Account).filter(Account.id == notification.user_id).first()

                if not user or not user.email:
                    result["skipped"] += 1
                    if failed_status:
                        notification.status_id = failed_status.id
                    self.db.commit()
                    continue

                # Отправляем email
                email_result = self.email_service.send_email(
                    to_email=user.email,
                    subject=notification.subject,
                    html_content=notification.message
                )

                if email_result["success"]:
                    result["sent"] += 1
                    if sent_status:
                        notification.status_id = sent_status.id
                        notification.sent_at = now
                else:
                    result["failed"] += 1
                    if failed_status:
                        notification.status_id = failed_status.id

                self.db.commit()

            result["message"] = f"Обработано: {result['processed']}, отправлено: {result['sent']}, ошибок: {result['failed']}, пропущено: {result['skipped']}"
            logger.info(f"Отправка отложенных уведомлений: {result['message']}")

        except Exception as e:
            self.db.rollback()
            result["success"] = False
            result["message"] = f"Ошибка: {str(e)}"
            logger.error(f"Ошибка при отправке отложенных уведомлений: {e}")

        return result

    def get_user_notifications(
        self,
        user_id: int,
        limit: int = 50,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Получение уведомлений пользователя

        Args:
            user_id: ID пользователя
            limit: Лимит записей
            skip: Пропуск записей

        Returns:
            Список уведомлений
        """
        notifications = self.db.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

        result = []
        for notif in notifications:
            result.append({
                "id": notif.id,
                "type": notif.notification_type,
                "subject": notif.subject,
                "message": notif.message,
                "scheduled_at": notif.scheduled_at.isoformat() if notif.scheduled_at else None,
                "sent_at": notif.sent_at.isoformat() if notif.sent_at else None,
                "created_at": notif.created_at.isoformat() if notif.created_at else None,
                "status_name": notif.status.name if notif.status else None
            })

        return result


# Функция для создания сервиса
def get_notification_service(db: Session) -> NotificationService:
    """Фабричная функция для создания сервиса уведомлений"""
    return NotificationService(db)


__all__ = ["NotificationService", "get_notification_service"]
