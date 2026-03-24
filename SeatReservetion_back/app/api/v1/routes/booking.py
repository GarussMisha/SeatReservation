"""
API роуты для управления бронированиями
Предоставляет CRUD операции для создания, чтения, обновления и удаления бронирований рабочих мест
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, datetime

from app.core.database import get_db
from app.models.booking import Booking
from app.models.account import Account
from app.models.workspace import Workspace
from app.models.status import Status
from app.schemas.booking import (
    BookingCreate,
    BookingUpdate,
    BookingResponse,
    BookingSearchParams,
    BookingStats
)
from app.services.notification_service import get_notification_service

router = APIRouter(tags=["bookings"])


def format_booking_response(booking: Booking, db: Session) -> Dict[str, Any]:
    """
    Форматирование ответа с данными бронирования
    
    Args:
        booking: Объект бронирования из БД
        db: Сессия базы данных
    
    Returns:
        Словарь с отформатированными данными
    """
    # Получаем связанные данные
    account = db.query(Account).filter(Account.id == booking.account_id).first()
    workspace = db.query(Workspace).filter(Workspace.id == booking.workspace_id).first()
    status_obj = db.query(Status).filter(Status.id == booking.status_id).first()
    
    # Получаем связанные данные рабочего места
    room_name = None
    room_address = None
    if workspace:
        from app.models.room import Room
        room = db.query(Room).filter(Room.id == workspace.room_id).first()
        room_name = getattr(room, 'name', None) if room else None
        room_address = getattr(room, 'address', None) if room else None
    
    # Получаем данные пользователя напрямую из account
    account_first_name = getattr(account, 'first_name', None) if account else None
    account_last_name = getattr(account, 'last_name', None) if account else None
    account_email = getattr(account, 'email', None) if account else None
    
    return {
        "id": getattr(booking, 'id', None),
        "booking_date": getattr(booking, 'booking_date', None).isoformat() if booking.booking_date is not None else None,
        "status_id": getattr(booking, 'status_id', None),
        "account_id": getattr(booking, 'account_id', None),
        "workspace_id": getattr(booking, 'workspace_id', None),
        "created_at": getattr(booking, 'created_at', None).isoformat() if booking.created_at is not None else None,
        # Данные пользователя
        "account_login": getattr(account, 'login', None) if account else None,
        "account_first_name": account_first_name,
        "account_last_name": account_last_name,
        "account_email": account_email,
        # Данные рабочего места
        "workspace_name": getattr(workspace, 'name', None) if workspace else None,
        "workspace_room_name": room_name,
        "workspace_room_address": room_address,
        # Данные статуса
        "status_name": getattr(status_obj, 'name', None) if status_obj else None,
        "status_description": getattr(status_obj, 'description', None) if status_obj else None
    }


@router.get("/", response_model=List[Dict[str, Any]])
async def get_all_bookings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Получить список всех бронирований с пагинацией
    
    Args:
        skip: Количество пропускаемых записей
        limit: Максимальное количество возвращаемых записей
        db: Сессия базы данных
    
    Returns:
        Список бронирований с связанными данными
    """
    try:
        bookings = db.query(Booking).offset(skip).limit(limit).all()
        result = []
        
        for booking in bookings:
            result.append(format_booking_response(booking, db))
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении бронирований: {str(e)}"
        )


@router.get("/{booking_id}", response_model=Dict[str, Any])
async def get_booking(booking_id: int, db: Session = Depends(get_db)):
    """
    Получить конкретное бронирование по ID
    
    Args:
        booking_id: ID бронирования
        db: Сессия базы данных
    
    Returns:
        Данные бронирования с связанной информацией
    
    Raises:
        HTTPException: 404 если бронирование не найдено
    """
    try:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Бронирование с ID {booking_id} не найдено"
            )
        
        return format_booking_response(booking, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении бронирования: {str(e)}"
        )


@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db)
):
    """
    Создать новое бронирование
    
    Args:
        booking_data: Данные для создания бронирования
        db: Сессия базы данных
    
    Returns:
        Созданное бронирование с полными данными
    
    Raises:
        HTTPException: 400 если пользователь, рабочее место или статус не найдены
        HTTPException: 409 если рабочее место уже забронировано на эту дату
    """
    try:
        # Проверяем существование аккаунта
        account = db.query(Account).filter(Account.id == booking_data.account_id).first()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Пользователь с ID {booking_data.account_id} не найден"
            )
        
        # Проверяем существование рабочего места
        workspace = db.query(Workspace).filter(Workspace.id == booking_data.workspace_id).first()
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Рабочее место с ID {booking_data.workspace_id} не найдено"
            )
        
        # Проверяем, что рабочее место активно
        if not getattr(workspace, 'is_active', True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Рабочее место '{workspace.name}' не активно и не может быть забронировано"
            )
        
        # Проверяем существование статуса
        status_obj = db.query(Status).filter(Status.id == booking_data.status_id).first()
        if not status_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Статус с ID {booking_data.status_id} не найден"
            )
        
        # Проверяем, что у пользователя нет других бронирований на эту дату (исключая отмененные)
        from sqlalchemy import not_
        
        # Формируем запрос для проверки существующих бронирований пользователя на эту дату
        user_bookings_query = db.query(Booking).filter(
            Booking.account_id == booking_data.account_id,
            Booking.booking_date == booking_data.booking_date
        )
        
        # Получаем статус "cancelled" для исключения отмененных бронирований
        cancelled_status = db.query(Status).filter(Status.name == "cancelled").first()
        if cancelled_status:
            user_bookings_query = user_bookings_query.filter(Booking.status_id != cancelled_status.id)
        
        existing_user_booking = user_bookings_query.first()
        if existing_user_booking:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"У вас уже есть бронирование на {booking_data.booking_date}. Один пользователь может забронировать только одно рабочее место в день."
            )
        
        # Проверяем, что рабочее место не забронировано на эту дату (исключая отмененные)
        workspace_bookings_query = db.query(Booking).filter(
            Booking.workspace_id == booking_data.workspace_id,
            Booking.booking_date == booking_data.booking_date
        )
        
        if cancelled_status:
            workspace_bookings_query = workspace_bookings_query.filter(Booking.status_id != cancelled_status.id)
        
        existing_workspace_booking = workspace_bookings_query.first()
        if existing_workspace_booking:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Рабочее место уже забронировано на {booking_data.booking_date}"
            )
        
        # Создаем бронирование
        new_booking = Booking(
            booking_date=booking_data.booking_date,
            status_id=booking_data.status_id,
            account_id=booking_data.account_id,
            workspace_id=booking_data.workspace_id
        )
        
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)
        
        # Форматируем ответ
        result = format_booking_response(new_booking, db)
        result["message"] = "Бронирование успешно создано"
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании бронирования: {str(e)}"
        )


@router.put("/{booking_id}", response_model=Dict[str, Any])
async def update_booking(
    booking_id: int,
    booking_data: BookingUpdate,
    db: Session = Depends(get_db)
):
    """
    Обновить данные бронирования
    
    Args:
        booking_id: ID бронирования
        booking_data: Данные для обновления
        db: Сессия базы данных
    
    Returns:
        Обновленное бронирование
    
    Raises:
        HTTPException: 404 если бронирование не найдено
        HTTPException: 409 если конфликт с существующим бронированием
    """
    try:
        # Проверяем существование бронирования
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Бронирование с ID {booking_id} не найдено"
            )
        
        # Проверяем новый статус, если указан
        if booking_data.status_id:
            status_obj = db.query(Status).filter(Status.id == booking_data.status_id).first()
            if not status_obj:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Статус с ID {booking_data.status_id} не найден"
                )
        
        # Если меняется рабочее место, проверяем что новое место активно
        if booking_data.workspace_id and booking_data.workspace_id != booking.workspace_id:
            workspace = db.query(Workspace).filter(Workspace.id == booking_data.workspace_id).first()
            if not workspace:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Рабочее место с ID {booking_data.workspace_id} не найдено"
                )
            
            if getattr(workspace, 'is_active', True) == False:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Рабочее место '{workspace.name}' не активно и не может быть забронировано"
                )
        
        # Проверяем конфликт при изменении даты (исключая отмененные)
        if booking_data.booking_date and booking_data.booking_date != booking.booking_date:
            from sqlalchemy import not_
            
            # Проверяем, что у пользователя нет других бронирований на новую дату (исключая отмененные)
            user_bookings_query = db.query(Booking).filter(
                Booking.account_id == booking.account_id,
                Booking.booking_date == booking_data.booking_date,
                Booking.id != booking_id
            )
            
            cancelled_status = db.query(Status).filter(Status.name == "cancelled").first()
            if cancelled_status:
                user_bookings_query = user_bookings_query.filter(Booking.status_id != cancelled_status.id)
            
            existing_user_booking = user_bookings_query.first()
            if existing_user_booking:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"У вас уже есть бронирование на {booking_data.booking_date}. Один пользователь может забронировать только одно рабочее место в день."
                )
            
            # Проверяем, что рабочее место не забронировано на новую дату (исключая отмененные)
            # Определяем ID рабочего места для проверки
            workspace_id_to_check = booking_data.workspace_id if booking_data.workspace_id else booking.workspace_id
            workspace_bookings_query = db.query(Booking).filter(
                Booking.workspace_id == workspace_id_to_check,
                Booking.booking_date == booking_data.booking_date,
                Booking.id != booking_id
            )
            
            if cancelled_status:
                workspace_bookings_query = workspace_bookings_query.filter(Booking.status_id != cancelled_status.id)
            
            existing_workspace_booking = workspace_bookings_query.first()
            if existing_workspace_booking:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Рабочее место уже забронировано на {booking_data.booking_date}"
                )
        
        # Обновляем поля
        update_data = booking_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(booking, field, value)
        
        db.commit()
        db.refresh(booking)
        
        # Форматируем ответ
        result = format_booking_response(booking, db)
        result["message"] = "Бронирование успешно обновлено"
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении бронирования: {str(e)}"
        )


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(booking_id: int, db: Session = Depends(get_db)):
    """
    Удалить бронирование
    
    Args:
        booking_id: ID бронирования
        db: Сессия базы данных
    
    Raises:
        HTTPException: 404 если бронирование не найдено
    """
    try:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Бронирование с ID {booking_id} не найдено"
            )
        
        db.delete(booking)
        db.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении бронирования: {str(e)}"
        )


@router.get("/workspace/{workspace_id}", response_model=List[Dict[str, Any]])
async def get_bookings_by_workspace(
    workspace_id: int,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Получить бронирования конкретного рабочего места
    
    Args:
        workspace_id: ID рабочего места
        date_from: Начальная дата (опционально)
        date_to: Конечная дата (опционально)
        db: Сессия базы данных
    
    Returns:
        Список бронирований рабочего места
    
    Raises:
        HTTPException: 404 если рабочее место не найдено
    """
    try:
        # Проверяем существование рабочего места
        workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Рабочее место с ID {workspace_id} не найдено"
            )
        
        # Формируем запрос
        query = db.query(Booking).filter(Booking.workspace_id == workspace_id)
        
        if date_from:
            query = query.filter(Booking.booking_date >= date_from)
        if date_to:
            query = query.filter(Booking.booking_date <= date_to)
        
        bookings = query.all()
        result = []
        
        for booking in bookings:
            result.append(format_booking_response(booking, db))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении бронирований рабочего места: {str(e)}"
        )


@router.get("/account/{account_id}", response_model=List[Dict[str, Any]])
async def get_bookings_by_account(
    account_id: int,
    include_past: bool = False,
    db: Session = Depends(get_db)
):
    """
    Получить бронирования конкретного пользователя
    
    Args:
        account_id: ID пользователя
        include_past: Включать прошедшие бронирования
        db: Сессия базы данных
    
    Returns:
        Список бронирований пользователя
    
    Raises:
        HTTPException: 404 если пользователь не найден
    """
    try:
        # Проверяем существование пользователя
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пользователь с ID {account_id} не найден"
            )
        
        # Формируем запрос
        query = db.query(Booking).filter(Booking.account_id == account_id)
        
        if not include_past:
            query = query.filter(Booking.booking_date >= date.today())
        
        bookings = query.order_by(Booking.booking_date).all()
        result = []
        
        for booking in bookings:
            result.append(format_booking_response(booking, db))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении бронирований пользователя: {str(e)}"
        )


@router.get("/date/{booking_date}", response_model=List[Dict[str, Any]])
async def get_bookings_by_date(
    booking_date: date,
    exclude_cancelled: bool = True,
    db: Session = Depends(get_db)
):
    """
    Получить все бронирования на конкретную дату
    
    Args:
        booking_date: Дата для поиска бронирований
        exclude_cancelled: Исключать ли отмененные бронирования (по умолчанию да)
        db: Сессия базы данных
    
    Returns:
        Список бронирований на указанную дату
    """
    try:
        # Формируем базовый запрос
        query = db.query(Booking).filter(Booking.booking_date == booking_date)
        
        # Если exclude_cancelled=True, исключаем отмененные бронирования
        if exclude_cancelled:
            cancelled_status = db.query(Status).filter(Status.name == "cancelled").first()
            if cancelled_status:
                query = query.filter(Booking.status_id != cancelled_status.id)
        
        bookings = query.all()
        result = []
        
        for booking in bookings:
            result.append(format_booking_response(booking, db))
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении бронирований на дату: {str(e)}"
        )


@router.get("/stats/overview", response_model=BookingStats)
async def get_bookings_stats(db: Session = Depends(get_db)):
    """
    Получить статистику по бронированиям
    
    Args:
        db: Сессия базы данных
    
    Returns:
        Статистика по бронированиям
    """
    try:
        today = date.today()
        
        # Общая статистика
        total_bookings = db.query(Booking).count()
        upcoming_bookings = db.query(Booking).filter(Booking.booking_date > today).count()
        today_bookings = db.query(Booking).filter(Booking.booking_date == today).count()
        past_bookings = db.query(Booking).filter(Booking.booking_date < today).count()
        
        # Отмененные бронирования
        cancelled_status = db.query(Status).filter(Status.name == "cancelled").first()
        cancelled_bookings = 0
        if cancelled_status:
            cancelled_bookings = db.query(Booking).filter(Booking.status_id == cancelled_status.id).count()
        
        # Распределение по статусам
        bookings_by_status = {}
        all_statuses = db.query(Status).all()
        for status_obj in all_statuses:
            count = db.query(Booking).filter(Booking.status_id == status_obj.id).count()
            bookings_by_status[status_obj.name] = count
        
        # Распределение по рабочим местам
        bookings_by_workspace = {}
        workspaces = db.query(Workspace).all()
        for workspace in workspaces:
            count = db.query(Booking).filter(Booking.workspace_id == workspace.id).count()
            bookings_by_workspace[workspace.name] = count
        
        # Коэффициент использования
        total_workspaces = db.query(Workspace).count()
        utilization_rate = 0.0
        if total_workspaces > 0:
            utilization_rate = min(today_bookings / total_workspaces, 1.0)
        
        return BookingStats(
            total_bookings=total_bookings,
            upcoming_bookings=upcoming_bookings,
            today_bookings=today_bookings,
            past_bookings=past_bookings,
            cancelled_bookings=cancelled_bookings,
            bookings_by_status=bookings_by_status,
            bookings_by_workspace=bookings_by_workspace,
            utilization_rate=utilization_rate
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статистики: {str(e)}"
        )


@router.post("/{booking_id}/cancel", response_model=Dict[str, Any])
async def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    """
    Отменить бронирование
    
    Args:
        booking_id: ID бронирования
        db: Сессия базы данных
    
    Returns:
        Обновленное бронирование с отмененным статусом
    
    Raises:
        HTTPException: 404 если бронирование не найдено
    """
    try:
        # Проверяем существование бронирования
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Бронирование с ID {booking_id} не найдено"
            )
        
        # Получаем статус "cancelled"
        cancelled_status = db.query(Status).filter(Status.name == "cancelled").first()
        if not cancelled_status:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Статус 'cancelled' не найден в базе данных"
            )
        
        # Изменяем статус бронирования на "отменено"
        booking.status_id = cancelled_status.id
        db.commit()
        
        # Отправляем уведомление пользователю
        try:
            notification_service = get_notification_service(db)
            notification_service.send_booking_cancelled_notification(booking_id=booking.id)
        except Exception as notif_error:
            # Логгируем ошибку уведомления, но не прерываем основной запрос
            print(f"Предупреждение: не удалось отправить уведомление об отмене: {notif_error}")
        
        db.refresh(booking)

        # Форматируем ответ
        result = format_booking_response(booking, db)
        result["message"] = "Бронирование успешно отменено"

        return result
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при отмене бронирования: {str(e)}"
        )