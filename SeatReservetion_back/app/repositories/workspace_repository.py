"""
Репозиторий для работы с моделью Workspace (рабочие места)
Обеспечивает доступ к данным рабочих мест в базе данных и бизнес-логику
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from datetime import date

from app.models.workspace import Workspace
from app.models.room import Room
from app.models.status import Status
from app.schemas.workspace import WorkspaceSearchParams


class WorkspaceRepository:
    """Репозиторий для работы с рабочими местами"""
    
    def __init__(self, db: Session):
        """Инициализация репозитория"""
        self.db = db
    
    def create(self, workspace_data: Dict[str, Any]) -> Workspace:
        """
        Создание нового рабочего места
        
        Args:
            workspace_data: Словарь с данными рабочего места
            
        Returns:
            Созданный объект Workspace
        """
        db_workspace = Workspace(**workspace_data)
        self.db.add(db_workspace)
        self.db.commit()
        self.db.refresh(db_workspace)
        return db_workspace
    
    def get_by_id(self, workspace_id: int) -> Optional[Workspace]:
        """
        Получение рабочего места по ID
        
        Args:
            workspace_id: ID рабочего места
            
        Returns:
            Объект Workspace или None
        """
        return self.db.query(Workspace).filter(Workspace.id == workspace_id).first()
    
    def get_by_room_id(self, room_id: int) -> List[Workspace]:
        """
        Получение всех рабочих мест в помещении
        
        Args:
            room_id: ID помещения
            
        Returns:
            Список рабочих мест
        """
        return self.db.query(Workspace).filter(Workspace.room_id == room_id).all()
    
    def get_active_by_room_id(self, room_id: int) -> List[Workspace]:
        """
        Получение активных рабочих мест в помещении
        
        Args:
            room_id: ID помещения
            
        Returns:
            Список активных рабочих мест
        """
        return self.db.query(Workspace).filter(
            and_(Workspace.room_id == room_id, Workspace.is_active == True)
        ).all()
    
    def update(self, workspace_id: int, workspace_data: Dict[str, Any]) -> Optional[Workspace]:
        """
        Обновление данных рабочего места
        
        Args:
            workspace_id: ID рабочего места
            workspace_data: Словарь с обновленными данными
            
        Returns:
            Обновленный объект Workspace или None
        """
        db_workspace = self.get_by_id(workspace_id)
        if db_workspace:
            for key, value in workspace_data.items():
                setattr(db_workspace, key, value)
            self.db.commit()
            self.db.refresh(db_workspace)
        return db_workspace
    
    def delete(self, workspace_id: int) -> bool:
        """
        Удаление рабочего места
        
        Args:
            workspace_id: ID рабочего места
            
        Returns:
            True если удаление успешно, False иначе
        """
        db_workspace = self.get_by_id(workspace_id)
        if db_workspace:
            self.db.delete(db_workspace)
            self.db.commit()
            return True
        return False
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Workspace]:
        """
        Получение всех рабочих мест с пагинацией
        
        Args:
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей
            
        Returns:
            Список рабочих мест
        """
        return self.db.query(Workspace).offset(skip).limit(limit).all()
    
    def search_workspaces(self, search_params: WorkspaceSearchParams) -> tuple[List[Workspace], int]:
        """
        Поиск и фильтрация рабочих мест с пагинацией
        
        Args:
            search_params: Параметры поиска
            
        Returns:
            Кортеж (список рабочих мест, общее количество)
        """
        query = self.db.query(Workspace).join(Room)
        
        # Применяем поиск
        if search_params.search:
            search_term = f"%{search_params.search.lower()}%"
            query = query.filter(
                or_(
                    Workspace.name.ilike(search_term),
                    Room.name.ilike(search_term),
                    Room.address.ilike(search_term)
                )
            )
        
        # Фильтр по помещению
        if search_params.room_id:
            query = query.filter(Workspace.room_id == search_params.room_id)
        
        # Фильтр по активности
        if search_params.is_active is not None:
            query = query.filter(Workspace.is_active == search_params.is_active)
        
        # Подсчет общего количества
        total = query.count()
        
        # Сортировка
        sort_field_map = {
            "id": Workspace.id,
            "name": Workspace.name,
            "is_active": Workspace.is_active,
            "created_at": Workspace.created_at,
            "room_name": Room.name
        }
        
        sort_field = sort_field_map.get(search_params.sort_by, Workspace.name)
        if search_params.sort_order.lower() == "asc":
            query = query.order_by(asc(sort_field))
        else:
            query = query.order_by(desc(sort_field))
        
        # Пагинация
        offset = (search_params.page - 1) * search_params.per_page
        workspaces = query.offset(offset).limit(search_params.per_page).all()
        
        return workspaces, total
    
    def get_with_room_details(self, workspace_id: int) -> Optional[Workspace]:
        """
        Получение рабочего места с детальной информацией о помещении
        
        Args:
            workspace_id: ID рабочего места
            
        Returns:
            Объект Workspace с данными помещения или None
        """
        return self.db.query(Workspace).join(Room).join(Status).filter(
            Workspace.id == workspace_id
        ).first()
    
    def get_available_on_date(self, workspace_id: int, check_date: date) -> bool:
        """
        Проверка доступности рабочего места на определенную дату
        
        Args:
            workspace_id: ID рабочего места
            check_date: Дата для проверки
            
        Returns:
            True если место доступно
        """
        from app.models.booking import Booking
        
        existing_booking = self.db.query(Booking).filter(
            and_(
                Booking.workspace_id == workspace_id,
                Booking.booking_date == check_date
            )
        ).first()
        
        return existing_booking is None
    
    def get_bookings_count(self, workspace_id: int) -> int:
        """
        Подсчет общего количества бронирований рабочего места
        
        Args:
            workspace_id: ID рабочего места
            
        Returns:
            Количество бронирований
        """
        workspace = self.db.query(Workspace).filter(Workspace.id == workspace_id).first()
        if workspace and hasattr(workspace, 'bookings'):
            return len(workspace.bookings)
        return 0
    
    def get_recent_bookings(self, workspace_id: int, limit: int = 5) -> List[Workspace]:
        """
        Получение последних бронирований рабочего места
        
        Args:
            workspace_id: ID рабочего места
            limit: Максимальное количество бронирований
            
        Returns:
            Список рабочих мест с последними бронированиями
        """
        from app.models.booking import Booking
        from datetime import datetime
        
        return self.db.query(Workspace).filter(Workspace.id == workspace_id).join(
            Booking
        ).order_by(desc(Booking.created_at)).limit(limit).all()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Получение статистики по рабочим местам
        
        Returns:
            Словарь со статистикой
        """
        # Общее количество рабочих мест
        total = self.db.query(Workspace).count()
        
        # Количество активных рабочих мест
        active_workspaces = self.db.query(Workspace).filter(Workspace.is_active == True).count()
        inactive_workspaces = total - active_workspaces
        
        # Распределение по помещениям
        workspaces_by_room = {}
        rooms = self.db.query(Room).all()
        
        for room in rooms:
            count = self.db.query(Workspace).filter(Workspace.room_id == room.id).count()
            workspaces_by_room[room.name] = count
        
        # Подсчет бронирований по помещениям
        bookings_by_room = {}
        for room in rooms:
            workspace_ids = [w.id for w in self.db.query(Workspace).filter(Workspace.room_id == room.id).all()]
            if workspace_ids:
                from app.models.booking import Booking
                total_bookings = self.db.query(Booking).filter(Booking.workspace_id.in_(workspace_ids)).count()
                bookings_by_room[room.name] = total_bookings
            else:
                bookings_by_room[room.name] = 0
        
        return {
            "total_workspaces": total,
            "active_workspaces": active_workspaces,
            "inactive_workspaces": inactive_workspaces,
            "workspaces_by_room": workspaces_by_room,
            "bookings_by_room": bookings_by_room
        }
    
    def exists(self, workspace_id: int) -> bool:
        """
        Проверка существования рабочего места
        
        Args:
            workspace_id: ID рабочего места
            
        Returns:
            True если рабочее место существует
        """
        return self.db.query(Workspace).filter(Workspace.id == workspace_id).first() is not None
    
    def get_workspaces_by_status(self, room_id: int, is_active: bool) -> List[Workspace]:
        """
        Получение рабочих мест по статусу активности в помещении
        
        Args:
            room_id: ID помещения
            is_active: Статус активности
            
        Returns:
            Список рабочих мест
        """
        return self.db.query(Workspace).filter(
            and_(Workspace.room_id == room_id, Workspace.is_active == is_active)
        ).all()
    
    def get_utilization_rate(self, workspace_id: int, start_date: date, end_date: date) -> float:
        """
        Расчет коэффициента использования рабочего места за период
        
        Args:
            workspace_id: ID рабочего места
            start_date: Начальная дата периода
            end_date: Конечная дата периода
            
        Returns:
            Коэффициент использования (0-1)
        """
        from app.models.booking import Booking
        
        # Подсчитываем общее количество дней в периоде
        total_days = (end_date - start_date).days + 1
        
        # Подсчитываем дни с бронированиями
        booking_days = self.db.query(Booking).filter(
            and_(
                Booking.workspace_id == workspace_id,
                Booking.booking_date >= start_date,
                Booking.booking_date <= end_date
            )
        ).count()
        
        return booking_days / total_days if total_days > 0 else 0.0
    
    def get_most_popular(self, limit: int = 10) -> List[Workspace]:
        """
        Получение наиболее популярных рабочих мест
        
        Args:
            limit: Максимальное количество результатов
            
        Returns:
            Список популярных рабочих мест
        """
        from app.models.booking import Booking
        from sqlalchemy import func
        
        return self.db.query(Workspace).join(Booking).group_by(Workspace.id).order_by(
            desc(func.count(Booking.id))
        ).limit(limit).all()
    
    def bulk_update_status(self, workspace_ids: List[int], is_active: bool) -> int:
        """
        Массовое обновление статуса активности рабочих мест
        
        Args:
            workspace_ids: Список ID рабочих мест
            is_active: Новый статус активности
            
        Returns:
            Количество обновленных записей
        """
        updated_count = self.db.query(Workspace).filter(
            Workspace.id.in_(workspace_ids)
        ).update({'is_active': is_active}, synchronize_session=False)
        
        self.db.commit()
        return updated_count