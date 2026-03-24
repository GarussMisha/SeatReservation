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

            # Добавляем задачу проверки отложенных уведомлений
            self.scheduler.add_job(
                func=self._send_pending_notifications_task,
                trigger=IntervalTrigger(minutes=check_interval_minutes),
                id='send_pending_notifications',
                name='Отправка отложенных уведомлений',
                replace_existing=True,
                misfire_grace_time=60  # Допустимая задержка выполнения (секунды)
            )

            # Запускаем планировщик
            self.scheduler.start()
            self._is_running = True

            logger.info(f"Планировщик запущен. Проверка уведомлений каждые {check_interval_minutes} мин.")

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
