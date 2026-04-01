"""
Scheduler Service - сервис для фоновой отправки отложенных уведомлений
Использует APScheduler для периодического запуска задач
"""
import logging
from datetime import datetime
from typing import Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class SchedulerService:
    """Сервис для планирования фоновых задач"""

    def __init__(self):
        self.scheduler: Optional[BackgroundScheduler] = None
        self._is_running = False

    def start(self, check_interval_minutes: int = 5):
        """
        Запуск планировщика задач

        Args:
            check_interval_minutes: Интервал проверки отложенных уведомлений (в минутах)
        """
        if self._is_running:
            logger.warning("Планировщик уже запущен")
            return

        try:
            self.scheduler = BackgroundScheduler()

            # Задача 1: Проверка pending уведомлений (каждые 5 минут)
            self.scheduler.add_job(
                func=self._send_pending_notifications_task,
                trigger=IntervalTrigger(minutes=check_interval_minutes),
                id='send_pending_notifications',
                name='Отправка отложенных уведомлений',
                replace_existing=True,
                misfire_grace_time=60  # Допустимая задержка выполнения (секунды)
            )

            # Задача 2: Напоминания о бронированиях (каждый час)
            # Отправляет напоминания за 6 часов до начала бронирования (в 18:00 за 00:00)
            self.scheduler.add_job(
                func=self._send_booking_reminders_task,
                trigger=IntervalTrigger(hours=1),
                id='send_booking_reminders',
                name='Напоминания о бронированиях',
                replace_existing=True,
                misfire_grace_time=300
            )

            # Запускаем планировщик
            self.scheduler.start()
            self._is_running = True

            logger.info(f"Планировщик запущен. Проверка уведомлений каждые {check_interval_minutes} мин.")
            logger.info("Напоминания о бронированиях проверяются каждый час (17:00-23:00)")

        except Exception as e:
            logger.error(f"Ошибка при запуске планировщика: {e}")
            self._is_running = False

    def stop(self):
        """Остановка планировщика"""
        if self.scheduler and self._is_running:
            try:
                self.scheduler.shutdown(wait=True)
                self._is_running = False
                logger.info("Планировщик остановлен")
            except Exception as e:
                logger.error(f"Ошибка при остановке планировщика: {e}")

    def _send_pending_notifications_task(self):
        """
        Задача для отправки отложенных уведомлений
        Вызывается планировщиком периодически
        """
        logger.debug("Запуск задачи проверки отложенных уведомлений")

        db: Session = SessionLocal()
        try:
            notification_service = NotificationService(db)
            result = notification_service.send_pending_notifications()

            logger.info(
                f"Отправка отложенных уведомлений завершена: "
                f"обработано={result.get('processed', 0)}, "
                f"отправлено={result.get('sent', 0)}, "
                f"ошибок={result.get('failed', 0)}, "
                f"пропущено={result.get('skipped', 0)}"
            )

        except Exception as e:
            logger.error(f"Ошибка в задаче отправки уведомлений: {e}")
        finally:
            db.close()

    def _send_booking_reminders_task(self):
        """
        Проверка бронирований и отправка напоминаний за 6 часов до начала
        Вызывается планировщиком каждый час
        Напоминание отправляется в 18:00 за 6 часов до начала бронирования (00:00 следующего дня)
        """
        logger.debug("Запуск задачи проверки напоминаний о бронированиях")

        db: Session = SessionLocal()
        try:
            from app.models.booking import Booking
            from app.models.status import BookingStatuses
            from app.services.notification_service import NotificationService
            from datetime import timedelta, time
            
            # Текущее время (локальное время сервера)
            now = datetime.now()

            # Находим все CONFIRMED бронирования на завтра
            # Напоминание отправляется сегодня в 18:00 за 6 часов до начала (00:00 завтра)
            tomorrow = (now + timedelta(days=1)).date()

            # Проверяем, что сейчас между 17:00 и 23:00 (время для напоминаний на завтра)
            current_hour = now.hour
            if current_hour < 17 or current_hour > 23:
                logger.debug(f"Сейчас {current_hour}:00 - не время для напоминаний (ждем 17:00-23:00)")
                return
            
            bookings = db.query(Booking).filter(
                Booking.booking_date == tomorrow,
                Booking.status_id == BookingStatuses.CONFIRMED
            ).all()
            
            if not bookings:
                logger.debug("Нет подтвержденных бронирований на завтра")
                return

            reminders_sent = 0
            reminders_failed = 0
            
            for booking in bookings:
                # Проверяем, не отправляли ли уже напоминание сегодня
                already_reminded = db.query(Notification).filter(
                    Notification.user_id == booking.account_id,
                    Notification.notification_type == "booking_reminder",
                    Notification.created_at >= now - timedelta(hours=24)
                ).first()
                
                if already_reminded:
                    logger.debug(f"Напоминание уже отправлено для booking {booking.id}")
                    continue
                
                # Отправляем напоминание
                notification_service = NotificationService(db)
                result = notification_service.send_booking_reminder_notification(
                    booking_id=booking.id
                )
                
                if result["success"]:
                    reminders_sent += 1
                    logger.info(f"Напоминание отправлено для booking {booking.id}")
                else:
                    reminders_failed += 1
                    logger.warning(f"Не удалось отправить напоминание для booking {booking.id}: {result['message']}")
            
            logger.info(
                f"Напоминания о бронированиях: "
                f"всего={len(bookings)}, отправлено={reminders_sent}, "
                f"ошибок={reminders_failed}"
            )

        except Exception as e:
            logger.error(f"Ошибка в задаче напоминаний: {e}")
        finally:
            db.close()

    def is_running(self) -> bool:
        """Проверка, запущен ли планировщик"""
        return self._is_running


# Singleton экземпляр сервиса
scheduler_service = SchedulerService()


def start_notification_scheduler(check_interval_minutes: int = 5):
    """
    Функция для запуска планировщика уведомлений

    Args:
        check_interval_minutes: Интервал проверки в минутах
    """
    scheduler_service.start(check_interval_minutes)


def stop_notification_scheduler():
    """Функция для остановки планировщика"""
    scheduler_service.stop()


__all__ = [
    "SchedulerService",
    "scheduler_service",
    "start_notification_scheduler",
    "stop_notification_scheduler",
]
