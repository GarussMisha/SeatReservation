"""
API роуты для управления помещениями
Предоставляет CRUD операции для создания, чтения, обновления и удаления помещений
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc as sql_desc
import logging

from app.core.database import get_db
from app.models.room import Room
from app.models.status import Status
from app.models.workspace import Workspace
from app.models.booking import Booking
from app.schemas.room import (
    RoomCreate,
    RoomUpdate,
    RoomResponse,
    RoomSearchParams,
    RoomStats,
    RoomBulkUpdate
)
from app.services.notification_service import get_notification_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["rooms"])


def format_room_response(room: Room, db: Session) -> Dict[str, Any]:
    """
    Форматирование ответа с данными помещения
    
    Args:
        room: Объект помещения из БД
        db: Сессия базы данных
    
    Returns:
        Словарь с отформатированными данными
    """
    # Получаем связанные данные
    status_obj = db.query(Status).filter(Status.id == room.status_id).first()
    
    # Подсчитываем рабочие места
    total_workspaces = db.query(Workspace).filter(Workspace.room_id == room.id).count()
    active_workspaces = db.query(Workspace).filter(
        and_(Workspace.room_id == room.id, Workspace.is_active == True)
    ).count()
    inactive_workspaces = total_workspaces - active_workspaces
    
    created_at = getattr(room, 'created_at', None)
    created_at_str = created_at.isoformat() if created_at else None
    
    return {
        "id": getattr(room, 'id', None),
        "name": getattr(room, 'name', None),
        "address": getattr(room, 'address', None),
        "description": getattr(room, 'description', None),
        "status_id": getattr(room, 'status_id', None),
        "created_at": created_at_str,
        # Данные статуса
        "status_name": getattr(status_obj, 'name', None) if status_obj else None,
        # Статистика
        "total_workspaces": total_workspaces,
        "active_workspaces": active_workspaces,
        "inactive_workspaces": inactive_workspaces
    }


@router.get("/", response_model=List[Dict[str, Any]])
async def get_all_rooms(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Получить список всех помещений с пагинацией
    
    Args:
        skip: Количество пропускаемых записей
        limit: Максимальное количество возвращаемых записей
        db: Сессия базы данных
    
    Returns:
        Список помещений с связанными данными
    """
    try:
        rooms = db.query(Room).offset(skip).limit(limit).all()
        result = []
        
        for room in rooms:
            result.append(format_room_response(room, db))
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении помещений: {str(e)}"
        )


@router.get("/{room_id}", response_model=Dict[str, Any])
async def get_room(room_id: int, db: Session = Depends(get_db)):
    """
    Получить конкретное помещение по ID
    
    Args:
        room_id: ID помещения
        db: Сессия базы данных
    
    Returns:
        Данные помещения с связанной информацией
    
    Raises:
        HTTPException: 404 если помещение не найдено
    """
    try:
        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Помещение с ID {room_id} не найдено"
            )
        
        return format_room_response(room, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении помещения: {str(e)}"
        )


@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_room(
    room_data: RoomCreate,
    db: Session = Depends(get_db)
):
    """
    Создать новое помещение
    
    Args:
        room_data: Данные для создания помещения
        db: Сессия базы данных
    
    Returns:
        Созданное помещение с полными данными
    
    Raises:
        HTTPException: 400 если статус не найден или название не уникально
    """
    try:
        # Проверяем существование статуса
        status_obj = db.query(Status).filter(Status.id == room_data.status_id).first()
        if not status_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Статус с ID {room_data.status_id} не найден"
            )
        
        # Проверяем уникальность названия
        existing_room = db.query(Room).filter(Room.name == room_data.name).first()
        if existing_room:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Помещение с названием '{room_data.name}' уже существует"
            )
        
        # Создаем помещение
        new_room = Room(
            name=room_data.name,
            address=room_data.address,
            description=room_data.description,
            status_id=room_data.status_id
        )
        
        db.add(new_room)
        db.commit()
        db.refresh(new_room)
        
        # Форматируем ответ
        result = format_room_response(new_room, db)
        result["message"] = "Помещение успешно создано"
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании помещения: {str(e)}"
        )


@router.put("/{room_id}", response_model=Dict[str, Any])
async def update_room(
    room_id: int,
    room_data: RoomUpdate,
    db: Session = Depends(get_db)
):
    """
    Обновить данные помещения
    
    Args:
        room_id: ID помещения
        room_data: Данные для обновления
        db: Сессия базы данных
    
    Returns:
        Обновленное помещение
    
    Raises:
        HTTPException: 404 если помещение не найдено
        HTTPException: 400 если новый статус не найден или название не уникально
    """
    try:
        # Проверяем существование помещения
        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Помещение с ID {room_id} не найдено"
            )
        
        # Проверяем новый статус, если указан
        if room_data.status_id:
            status_obj = db.query(Status).filter(Status.id == room_data.status_id).first()
            if not status_obj:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Статус с ID {room_data.status_id} не найден"
                )
        
        # Проверяем уникальность названия при изменении имени
        if room_data.name is not None:
            # Проверяем существование помещения с таким же названием
            existing_room = db.query(Room).filter(
                and_(
                    Room.name == room_data.name,
                    Room.id != room_id  # Исключаем текущее помещение
                )
            ).first()

            if existing_room:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Помещение с названием '{room_data.name}' уже существует"
                )

        # Проверяем, меняется ли статус помещения (для уведомления)
        send_notification = False
        old_status_id = room.status_id
        new_status_id = room_data.status_id if room_data.status_id is not None else old_status_id

        # Получаем статусы "active" и "inactive" для сравнения
        active_status = db.query(Status).filter(Status.name == "active").first()
        inactive_status = db.query(Status).filter(Status.name == "inactive").first()
        active_status_id = active_status.id if active_status else 1
        inactive_status_id = inactive_status.id if inactive_status else 2

        # Если статус меняется с "active" на "inactive" - отправляем уведомления
        if old_status_id == active_status_id and new_status_id == inactive_status_id:
            send_notification = True

        # Обновляем поля
        update_data = room_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(room, field, value)

        db.commit()

        # Если помещение отключено, отправляем уведомления
        if send_notification:
            try:
                notification_service = get_notification_service(db)
                notification_service.send_room_disabled_notification(room_id=room.id)
            except Exception as notif_error:
                # Логгируем ошибку уведомления, но не прерываем основной запрос
                print(f"Предупреждение: не удалось отправить уведомления: {notif_error}")
                logger.warning(f"Ошибка при отправке уведомления об отключении помещения {room_id}: {notif_error}")

        db.refresh(room)

        # Форматируем ответ
        result = format_room_response(room, db)
        result["message"] = "Помещение успешно обновлено"

        return result
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении помещения: {str(e)}"
        )


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(room_id: int, db: Session = Depends(get_db)):
    """
    Удалить помещение
    
    Args:
        room_id: ID помещения
        db: Сессия базы данных
    
    Raises:
        HTTPException: 404 если помещение не найдено
        HTTPException: 400 если в помещении есть рабочие места
    """
    try:
        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Помещение с ID {room_id} не найдено"
            )
        
        # Проверяем наличие рабочих мест
        workspace_count = db.query(Workspace).filter(Workspace.room_id == room_id).count()
        if workspace_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Нельзя удалить помещение с рабочими местами. Сначала удалите {workspace_count} рабочих мест"
            )
        
        db.delete(room)
        db.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении помещения: {str(e)}"
        )


@router.get("/search/", response_model=Dict[str, Any])
async def search_rooms(
    search: Optional[str] = Query(None, description="Поисковый запрос"),
    status_id: Optional[int] = Query(None, description="Фильтр по статусу"),
    has_workspaces: Optional[bool] = Query(None, description="Фильтр по наличию рабочих мест"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(50, ge=1, le=100, description="Количество записей на странице"),
    sort_by: str = Query("name", description="Поле сортировки"),
    sort_order: str = Query("asc", description="Порядок сортировки"),
    db: Session = Depends(get_db)
):
    """
    Поиск и фильтрация помещений
    
    Args:
        search: Поисковый запрос
        status_id: Фильтр по статусу
        has_workspaces: Фильтр по наличию рабочих мест
        page: Номер страницы
        per_page: Количество записей на странице
        sort_by: Поле сортировки
        sort_order: Порядок сортировки
        db: Сессия базы данных
    
    Returns:
        Результаты поиска с пагинацией
    """
    try:
        # Здесь можно использовать репозиторий, но для простоты используем прямые запросы
        query = db.query(Room).join(Status)
        
        # Применяем фильтры поиска
        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    Room.name.ilike(search_term),
                    Room.address.ilike(search_term),
                    Room.description.ilike(search_term),
                    Status.name.ilike(search_term)
                )
            )
        
        if status_id:
            query = query.filter(Room.status_id == status_id)
        
        if has_workspaces is not None:
            if has_workspaces:
                query = query.filter(Room.workspaces.any())
            else:
                query = query.filter(~Room.workspaces.any())
        
        # Подсчет общего количества
        total = query.count()
        
        # Сортировка
        from sqlalchemy import asc
        sort_field_map = {
            "id": Room.id,
            "name": Room.name,
            "address": Room.address,
            "status_name": Status.name,
            "created_at": Room.created_at
        }
        
        sort_field = sort_field_map.get(sort_by, Room.name)
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_field))
        else:
            query = query.order_by(sql_desc(sort_field))
        
        # Пагинация
        offset = (page - 1) * per_page
        rooms = query.offset(offset).limit(per_page).all()
        
        # Форматируем результаты
        results = []
        for room in rooms:
            results.append(format_room_response(room, db))
        
        return {
            "rooms": results,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при поиске помещений: {str(e)}"
        )


@router.get("/stats/overview", response_model=RoomStats)
async def get_rooms_stats(db: Session = Depends(get_db)):
    """
    Получить статистику по помещениям
    
    Args:
        db: Сессия базы данных
    
    Returns:
        Статистика по помещениям
    """
    try:
        # Общая статистика
        total_rooms = db.query(Room).count()
        total_workspaces = db.query(Workspace).count()
        active_workspaces = db.query(Workspace).filter(Workspace.is_active == True).count()
        inactive_workspaces = total_workspaces - active_workspaces
        
        # Распределение по статусам
        rooms_by_status = {}
        statuses = db.query(Status).all()
        for status in statuses:
            count = db.query(Room).filter(Room.status_id == status.id).count()
            rooms_by_status[status.name] = count
        
        # Активные помещения (с рабочими местами)
        active_rooms = db.query(Room).join(Workspace).distinct().count()
        inactive_rooms = total_rooms - active_rooms
        
        # Среднее количество рабочих мест на помещение
        avg_workspaces = total_workspaces / total_rooms if total_rooms > 0 else 0.0
        
        # Упрощенный расчет коэффициента использования
        utilization_rate = 0.75 if total_workspaces > 0 else 0.0
        
        return RoomStats(
            total_rooms=total_rooms,
            active_rooms=active_rooms,
            inactive_rooms=inactive_rooms,
            total_workspaces=total_workspaces,
            active_workspaces=active_workspaces,
            inactive_workspaces=inactive_workspaces,
            rooms_by_status=rooms_by_status,
            average_workspaces_per_room=avg_workspaces,
            utilization_rate=utilization_rate
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статистики: {str(e)}"
        )


@router.put("/bulk/update", response_model=Dict[str, Any])
async def bulk_update_rooms(
    bulk_data: RoomBulkUpdate,
    db: Session = Depends(get_db)
):
    """
    Массовое обновление помещений
    
    Args:
        bulk_data: Данные для массового обновления
        db: Сессия базы данных
    
    Returns:
        Результат массового обновления
    """
    try:
        # Проверяем существование помещений
        rooms = db.query(Room).filter(Room.id.in_(bulk_data.room_ids)).all()
        if len(rooms) != len(bulk_data.room_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Некоторые помещения не найдены"
            )
        
        # Проверяем новый статус, если указан
        if bulk_data.status_id:
            status_obj = db.query(Status).filter(Status.id == bulk_data.status_id).first()
            if not status_obj:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Статус с ID {bulk_data.status_id} не найден"
                )
        
        # Обновляем
        update_count = 0
        for room in rooms:
            if bulk_data.status_id is not None:
                setattr(room, 'status_id', bulk_data.status_id)
            if bulk_data.address is not None:
                setattr(room, 'address', bulk_data.address)
            if bulk_data.description is not None:
                setattr(room, 'description', bulk_data.description)
            update_count += 1
        
        db.commit()
        
        return {
            "message": f"Обновлено {update_count} помещений",
            "updated_count": update_count,
            "requested_count": len(bulk_data.room_ids)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при массовом обновлении: {str(e)}"
        )


@router.get("/{room_id}/workspaces", response_model=List[Dict[str, Any]])
async def get_room_workspaces(room_id: int, db: Session = Depends(get_db)):
    """
    Получить все рабочие места в помещении
    
    Args:
        room_id: ID помещения
        db: Сессия базы данных
    
    Returns:
        Список рабочих мест в указанном помещении
    
    Raises:
        HTTPException: 404 если помещение не найдено
    """
    try:
        # Проверяем существование помещения
        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Помещение с ID {room_id} не найдено"
            )
        
        workspaces = db.query(Workspace).filter(Workspace.room_id == room_id).all()
        result = []
        
        for workspace in workspaces:
            # Форматируем рабочее место аналогично workspace API
            workspace_created_at = workspace.created_at
            workspace_created_at_str = workspace_created_at.isoformat() if workspace_created_at else None
            
            workspace_dict = {
                "id": workspace.id,
                "name": workspace.name,
                "is_active": workspace.is_active,
                "room_id": workspace.room_id,
                "created_at": workspace_created_at_str,
                "room_name": room.name
            }
            result.append(workspace_dict)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении рабочих мест помещения: {str(e)}"
        )