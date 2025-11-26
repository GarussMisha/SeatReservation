"""
Сервис синхронизации статусов бронирований
Автоматически переводит просроченные бронирования в статус "completed"
"""

from datetime import datetime, date
from typing import List, Dict, Any, Optional
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models import Booking, Status
from app.repositories.booking_repository import BookingRepository
import logging

logger = logging.getLogger(__name__)


class BookingStatusSyncService:
    """Сервис для синхронизации статусов бронирований"""
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db or SessionLocal()
        self.booking_repo = BookingRepository(self.db)
        
    def close(self):
        """Закрытие сессии базы данных"""
        if self.db:
            self.db.close()
    
    def sync_expired_bookings(self, batch_size: int = 100) -> Dict[str, int]:
        """
        Синхронизация просроченных бронирований
        
        Args:
            batch_size: Размер батча для обработки
            
        Returns:
            Словарь с результатами синхронизации
        """
        results = {
            'processed': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        try:
            # Получаем статус "completed"
            completed_status = self.db.query(Status).filter(
                Status.name == 'completed'
            ).first()
            
            if not completed_status:
                logger.error("Статус 'completed' не найден в базе данных")
                return results
            
            today = date.today()
            
            # Получаем все бронирования, которые должны быть завершены
            expired_bookings = self.db.query(Booking).filter(
                and_(
                    Booking.booking_date < today,  # Дата бронирования прошла
                    Booking.status_id != completed_status.id,  # Еще не завершено
                    Booking.status_id != self._get_cancelled_status_id()  # И не отменено
                )
            ).limit(batch_size).all()
            
            logger.info(f"Найдено {len(expired_bookings)} просроченных бронирований для синхронизации")
            
            for booking in expired_bookings:
                try:
                    # Обновляем статус на "completed"
                    booking.status_id = completed_status.id
                    results['updated'] += 1
                    results['processed'] += 1
                    
                    logger.debug(
                        f"Обновлен статус бронирования ID={booking.id} "
                        f"с {booking.status.name} на completed"
                    )
                    
                except Exception as e:
                    logger.error(f"Ошибка при обновлении бронирования ID={booking.id}: {e}")
                    results['errors'] += 1
            
            # Коммитим изменения
            self.db.commit()
            
            logger.info(
                f"Синхронизация завершена: обновлено={results['updated']}, "
                f"пропущено={results['skipped']}, ошибки={results['errors']}"
            )
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Критическая ошибка при синхронизации: {e}")
            results['errors'] += 1
            
        return results
    
    def sync_single_booking(self, booking_id: int) -> Dict[str, Any]:
        """
        Синхронизация статуса одного бронирования
        
        Args:
            booking_id: ID бронирования
            
        Returns:
            Словарь с результатом операции
        """
        result = {
            'booking_id': booking_id,
            'status_updated': False,
            'old_status': None,
            'new_status': None,
            'error': None
        }
        
        try:
            # Используем join для получения всех данных одним запросом
            booking_with_status = self.db.query(Booking, Status).join(
                Status, Booking.status_id == Status.id
            ).filter(Booking.id == booking_id).first()
            
            if not booking_with_status:
                result['error'] = "Бронирование не найдено"
                return result
            
            booking, status = booking_with_status
            result['old_status'] = status.name
            
            today = date.today()
            
            # Проверяем, нужно ли обновить статус
            if booking.booking_date < today and status.name not in ['cancelled', 'completed']:
                completed_status = self.db.query(Status).filter(
                    Status.name == 'completed'
                ).first()
                
                if completed_status:
                    booking.status_id = completed_status.id
                    self.db.commit()
                    result['status_updated'] = True
                    result['new_status'] = 'completed'
                    
                    logger.info(
                        f"Автоматически обновлен статус бронирования ID={booking_id} "
                        f"с {result['old_status']} на completed"
                    )
                else:
                    result['error'] = "Статус 'completed' не найден"
            else:
                result['new_status'] = status.name
                
        except Exception as e:
            self.db.rollback()
            result['error'] = str(e)
            logger.error(f"Ошибка при синхронизации бронирования ID={booking_id}: {e}")
            
        return result
    
    def get_sync_stats(self) -> Dict[str, Any]:
        """
        Получение статистики синхронизации
        
        Returns:
            Словарь со статистикой
        """
        try:
            today = date.today()
            
            # Общее количество бронирований
            total_bookings = self.db.query(Booking).count()
            
            # Активные (еще не завершенные)
            active_bookings = self.db.query(Booking).join(Status).filter(
                and_(
                    Status.name.in_(['confirmed', 'pending']),
                    Booking.booking_date >= today
                )
            ).count()
            
            # Завершенные
            completed_bookings = self.db.query(Booking).join(Status).filter(
                Status.name == 'completed'
            ).count()
            
            # Отмененные
            cancelled_bookings = self.db.query(Booking).join(Status).filter(
                Status.name == 'cancelled'
            ).count()
            
            # Просроченные (должны быть завершены, но еще не переведены)
            expired_needing_sync = self.db.query(Booking).join(Status).filter(
                and_(
                    Booking.booking_date < today,
                    Status.name.in_(['confirmed', 'pending'])
                )
            ).count()
            
            return {
                'total_bookings': total_bookings,
                'active_bookings': active_bookings,
                'completed_bookings': completed_bookings,
                'cancelled_bookings': cancelled_bookings,
                'expired_needing_sync': expired_needing_sync,
                'last_sync_check': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Ошибка при получении статистики: {e}")
            return {'error': str(e)}
    
    def _get_cancelled_status_id(self) -> int:
        """Получение ID статуса 'cancelled'"""
        cancelled_status = self.db.query(Status).filter(
            Status.name == 'cancelled'
        ).first()
        
        if not cancelled_status:
            raise ValueError("Статус 'cancelled' не найден в базе данных")
            
        return cancelled_status.id
    
    def __enter__(self):
        """Поддержка контекстного менеджера"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Закрытие ресурсов при выходе из контекста"""
        self.close()


def sync_expired_bookings_batch(batch_size: int = 100) -> Dict[str, int]:
    """
    Функция для синхронизации просроченных бронирований (однократный запуск)
    
    Args:
        batch_size: Размер батча для обработки
        
    Returns:
        Словарь с результатами синхронизации
    """
    with BookingStatusSyncService() as service:
        return service.sync_expired_bookings(batch_size)


def sync_single_booking_by_id(booking_id: int) -> Dict[str, Any]:
    """
    Функция для синхронизации одного бронирования по ID
    
    Args:
        booking_id: ID бронирования
        
    Returns:
        Словарь с результатом операции
    """
    with BookingStatusSyncService() as service:
        return service.sync_single_booking(booking_id)


def get_booking_sync_stats() -> Dict[str, Any]:
    """
    Функция для получения статистики синхронизации
    
    Returns:
        Словарь со статистикой
    """
    with BookingStatusSyncService() as service:
        return service.get_sync_stats()