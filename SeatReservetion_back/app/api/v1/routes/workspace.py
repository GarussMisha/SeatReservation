"""
API роуты для управления рабочими местами
Предоставляет CRUD операции для создания, чтения, обновления и удаления рабочих мест
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date

from app.core.database import get_db
from app.models.workspace import Workspace
from app.models.room import Room
from app.models.status import Status
from app.schemas.workspace import (
    WorkspaceCreate, 
    WorkspaceUpdate, 
    WorkspaceResponse,
    WorkspaceSearchParams,
    WorkspaceStats,
    WorkspaceBulkUpdate
)

router = APIRouter(tags=["workspaces"])


def format_workspace_response(workspace: Workspace, db: Session) -> Dict[str, Any]:
    """
    Форматирование ответа с данными рабочего места
    
    Args:
        workspace: Объект рабочего места из БД
        db: Сессия базы данных
    
    Returns:
        Словарь с отформатированными данными
    """
    # Получаем связанные данные
    room = db.query(Room).filter(Room.id == workspace.room_id).first()
    status_obj = db.query(Status).filter(Status.id == room.status_id).first() if room else None
    
    # Подсчитываем бронирования
    booking_count = len(workspace.bookings) if workspace.bookings else 0
    
    return {
        "id": getattr(workspace, 'id', None),
        "name": getattr(workspace, 'name', None),
        "is_active": getattr(workspace, 'is_active', False),
        "room_id": getattr(workspace, 'room_id', None),
        "created_at": getattr(workspace, 'created_at', None).isoformat() if getattr(workspace, 'created_at', None) is not None else None,
        # Данные помещения
        "room_name": getattr(room, 'name', None) if room else None,
        "room_address": getattr(room, 'address', None) if room and getattr(room, 'address', None) else None,
        "room_description": getattr(room, 'description', None) if room and getattr(room, 'description', None) else None,
        "room_status_name": getattr(status_obj, 'name', None) if status_obj else None,
        # Статистика
        "total_bookings": booking_count,
        "active_bookings": booking_count  # Упрощенно - все бронирования считаются активными
    }


@router.get("/", response_model=List[Dict[str, Any]])
async def get_all_workspaces(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Получить список всех рабочих мест с пагинацией
    
    Args:
        skip: Количество пропускаемых записей
        limit: Максимальное количество возвращаемых записей
        db: Сессия базы данных
    
    Returns:
        Список рабочих мест с связанными данными
    """
    try:
        workspaces = db.query(Workspace).offset(skip).limit(limit).all()
        result = []
        
        for workspace in workspaces:
            result.append(format_workspace_response(workspace, db))
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении рабочих мест: {str(e)}"
        )


@router.get("/{workspace_id}", response_model=Dict[str, Any])
async def get_workspace(workspace_id: int, db: Session = Depends(get_db)):
    """
    Получить конкретное рабочее место по ID
    
    Args:
        workspace_id: ID рабочего места
        db: Сессия базы данных
    
    Returns:
        Данные рабочего места с связанной информацией
    
    Raises:
        HTTPException: 404 если рабочее место не найдено
    """
    try:
        workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Рабочее место с ID {workspace_id} не найдено"
            )
        
        return format_workspace_response(workspace, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении рабочего места: {str(e)}"
        )


@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace_data: WorkspaceCreate,
    db: Session = Depends(get_db)
):
    """
    Создать новое рабочее место
    
    Args:
        workspace_data: Данные для создания рабочего места
        db: Сессия базы данных
    
    Returns:
        Созданное рабочее место с полными данными
    
    Raises:
        HTTPException: 400 если помещение не найдено или название не уникально
    """
    try:
        # Проверяем существование помещения
        room = db.query(Room).filter(Room.id == workspace_data.room_id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Помещение с ID {workspace_data.room_id} не найдено"
            )
        
        # Проверяем уникальность названия в рамках помещения
        existing_workspace = db.query(Workspace).filter(
            and_(
                Workspace.name == workspace_data.name,
                Workspace.room_id == workspace_data.room_id
            )
        ).first()
        
        if existing_workspace:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Рабочее место с названием '{workspace_data.name}' уже существует в данном помещении"
            )
        
        # Создаем рабочее место
        new_workspace = Workspace(
            name=workspace_data.name,
            is_active=workspace_data.is_active,
            room_id=workspace_data.room_id
        )
        
        db.add(new_workspace)
        db.commit()
        db.refresh(new_workspace)
        
        # Форматируем ответ
        result = format_workspace_response(new_workspace, db)
        result["message"] = "Рабочее место успешно создано"
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании рабочего места: {str(e)}"
        )


@router.put("/{workspace_id}", response_model=Dict[str, Any])
async def update_workspace(
    workspace_id: int,
    workspace_data: WorkspaceUpdate,
    db: Session = Depends(get_db)
):
    """
    Обновить данные рабочего места
    
    Args:
        workspace_id: ID рабочего места
        workspace_data: Данные для обновления
        db: Сессия базы данных
    
    Returns:
        Обновленное рабочее место
    
    Raises:
        HTTPException: 404 если рабочее место не найдено
        HTTPException: 400 если новое помещение не найдено или название не уникально
    """
    try:
        # Проверяем существование рабочего места
        workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Рабочее место с ID {workspace_id} не найдено"
            )
        
        # Проверяем новое помещение, если указан
        if workspace_data.room_id:
            room = db.query(Room).filter(Room.id == workspace_data.room_id).first()
            if not room:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Помещение с ID {workspace_data.room_id} не найдено"
                )
        
        # Проверяем уникальность названия при изменении имени или помещения
        if workspace_data.name is not None or workspace_data.room_id is not None:
            # Определяем новое название и помещение
            new_name = workspace_data.name if workspace_data.name is not None else workspace.name
            new_room_id = workspace_data.room_id if workspace_data.room_id is not None else workspace.room_id
            
            # Проверяем существование рабочего места с таким же названием в том же помещении
            existing_workspace = db.query(Workspace).filter(
                and_(
                    Workspace.name == new_name,
                    Workspace.room_id == new_room_id,
                    Workspace.id != workspace_id  # Исключаем текущее рабочее место
                )
            ).first()
            
            if existing_workspace:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Рабочее место с названием '{new_name}' уже существует в данном помещении"
                )
        
        # Обновляем поля
        update_data = workspace_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(workspace, field, value)
        
        db.commit()
        db.refresh(workspace)
        
        # Форматируем ответ
        result = format_workspace_response(workspace, db)
        result["message"] = "Рабочее место успешно обновлено"
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении рабочего места: {str(e)}"
        )


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(workspace_id: int, db: Session = Depends(get_db)):
    """
    Удалить рабочее место
    
    Args:
        workspace_id: ID рабочего места
        db: Сессия базы данных
    
    Raises:
        HTTPException: 404 если рабочее место не найдено
    """
    try:
        workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Рабочее место с ID {workspace_id} не найдено"
            )
        
        db.delete(workspace)
        db.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении рабочего места: {str(e)}"
        )


@router.get("/room/{room_id}", response_model=List[Dict[str, Any]])
async def get_workspaces_by_room(
    room_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить все рабочие места в конкретном помещении
    
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
            result.append(format_workspace_response(workspace, db))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении рабочих мест помещения: {str(e)}"
        )


@router.get("/stats/overview", response_model=WorkspaceStats)
async def get_workspaces_stats(db: Session = Depends(get_db)):
    """
    Получить статистику по рабочим местам
    
    Args:
        db: Сессия базы данных
    
    Returns:
        Статистика по рабочим местам
    """
    try:
        # Общая статистика
        total_workspaces = db.query(Workspace).count()
        active_workspaces = db.query(Workspace).filter(Workspace.is_active == True).count()
        inactive_workspaces = total_workspaces - active_workspaces
        
        # Распределение по помещениям
        workspaces_by_room = {}
        rooms = db.query(Room).all()
        for room in rooms:
            count = db.query(Workspace).filter(Workspace.room_id == room.id).count()
            workspaces_by_room[room.name] = count
        
        # Упрощенный расчет коэффициента использования
        utilization_rate = 0.7 if total_workspaces > 0 else 0.0
        
        return WorkspaceStats(
            total_workspaces=total_workspaces,
            active_workspaces=active_workspaces,
            inactive_workspaces=inactive_workspaces,
            workspaces_by_room=workspaces_by_room,
            utilization_rate=utilization_rate
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статистики: {str(e)}"
        )


@router.put("/bulk/update", response_model=Dict[str, Any])
async def bulk_update_workspaces(
    bulk_data: WorkspaceBulkUpdate,
    db: Session = Depends(get_db)
):
    """
    Массовое обновление рабочих мест
    
    Args:
        bulk_data: Данные для массового обновления
        db: Сессия базы данных
    
    Returns:
        Результат массового обновления
    """
    try:
        # Проверяем существование рабочих мест
        workspaces = db.query(Workspace).filter(Workspace.id.in_(bulk_data.workspace_ids)).all()
        if len(workspaces) != len(bulk_data.workspace_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Некоторые рабочие места не найдены"
            )
        
        # Проверяем новое помещение, если указано
        if bulk_data.room_id:
            room = db.query(Room).filter(Room.id == bulk_data.room_id).first()
            if not room:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Помещение с ID {bulk_data.room_id} не найдено"
                )
        
        # Обновляем
        update_count = 0
        for workspace in workspaces:
            if bulk_data.is_active is not None:
                setattr(workspace, 'is_active', bulk_data.is_active)
            if bulk_data.room_id is not None:
                setattr(workspace, 'room_id', bulk_data.room_id)
            update_count += 1
        
        db.commit()
        
        return {
            "message": f"Обновлено {update_count} рабочих мест",
            "updated_count": update_count,
            "requested_count": len(bulk_data.workspace_ids)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при массовом обновлении: {str(e)}"
        )