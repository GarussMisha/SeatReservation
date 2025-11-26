"""
Репозиторий для работы с моделью Booking (бронирования)
Обеспечивает доступ к данным бронирований в базе данных и бизнес-логику
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from datetime import date, datetime, timedelta

from app.models.booking import Booking
from app.models.account import Account
from app.models.workspace import Workspace
from app.models.status import Status
from app.models.room import Room
from app.schemas.booking import BookingSearchParams


class BookingRepository:
    """Репозиторий для работы с бронированиями"""
    
    def __init__(self, db: Session):
        """Инициализация репозитория"""
        self.db = db
    
    def create(self, booking_data: Dict[str, Any]) -> Booking:
        """
        Создание нового бронирования
        
        Args:
            booking_data: Словарь с данными бронирования
            
        Returns:
            Созданный объект Booking
        """
        db_booking = Booking(**booking_data)
        self.db.add(db_booking)
        self.db.commit()
        self.db.refresh(db_booking)
        return db_booking
    
    def get_by_id(self, booking_id: int) -> Optional[Booking]:
        """
        Получение бронирования по ID
        
        Args:
            booking_id: ID бронирования
            
        Returns:
            Объект Booking или None
        """
        return self.db.query(Booking).filter(Booking.id == booking_id).first()
    
    def get_by_workspace_and_date(self, workspace_id: int, booking_date: date) -> Optional[Booking]:
        """
        Получение бронирования по рабочему месту и дате
        
        Args:
            workspace_id: ID рабочего места
            booking_date: Дата бронирования
            
        Returns:
            Объект Booking или None
        """
        return self.db.query(Booking).filter(
            and_(
                Booking.workspace_id == workspace_id,
                Booking.booking_date == booking_date
            )
        ).first()
    
    def get_by_account_id(self, account_id: int) -> List[Booking]:
        """
        Получение всех бронирований пользователя
        
        Args:
            account_id: ID аккаунта
            
        Returns:
            Список бронирований
        """
        return self.db.query(Booking).filter(Booking.account_id == account_id).all()
    
    def get_by_workspace_id(self, workspace_id: int) -> List[Booking]:
        """
        Получение всех бронирований рабочего места
        
        Args:
            workspace_id: ID рабочего места
            
        Returns:
            Список бронирований
        """
        return self.db.query(Booking).filter(Booking.workspace_id == workspace_id).all()
    
    def get_by_date_range(self, date_from: date, date_to: date) -> List[Booking]:
        """
        Получение бронирований в диапазоне дат
        
        Args:
            date_from: Начальная дата
            date_to: Конечная дата
            
        Returns:
            Список бронирований
        """
        return self.db.query(Booking).filter(
            and_(
                Booking.booking_date >= date_from,
                Booking.booking_date <= date_to
            )
        ).all()
    
    def get_by_date(self, booking_date: date) -> List[Booking]:
        """
        Получение бронирований на конкретную дату
        
        Args:
            booking_date: Дата для поиска
            
        Returns:
            Список бронирований
        """
        return self.db.query(Booking).filter(Booking.booking_date == booking_date).all()
    
    def update(self, booking_id: int, booking_data: Dict[str, Any]) -> Optional[Booking]:
        """
        Обновление данных бронирования
        
        Args:
            booking_id: ID бронирования
            booking_data: Словарь с обновленными данными
            
        Returns:
            Обновленный объект Booking или None
        """
        db_booking = self.get_by_id(booking_id)
        if db_booking:
            for key, value in booking_data.items():
                setattr(db_booking, key, value)
            self.db.commit()
            self.db.refresh(db_booking)
        return db_booking
    
    def delete(self, booking_id: int) -> bool:
        """
        Удаление бронирования
        
        Args:
            booking_id: ID бронирования
            
        Returns:
            True если удаление успешно, False иначе
        """
        db_booking = self.get_by_id(booking_id)
        if db_booking:
            self.db.delete(db_booking)
            self.db.commit()
            return True
        return False
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Booking]:
        """
        Получение всех бронирований с пагинацией
        
        Args:
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей
            
        Returns:
            Список бронирований
        """
        return self.db.query(Booking).offset(skip).limit(limit).all()
    
    def search_bookings(self, search_params: BookingSearchParams) -> tuple[List[Booking], int]:
        """
        Поиск и фильтрация бронирований с пагинацией
        
        Args:
            search_params: Параметры поиска
            
        Returns:
            Кортеж (список бронирований, общее количество)
        """
        query = self.db.query(Booking).join(Account).join(Workspace).join(Room).join(Status)
        
        # Применяем поиск
        if search_params.search:
            search_term = f"%{search_params.search.lower()}%"
            query = query.filter(
                or_(
                    Account.login.ilike(search_term),
                    Workspace.name.ilike(search_term),
                    Room.name.ilike(search_term)
                )
            )
        
        # Фильтр по дате
        if search_params.date_from:
            query = query.filter(Booking.booking_date >= search_params.date_from)
        if search_params.date_to:
            query = query.filter(Booking.booking_date <= search_params.date_to)
        
        # Фильтр по пользователю
        if search_params.account_id:
            query = query.filter(Booking.account_id == search_params.account_id)
        
        # Фильтр по рабочему месту
        if search_params.workspace_id:
            query = query.filter(Booking.workspace_id == search_params.workspace_id)
        
        # Фильтр по статусу
        if search_params.status_id:
            query = query.filter(Booking.status_id == search_params.status_id)
        
        # Подсчет общего количества
        total = query.count()
        
        # Сортировка
        sort_field_map = {
            "id": Booking.id,
            "booking_date": Booking.booking_date,
            "created_at": Booking.created_at,
            "account_login": Account.login,
            "workspace_name": Workspace.name,
            "status_name": Status.name
        }
        
        sort_field = sort_field_map.get(search_params.sort_by, Booking.booking_date)
        if search_params.sort_order.lower() == "asc":
            query = query.order_by(asc(sort_field))
        else:
            query = query.order_by(desc(sort_field))
        
        # Пагинация
        offset = (search_params.page - 1) * search_params.per_page
        bookings = query.offset(offset).limit(search_params.per_page).all()
        
        return bookings, total
    
    def get_with_details(self, booking_id: int) -> Optional[Booking]:
        """
        Получение бронирования с детальной информацией
        
        Args:
            booking_id: ID бронирования
            
        Returns:
            Объект Booking с связанными данными или None
        """
        return self.db.query(Booking).join(Account).join(Workspace).join(Room).join(
            Status
        ).filter(Booking.id == booking_id).first()
    
    def get_by_status_id(self, status_id: int) -> List[Booking]:
        """
        Получение всех бронирований с определенным статусом
        
        Args:
            status_id: ID статуса
            
        Returns:
            Список бронирований
        """
        return self.db.query(Booking).filter(Booking.status_id == status_id).all()
    
    def get_confirmed_bookings(self) -> List[Booking]:
        """
        Получение подтвержденных бронирований
        
        Returns:
            Список подтвержденных бронирований
        """
        confirmed_status = self.db.query(Status).filter(Status.name == "confirmed").first()
        if confirmed_status:
            return self.db.query(Booking).filter(Booking.status_id == confirmed_status.id).all()
        return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Получение статистики по бронированиям
        
        Returns:
            Словарь со статистикой
        """
        today = date.today()
        
        # Общее количество бронирований
        total = self.db.query(Booking).count()
        
        # Бронирования по датам
        upcoming_bookings = self.db.query(Booking).filter(Booking.booking_date > today).count()
        today_bookings = self.db.query(Booking).filter(Booking.booking_date == today).count()
        past_bookings = self.db.query(Booking).filter(Booking.booking_date < today).count()
        
        # Отмененные бронирования
        cancelled_status = self.db.query(Status).filter(Status.name == "cancelled").first()
        cancelled_bookings = 0
        if cancelled_status:
            cancelled_bookings = self.db.query(Booking).filter(
                Booking.status_id == cancelled_status.id
            ).count()
        
        # Распределение по статусам
        bookings_by_status = {}
        all_statuses = self.db.query(Status).all()
        for status in all_statuses:
            count = self.db.query(Booking).filter(Booking.status_id == status.id).count()
            bookings_by_status[status.name] = count
        
        # Распределение по рабочим местам
        bookings_by_workspace = {}
        workspaces = self.db.query(Workspace).all()
        for workspace in workspaces:
            count = self.db.query(Booking).filter(Booking.workspace_id == workspace.id).count()
            bookings_by_workspace[workspace.name] = count
        
        # Распределение по пользователям
        bookings_by_user = {}
        accounts = self.db.query(Account).all()
        for account in accounts:
            count = self.db.query(Booking).filter(Booking.account_id == account.id).count()
            bookings_by_user[account.login] = count
        
        # Коэффициент использования на сегодня
        total_workspaces = self.db.query(Workspace).count()
        utilization_rate = 0.0
        if total_workspaces > 0:
            utilization_rate = min(today_bookings / total_workspaces, 1.0)
        
        # Среднее количество бронирований в день
        avg_bookings_per_day = 0.0
        if total > 0:
            # Упрощенный расчет - в реальности нужна более сложная логика
            avg_bookings_per_day = total / 30  # Примерно 30 дней
        
        return {
            "total_bookings": total,
            "upcoming_bookings": upcoming_bookings,
            "today_bookings": today_bookings,
            "past_bookings": past_bookings,
            "cancelled_bookings": cancelled_bookings,
            "bookings_by_status": bookings_by_status,
            "bookings_by_workspace": bookings_by_workspace,
            "bookings_by_user": bookings_by_user,
            "utilization_rate": utilization_rate,
            "avg_bookings_per_day": avg_bookings_per_day
        }
    
    def exists(self, booking_id: int) -> bool:
        """
        Проверка существования бронирования
        
        Args:
            booking_id: ID бронирования
            
        Returns:
            True если бронирование существует
        """
        return self.db.query(Booking).filter(Booking.id == booking_id).first() is not None
    
    def check_workspace_availability(self, workspace_id: int, booking_date: date, exclude_id: Optional[int] = None) -> bool:
        """
        Проверка доступности рабочего места на дату
        
        Args:
            workspace_id: ID рабочего места
            booking_date: Дата для проверки
            exclude_id: ID бронирования для исключения (при обновлении)
            
        Returns:
            True если рабочее место доступно
        """
        query = self.db.query(Booking).filter(
            and_(
                Booking.workspace_id == workspace_id,
                Booking.booking_date == booking_date
            )
        )
        
        if exclude_id:
            query = query.filter(Booking.id != exclude_id)
        
        return query.first() is None
    
    def get_user_bookings_summary(self, account_id: int) -> Dict[str, Any]:
        """
        Получение сводки бронирований пользователя
        
        Args:
            account_id: ID аккаунта пользователя
            
        Returns:
            Словарь с информацией о бронированиях
        """
        today = date.today()
        
        # Общее количество
        total = self.db.query(Booking).filter(Booking.account_id == account_id).count()
        
        # По статусам
        bookings_by_status = {}
        all_statuses = self.db.query(Status).all()
        for status in all_statuses:
            count = self.db.query(Booking).filter(
                and_(
                    Booking.account_id == account_id,
                    Booking.status_id == status.id
                )
            ).count()
            bookings_by_status[status.name] = count
        
        # По датам
        upcoming = self.db.query(Booking).filter(
            and_(
                Booking.account_id == account_id,
                Booking.booking_date > today
            )
        ).count()
        
        past = total - upcoming
        
        return {
            "total_bookings": total,
            "upcoming_bookings": upcoming,
            "past_bookings": past,
            "bookings_by_status": bookings_by_status
        }
    
    def get_most_popular_workspaces(self, limit: int = 10) -> List[Workspace]:
        """
        Получение наиболее популярных рабочих мест по количеству бронирований
        
        Args:
            limit: Максимальное количество результатов
            
        Returns:
            Список популярных рабочих мест
        """
        return self.db.query(Workspace).join(Booking).group_by(Workspace.id).order_by(
            desc(func.count(Booking.id))
        ).limit(limit).all()
    
    def get_bookings_by_month(self, year: int, month: int) -> List[Booking]:
        """
        Получение бронирований за конкретный месяц
        
        Args:
            year: Год
            month: Месяц
            
        Returns:
            Список бронирований за месяц
        """
        from datetime import datetime
        start_date = date(year, month, 1)
        
        # Определяем последний день месяца
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        return self.db.query(Booking).filter(
            and_(
                Booking.booking_date >= start_date,
                Booking.booking_date <= end_date
            )
        ).all()
    
    def cancel_booking(self, booking_id: int) -> bool:
        """
        Отмена бронирования
        
        Args:
            booking_id: ID бронирования
            
        Returns:
            True если отмена успешна
        """
        cancelled_status = self.db.query(Status).filter(Status.name == "cancelled").first()
        if not cancelled_status:
            return False
        
        booking = self.get_by_id(booking_id)
        if booking:
            booking.status_id = cancelled_status.id
            self.db.commit()
            return True
        return False
    
    def confirm_booking(self, booking_id: int) -> bool:
        """
        Подтверждение бронирования
        
        Args:
            booking_id: ID бронирования
            
        Returns:
            True если подтверждение успешно
        """
        confirmed_status = self.db.query(Status).filter(Status.name == "confirmed").first()
        if not confirmed_status:
            return False
        
        booking = self.get_by_id(booking_id)
        if booking:
            booking.status_id = confirmed_status.id
            self.db.commit()
            return True
        return False