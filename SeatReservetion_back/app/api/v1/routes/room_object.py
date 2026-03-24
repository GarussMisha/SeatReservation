"""
API для управления объектами помещения
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.core.database import get_db
from app.models.room_object import RoomObject
from app.models.workspace_on_plan import WorkspaceOnPlan
from app.models.wall import Wall
from app.models.door import Door
from app.models.window import Window
from app.models.room import Room
from app.schemas.room_object import (
    RoomObjectCreate,
    RoomObjectUpdate,
    RoomObjectResponse,
    WallCreate,
    WallResponse,
    DoorCreate,
    DoorResponse,
    WindowCreate,
    WindowResponse,
    WorkspaceOnPlanCreate,
    WorkspaceOnPlanUpdate,
    WorkspaceOnPlanResponse,
    RoomPlanCreate,
    RoomPlanResponse,
)

router = APIRouter(tags=["Room Objects"])


# === CRUD для RoomObject ===

@router.get("/{room_id}/objects", response_model=List[RoomObjectResponse])
def get_room_objects(room_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Получить все объекты помещения
    
    - **room_id**: ID помещения
    - **skip**: Пропуск записей
    - **limit**: Лимит записей
    """
    objects = db.query(RoomObject).filter(RoomObject.room_id == room_id).offset(skip).limit(limit).all()
    return objects


@router.get("/objects/{object_id}", response_model=RoomObjectResponse)
def get_room_object(object_id: int, db: Session = Depends(get_db)):
    """
    Получить объект помещения по ID
    """
    obj = db.query(RoomObject).filter(RoomObject.id == object_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Объект не найден")
    return obj


@router.post("/{room_id}/objects", response_model=RoomObjectResponse, status_code=status.HTTP_201_CREATED)
def create_room_object(room_id: int, object_data: RoomObjectCreate, db: Session = Depends(get_db)):
    """
    Создать объект помещения
    
    - **room_id**: ID помещения
    - **object_type**: Тип объекта (wall, door, window, workspace, printer, kitchen, meeting_room, staircase)
    - **x, y**: Координаты
    - **rotation**: Угол поворота
    - **width, height**: Размеры
    - **name**: Имя объекта
    - **properties**: Дополнительные свойства JSON
    """
    # Проверяем существование помещения
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Помещение не найдено")
    
    # Создаем объект
    db_object = RoomObject(
        room_id=room_id,
        object_type=object_data.object_type,
        x=object_data.x,
        y=object_data.y,
        rotation=object_data.rotation,
        width=object_data.width,
        height=object_data.height,
        name=object_data.name,
        description=object_data.description,
        is_active=object_data.is_active,
        properties=json.dumps(object_data.properties) if object_data.properties else None,
    )
    
    db.add(db_object)
    db.commit()
    db.refresh(db_object)
    
    # Если это рабочее место, создаем запись в workspace_on_plan
    if object_data.object_type == "workspace":
        workspace_on_plan = WorkspaceOnPlan(
            room_object_id=db_object.id,
            status_id=1,  # По умолчанию свободно
            workspace_number=None,  # Будет автогенерировано
        )
        db.add(workspace_on_plan)
        db.commit()
    
    return db_object


@router.put("/objects/{object_id}", response_model=RoomObjectResponse)
def update_room_object(object_id: int, update_data: RoomObjectUpdate, db: Session = Depends(get_db)):
    """
    Обновить объект помещения
    """
    obj = db.query(RoomObject).filter(RoomObject.id == object_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Объект не найден")
    
    # Обновляем поля
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        if field == "properties" and value is not None:
            value = json.dumps(value)
        setattr(obj, field, value)
    
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/objects/{object_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room_object(object_id: int, db: Session = Depends(get_db)):
    """
    Удалить объект помещения
    """
    obj = db.query(RoomObject).filter(RoomObject.id == object_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Объект не найден")
    
    db.delete(obj)
    db.commit()
    return None


# === Специализированные endpoints для стен ===

@router.post("/walls", response_model=WallResponse, status_code=status.HTTP_201_CREATED)
def create_wall(wall_data: WallCreate, db: Session = Depends(get_db)):
    """
    Создать стену
    
    Сначала создается RoomObject, затем Wall
    """
    # Создаем базовый объект
    room_object = RoomObject(
        room_id=db.query(Room).filter(Room.id == wall_data.room_object_id).first().id if not db.query(Room).filter(Room.id == wall_data.room_object_id).first() else wall_data.room_object_id,
        object_type="wall",
        width=wall_data.length,
        height=wall_data.thickness,
    )
    db.add(room_object)
    db.commit()
    db.refresh(room_object)
    
    # Создаем стену
    wall = Wall(
        room_object_id=room_object.id,
        wall_type=wall_data.wall_type,
        length=wall_data.length,
        thickness=wall_data.thickness,
        has_window=wall_data.has_window,
        has_door=wall_data.has_door,
    )
    db.add(wall)
    db.commit()
    db.refresh(wall)
    
    return wall


# === Специализированные endpoints для дверей ===

@router.post("/doors", response_model=DoorResponse, status_code=status.HTTP_201_CREATED)
def create_door(door_data: DoorCreate, db: Session = Depends(get_db)):
    """
    Создать дверь
    """
    # Создаем базовый объект
    room_object = RoomObject(
        room_id=db.query(Room).filter(Room.id == door_data.room_object_id).first().id,
        object_type="door",
        width=door_data.width,
        height=100,
    )
    db.add(room_object)
    db.commit()
    db.refresh(room_object)
    
    # Создаем дверь
    door = Door(
        room_object_id=room_object.id,
        door_type=door_data.door_type,
        swing_direction=door_data.swing_direction,
        is_open=door_data.is_open,
        width=door_data.width,
    )
    db.add(door)
    db.commit()
    db.refresh(door)
    
    return door


# === Специализированные endpoints для окон ===

@router.post("/windows", response_model=WindowResponse, status_code=status.HTTP_201_CREATED)
def create_window(window_data: WindowCreate, db: Session = Depends(get_db)):
    """
    Создать окно
    """
    # Создаем базовый объект
    room_object = RoomObject(
        room_id=db.query(Room).filter(Room.id == window_data.room_object_id).first().id,
        object_type="window",
        width=window_data.width,
        height=window_data.height,
    )
    db.add(room_object)
    db.commit()
    db.refresh(room_object)
    
    # Создаем окно
    window = Window(
        room_object_id=room_object.id,
        width=window_data.width,
        height=window_data.height,
        is_open=window_data.is_open,
        window_type=window_data.window_type,
    )
    db.add(window)
    db.commit()
    db.refresh(window)
    
    return window


# === Endpoints для рабочих мест на плане ===

@router.post("/workspaces-on-plan", response_model=WorkspaceOnPlanResponse, status_code=status.HTTP_201_CREATED)
def create_workspace_on_plan(workspace_data: WorkspaceOnPlanCreate, db: Session = Depends(get_db)):
    """
    Создать рабочее место на плане
    """
    # Проверяем существование room_object
    room_object = db.query(RoomObject).filter(RoomObject.id == workspace_data.room_object_id).first()
    if not room_object:
        raise HTTPException(status_code=404, detail="Объект помещения не найден")
    
    # Создаем рабочее место на плане
    workspace_on_plan = WorkspaceOnPlan(
        room_object_id=workspace_data.room_object_id,
        workspace_id=workspace_data.workspace_id,
        status_id=workspace_data.status_id,
        workspace_number=workspace_data.workspace_number,
    )
    db.add(workspace_on_plan)
    db.commit()
    db.refresh(workspace_on_plan)
    
    return workspace_on_plan


@router.put("/workspaces-on-plan/{wp_id}", response_model=WorkspaceOnPlanResponse)
def update_workspace_on_plan(wp_id: int, update_data: WorkspaceOnPlanUpdate, db: Session = Depends(get_db)):
    """
    Обновить рабочее место на плане
    """
    wp = db.query(WorkspaceOnPlan).filter(WorkspaceOnPlan.id == wp_id).first()
    if not wp:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(wp, field, value)
    
    db.commit()
    db.refresh(wp)
    return wp


# === Endpoints для управления планом помещения ===

@router.post("/{room_id}/plan", response_model=RoomPlanResponse)
def save_room_plan(room_id: int, plan_data: RoomPlanCreate, db: Session = Depends(get_db)):
    """
    Сохранить весь план помещения
    
    - **objects**: Список всех объектов с их свойствами
    """
    # Проверяем помещение
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Помещение не найдено")
    
    created_objects = []
    
    for obj_data in plan_data.objects:
        # Создаем RoomObject
        room_object = RoomObject(
            room_id=room_id,
            object_type=obj_data.get("object_type", "workspace"),
            x=obj_data.get("x", 0),
            y=obj_data.get("y", 0),
            rotation=obj_data.get("rotation", 0),
            width=obj_data.get("width", 100),
            height=obj_data.get("height", 50),
            name=obj_data.get("name"),
            description=obj_data.get("description"),
            is_active=obj_data.get("is_active", True),
            properties=json.dumps(obj_data.get("properties", {})) if obj_data.get("properties") else None,
        )
        db.add(room_object)
        db.flush()  # Получаем ID
        created_objects.append(room_object)
        
        # Если это рабочее место, создаем запись в workspace_on_plan
        if obj_data.get("object_type") == "workspace":
            workspace_on_plan = WorkspaceOnPlan(
                room_object_id=room_object.id,
                status_id=obj_data.get("status_id", 1),
                workspace_number=obj_data.get("workspace_number"),
            )
            db.add(workspace_on_plan)
    
    db.commit()
    
    return RoomPlanResponse(
        room_id=room_id,
        objects=created_objects,
        total_objects=len(created_objects)
    )


@router.get("/{room_id}/plan", response_model=RoomPlanResponse)
def get_room_plan(room_id: int, db: Session = Depends(get_db)):
    """
    Получить весь план помещения
    """
    objects = db.query(RoomObject).filter(RoomObject.room_id == room_id).all()
    
    return RoomPlanResponse(
        room_id=room_id,
        objects=objects,
        total_objects=len(objects)
    )
