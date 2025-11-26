"""
API эндпоинты для синхронизации статусов бронирований
"""

from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.database import SessionLocal
from app.services.booking_status_sync import BookingStatusSyncService
from app.schemas.account import CurrentUserResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/bookings/status", summary="Принудительная синхронизация статусов бронирований")
def sync_booking_statuses(
    batch_size: int = 100,
    db: Session = Depends(get_db),
    current_user: CurrentUserResponse = Depends(get_current_user)
):
    """
    Принудительная синхронизация статусов просроченных бронирований.
    
    Автоматически переводит бронирования с прошедшей датой в статус "completed".
    
    Args:
        batch_size: Размер батча для обработки (по умолчанию 100)
        
    Returns:
        Результат синхронизации с статистикой
    """
    try:
        with BookingStatusSyncService(db) as service:
            results = service.sync_expired_bookings(batch_size)
            
        return {
            "success": True,
            "message": "Синхронизация статусов бронирований выполнена",
            "timestamp": datetime.now().isoformat(),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Ошибка при синхронизации статусов: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при синхронизации: {str(e)}"
        )


@router.get("/bookings/status", summary="Получить статистику синхронизации")
def get_sync_status(
    db: Session = Depends(get_db),
    current_user: CurrentUserResponse = Depends(get_current_user)
):
    """
    Получение текущей статистики синхронизации статусов бронирований.
    
    Returns:
        Статистика по бронированиям и состоянию синхронизации
    """
    try:
        with BookingStatusSyncService(db) as service:
            stats = service.get_sync_stats()
            
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Ошибка при получении статистики синхронизации: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статистики: {str(e)}"
        )


@router.post("/bookings/{booking_id}/status", summary="Синхронизация статуса конкретного бронирования")
def sync_single_booking_status(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUserResponse = Depends(get_current_user)
):
    """
    Синхронизация статуса одного конкретного бронирования.
    
    Args:
        booking_id: ID бронирования для синхронизации
        
    Returns:
        Результат синхронизации конкретного бронирования
    """
    try:
        with BookingStatusSyncService(db) as service:
            result = service.sync_single_booking(booking_id)
            
        if result.get('error'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['error']
            )
            
        return {
            "success": True,
            "message": f"Статус бронирования ID={booking_id} синхронизирован",
            "timestamp": datetime.now().isoformat(),
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при синхронизации бронирования ID={booking_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при синхронизации бронирования: {str(e)}"
        )


@router.post("/test-connection", summary="Тест подключения к системе синхронизации")
def test_sync_connection(
    db: Session = Depends(get_db),
    current_user: CurrentUserResponse = Depends(get_current_user)
):
    """
    Тест подключения к системе синхронизации.
    Проверяет доступность всех необходимых статусов в базе данных.
    
    Returns:
        Информация о состоянии системы синхронизации
    """
    try:
        with BookingStatusSyncService(db) as service:
            # Простой тест - получаем статистику
            stats = service.get_sync_stats()
            
        return {
            "success": True,
            "message": "Система синхронизации работает корректно",
            "timestamp": datetime.now().isoformat(),
            "connection_status": "active",
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Ошибка при тестировании системы синхронизации: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка тестирования системы: {str(e)}"
        )


# Эндпоинт для автоматической синхронизации (без аутентификации для системных вызовов)
@router.post("/auto/bookings/status", summary="Автоматическая синхронизация (системный вызов)")
def auto_sync_booking_statuses(
    batch_size: int = 50,
    db: Session = Depends(get_db)
):
    """
    Автоматическая синхронизация статусов бронирований.
    Предназначен для вызова системными процессами (cron, планировщик задач).
    
    Args:
        batch_size: Размер батча для обработки (по умолчанию 50)
        
    Returns:
        Результат синхронизации с минимальной информацией
    """
    try:
        with BookingStatusSyncService(db) as service:
            results = service.sync_expired_bookings(batch_size)
            
        return {
            "success": True,
            "auto_sync": True,
            "timestamp": datetime.now().isoformat(),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Ошибка при автоматической синхронизации: {e}")
        return {
            "success": False,
            "auto_sync": True,
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }