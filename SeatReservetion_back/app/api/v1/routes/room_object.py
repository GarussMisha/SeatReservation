"""
API для управления объектами помещения
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json

from app.core.database import get_db
from app.core.status_constants import WorkspaceStatuses, BookingStatuses
from app.models.room_object import RoomObject
from app.models.workspace_on_plan import WorkspaceOnPlan
from app.models.workspace import Workspace
from app.models.wall import Wall
from app.models.door import Door
from app.models.window import Window
from app.models.room import Room
from app.models.booking import Booking
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
from app.schemas.workspace import WorkspaceResponse

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
            status_id=WorkspaceStatuses.FREE,  # ✅ 10 = free (вместо status_id=1)
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

    ВАЖНО: Все существующие объекты помещения удаляются и создаются заново.
    При создании рабочих мест автоматически создаются записи в таблице workspaces.
    """
    # Проверяем помещение
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Помещение не найдено")

    # Сохраняем размеры поля если они указаны
    if plan_data.fieldWidth is not None:
        room.field_width = plan_data.fieldWidth
    if plan_data.fieldHeight is not None:
        room.field_height = plan_data.fieldHeight
    db.commit()

    # === Удаляем все существующие объекты помещения ===
    # Сначала собираем ID рабочих мест, которые будут удалены (для каскадного удаления workspaces)
    workspace_ids_to_delete = []
    existing_objects = db.query(RoomObject).filter(RoomObject.room_id == room_id).all()
    for obj in existing_objects:
        if obj.object_type == "workspace" and obj.workspace_data:
            if obj.workspace_data.workspace_id:
                workspace_ids_to_delete.append(obj.workspace_data.workspace_id)
        db.delete(obj)
    db.commit()

    # === Удаляем рабочие места из основной таблицы workspaces ===
    # Удаляем только те рабочие места, которые не имеют активных бронирований
    for ws_id in workspace_ids_to_delete:
        # Проверяем наличие активных бронирований (исключаем cancelled=14 и completed=15)
        has_active_bookings = db.query(Booking).filter(
            Booking.workspace_id == ws_id,
            Booking.status_id.notin_([14, 15])
        ).first()

        if not has_active_bookings:
            workspace = db.query(Workspace).filter(Workspace.id == ws_id).first()
            if workspace:
                db.delete(workspace)
    
    db.commit()

    # === Подсчитываем количество рабочих мест для генерации названий ===
    workspace_counter = db.query(Workspace).filter(
        Workspace.room_id == room_id
    ).count()

    created_objects = []
    created_workspaces_map = {}  # room_object_id -> workspace_id

    for obj_data in plan_data.objects:
        print(f"Обработка объекта: {obj_data}")

        # Для стен, перегородок и окон сохраняем points в properties
        properties = obj_data.get("properties") if obj_data.get("properties") else {}
        if obj_data.get("object_type") in ["wall", "internal_wall", "window"]:
            if "points" in obj_data:
                print(f"Найден points для {obj_data.get('object_type')}: {obj_data['points']}")
                properties["points"] = obj_data["points"]
            else:
                print(f"Нет points для {obj_data.get('object_type')}")

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
            properties=json.dumps(properties) if properties else None,
        )
        db.add(room_object)
        db.flush()  # Получаем ID
        created_objects.append(room_object)

        # Если это рабочее место, создаем запись в workspace и workspace_on_plan
        if obj_data.get("object_type") == "workspace":
            workspace_counter += 1
            
            # Используем название из объекта или генерируем по умолчанию
            workspace_name = obj_data.get("name")
            if not workspace_name:
                workspace_name = f"Рабочее место {workspace_counter}"
            
            # Проверяем уникальность названия в помещении
            existing_workspace = db.query(Workspace).filter(
                Workspace.name == workspace_name,
                Workspace.room_id == room_id
            ).first()
            
            if existing_workspace:
                # Если название занято, добавляем номер
                workspace_name = f"Рабочее место {workspace_counter}_{room_object.id}"
            
            # Создаем рабочее место в основной таблице
            workspace = Workspace(
                name=workspace_name,
                room_id=room_id,
                is_active=True,
                status_id=WorkspaceStatuses.FREE,  # ✅ 10 = free (вместо status_id=1)
            )
            db.add(workspace)
            db.flush()  # Получаем ID
            
            # Сохраняем маппинг
            created_workspaces_map[room_object.id] = workspace.id
            
            # Обновляем name в RoomObject
            room_object.name = workspace_name
            
            # Создаем запись в workspace_on_plan
            workspace_on_plan = WorkspaceOnPlan(
                room_object_id=room_object.id,
                workspace_id=workspace.id,
                status_id=WorkspaceStatuses.FREE,  # ✅ 10 = free (вместо status_id=1)
                workspace_number=workspace_counter,
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
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Помещение не найдено")

    objects = db.query(RoomObject).filter(RoomObject.room_id == room_id).all()

    # Для рабочих мест добавляем workspace_on_plan_id
    objects_with_data = []
    for obj in objects:
        obj_dict = {
            "id": obj.id,
            "room_id": obj.room_id,
            "object_type": obj.object_type,
            "x": obj.x,
            "y": obj.y,
            "rotation": obj.rotation,
            "width": obj.width,
            "height": obj.height,
            "name": obj.name,
            "description": obj.description,
            "is_active": obj.is_active,
            "properties": json.loads(obj.properties) if obj.properties else None,
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
            "updated_at": None,  # В модели RoomObject нет поля updated_at
        }

        # Если это рабочее место, добавляем workspace_on_plan_id
        if obj.object_type == "workspace" and obj.workspace_data:
            obj_dict["workspace_on_plan_id"] = obj.workspace_data.id

        objects_with_data.append(obj_dict)

    return RoomPlanResponse(
        room_id=room_id,
        objects=objects_with_data,
        total_objects=len(objects_with_data),
        fieldWidth=room.field_width,
        fieldHeight=room.field_height
    )


@router.delete("/{room_id}/plan", status_code=status.HTTP_204_NO_CONTENT)
def clear_room_plan(room_id: int, db: Session = Depends(get_db)):
    """
    Очистить весь план помещения (удалить все объекты)

    - Удаляет все объекты помещения (стены, двери, окна, рабочие места и др.)
    - Связанные записи (Wall, Door, Window, WorkspaceOnPlan) удаляются каскадно
    - Рабочие места из основной таблицы workspaces удаляются, если нет активных бронирований
    """
    # Проверяем помещение
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Помещение не найдено")

    # === Удаляем все существующие объекты помещения ===
    # Сначала собираем ID рабочих мест, которые будут удалены
    workspace_ids_to_delete = []
    existing_objects = db.query(RoomObject).filter(RoomObject.room_id == room_id).all()
    for obj in existing_objects:
        if obj.object_type == "workspace" and obj.workspace_data:
            if obj.workspace_data.workspace_id:
                workspace_ids_to_delete.append(obj.workspace_data.workspace_id)
        db.delete(obj)
    db.commit()

    # === Удаляем рабочие места из основной таблицы workspaces ===
    # Удаляем только те рабочие места, которые не имеют активных бронирований
    for ws_id in workspace_ids_to_delete:
        # Проверяем наличие активных бронирований (исключаем cancelled=14 и completed=15)
        has_active_bookings = db.query(Booking).filter(
            Booking.workspace_id == ws_id,
            Booking.status_id.notin_([14, 15])
        ).first()

        if not has_active_bookings:
            workspace = db.query(Workspace).filter(Workspace.id == ws_id).first()
            if workspace:
                db.delete(workspace)
    
    db.commit()

    return None


# === Endpoints для обновления названия рабочего места ===

@router.put("/{room_id}/workspaces-on-plan/{wp_id}/name", response_model=Dict[str, Any])
def update_workspace_name(
    room_id: int,
    wp_id: int,
    name_data: Dict[str, str],
    db: Session = Depends(get_db)
):
    """
    Обновить название рабочего места на плане

    - **room_id**: ID помещения
    - **wp_id**: ID записи в workspace_on_plan
    - **name**: Новое название рабочего места
    """
    # Проверяем существование workspace_on_plan
    wp = db.query(WorkspaceOnPlan).filter(WorkspaceOnPlan.id == wp_id).first()
    if not wp:
        raise HTTPException(status_code=404, detail="Запись рабочего места на плане не найдена")

    # Проверяем, что принадлежит этому помещению
    room_object = db.query(RoomObject).filter(RoomObject.id == wp.room_object_id).first()
    if not room_object or room_object.room_id != room_id:
        raise HTTPException(status_code=404, detail="Рабочее место не принадлежит этому помещению")

    # Получаем новое название
    new_name = name_data.get("name", "").strip()
    if not new_name:
        raise HTTPException(status_code=400, detail="Название не может быть пустым")

    # Проверяем уникальность названия в помещении
    existing = db.query(Workspace).filter(
        Workspace.name == new_name,
        Workspace.room_id == room_id,
        Workspace.id != wp.workspace_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Рабочее место с названием '{new_name}' уже существует в этом помещении"
        )

    # Обновляем название в основной таблице workspaces
    if wp.workspace_id:
        workspace = db.query(Workspace).filter(Workspace.id == wp.workspace_id).first()
        if workspace:
            workspace.name = new_name
            db.commit()
            db.refresh(workspace)
    
    # Обновляем название в room_object
    room_object.name = new_name
    db.commit()

    return {
        "message": "Название рабочего места успешно обновлено",
        "workspace_id": wp.workspace_id,
        "name": new_name
    }


# === Endpoint для получения рабочих мест с координатами ===

@router.get("/{room_id}/workspaces/with-locations", response_model=List[Dict[str, Any]])
def get_workspaces_with_locations(
    room_id: int,
    booking_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Получить все рабочие места помещения с их координатами на плане

    - **room_id**: ID помещения
    - **booking_date**: Дата для проверки бронирований (опционально)

    Возвращает рабочие места с координатами из room_objects и статусом бронирования
    """
    # Проверяем помещение
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Помещение не найдено")

    # Получаем все рабочие места на плане с координатами
    room_objects = db.query(RoomObject).filter(
        RoomObject.room_id == room_id,
        RoomObject.object_type == "workspace"
    ).all()

    result = []
    
    for room_obj in room_objects:
        workspace_on_plan = room_obj.workspace_data
        
        if not workspace_on_plan:
            continue

        workspace = None
        if workspace_on_plan.workspace_id:
            workspace = db.query(Workspace).filter(Workspace.id == workspace_on_plan.workspace_id).first()

        # === Определяем статус рабочего места ===
        # Статус зависит от: 1) статуса самого workspace, 2) наличия активной брони

        # По умолчанию считаем место свободным
        status = "available"
        current_booking = None

        # Если workspace не активен (is_active=False) ИЛИ имеет статус inactive - место не активно
        if workspace and (not workspace.is_active or workspace.status_id == 2):  # 2 = inactive
            status = "inactive"

        # Если есть дата для проверки - ищем бронь
        elif booking_date:
            # Ищем ВСЕ бронирования на эту дату, сортируем по ID (новые первые)
            booking = db.query(Booking).filter(
                Booking.workspace_id == workspace_on_plan.workspace_id,
                Booking.booking_date == booking_date
            ).order_by(Booking.id.desc()).first()

            print(f"DEBUG: workspace_id={workspace_on_plan.workspace_id}, booking_date={booking_date}, booking={booking}, status_id={booking.status_id if booking else 'None'}")

            # Проверяем статус бронирования
            if booking:
                # Статусы бронирований:
                # 12: pending - ожидает
                # 13: confirmed - подтверждена (активна)
                # 14: cancelled - отменена
                # 15: completed - завершена

                CONFIRMED_STATUS = 13  # Активная бронь

                if booking.status_id == CONFIRMED_STATUS:
                    # Бронь активна - место занято
                    status = "booked"
                    current_booking = {
                        "id": booking.id,
                        "account_id": booking.account_id,
                        "account_first_name": booking.account.first_name if booking.account else None,
                        "account_last_name": booking.account.last_name if booking.account else None,
                        "booking_date": booking.booking_date.isoformat(),
                        "status_id": booking.status_id,
                        "is_my_booking": False
                    }
                    print(f"DEBUG: Место занято, booking_id={booking.id}")
                else:
                    print(f"DEBUG: Бронь не активна (status_id={booking.status_id}), место свободно")
                # else: Бронь отменена (14) или завершена (15) или ожидает (12) - считаем место свободным
                # current_booking = None, status = "available"

        workspace_data = {
            "id": workspace_on_plan.workspace_id if workspace_on_plan.workspace_id else workspace_on_plan.id,
            "workspace_on_plan_id": workspace_on_plan.id,
            "room_object_id": room_obj.id,
            "name": workspace.name if workspace else f"Рабочее место {workspace_on_plan.workspace_number or room_obj.id}",
            "x": room_obj.x,
            "y": room_obj.y,
            "width": room_obj.width,
            "height": room_obj.height,
            "rotation": room_obj.rotation,
            "status": status,
            "status_id": workspace_on_plan.status_id,
            "workspace_number": workspace_on_plan.workspace_number,
            "is_active": workspace.is_active if workspace else True,
            "current_booking": current_booking
        }
        
        result.append(workspace_data)

    return result
