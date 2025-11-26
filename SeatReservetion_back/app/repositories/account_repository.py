"""
Репозиторий для работы с моделью Account (аккаунты пользователей)
Обеспечивает доступ к данным аккаунтов в базе данных и бизнес-логику
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from datetime import datetime, date

from app.models.account import Account
from app.models.status import Status
from app.schemas.account import AccountSearchParams


class AccountRepository:
    """Репозиторий для работы с аккаунтами пользователей"""
    
    def __init__(self, db: Session):
        """Инициализация репозитория"""
        self.db = db
    
    def create(self, account_data: Dict[str, Any]) -> Account:
        """
        Создание нового аккаунта пользователя
        
        Args:
            account_data: Словарь с данными аккаунта
            
        Returns:
            Созданный объект Account
        """
        db_account = Account(**account_data)
        self.db.add(db_account)
        self.db.commit()
        self.db.refresh(db_account)
        return db_account
    
    def get_by_id(self, account_id: int) -> Optional[Account]:
        """
        Получение аккаунта по ID
        
        Args:
            account_id: ID аккаунта
            
        Returns:
            Объект Account или None
        """
        return self.db.query(Account).filter(Account.id == account_id).first()
    
    def get_by_login(self, login: str) -> Optional[Account]:
        """
        Получение аккаунта по логину
        
        Args:
            login: Логин пользователя
            
        Returns:
            Объект Account или None
        """
        return self.db.query(Account).filter(Account.login == login).first()
    
    def get_by_email(self, email: str) -> List[Account]:
        """
        Получение всех аккаунтов по email
        
        Args:
            email: Email пользователя
            
        Returns:
            Список аккаунтов
        """
        return self.db.query(Account).filter(Account.email == email).all()
    
    def update(self, account_id: int, account_data: Dict[str, Any]) -> Optional[Account]:
        """
        Обновление данных аккаунта
        
        Args:
            account_id: ID аккаунта
            account_data: Словарь с обновленными данными
            
        Returns:
            Обновленный объект Account или None
        """
        db_account = self.get_by_id(account_id)
        if db_account:
            for key, value in account_data.items():
                setattr(db_account, key, value)
            self.db.commit()
            self.db.refresh(db_account)
        return db_account
    
    def delete(self, account_id: int) -> bool:
        """
        Удаление аккаунта
        
        Args:
            account_id: ID аккаунта
            
        Returns:
            True если удаление успешно, False иначе
        """
        db_account = self.get_by_id(account_id)
        if db_account:
            self.db.delete(db_account)
            self.db.commit()
            return True
        return False
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Account]:
        """
        Получение всех аккаунтов с пагинацией
        
        Args:
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей
            
        Returns:
            Список аккаунтов
        """
        return self.db.query(Account).offset(skip).limit(limit).all()
    
    def search_accounts(self, search_params: AccountSearchParams) -> tuple[List[Account], int]:
        """
        Поиск и фильтрация аккаунтов с пагинацией
        
        Args:
            search_params: Параметры поиска
            
        Returns:
            Кортеж (список аккаунтов, общее количество)
        """
        query = self.db.query(Account).join(Status)
        
        # Применяем поиск
        if search_params.search:
            search_term = f"%{search_params.search.lower()}%"
            query = query.filter(
                or_(
                    Account.login.ilike(search_term),
                    Account.first_name.ilike(search_term),
                    Account.last_name.ilike(search_term),
                    Account.email.ilike(search_term)
                )
            )
        
        # Фильтр по статусу
        if search_params.status_id:
            query = query.filter(Account.status_id == search_params.status_id)
        
        # Фильтр по типу пользователя
        if search_params.is_admin is not None:
            query = query.filter(Account.is_admin == search_params.is_admin)
        
        # Подсчет общего количества
        total = query.count()
        
        # Сортировка
        sort_field_map = {
            "id": Account.id,
            "login": Account.login,
            "created_at": Account.created_at,
            "is_admin": Account.is_admin
        }
        
        sort_field = sort_field_map.get(search_params.sort_by, Account.created_at)
        if search_params.sort_order.lower() == "asc":
            query = query.order_by(asc(sort_field))
        else:
            query = query.order_by(desc(sort_field))
        
        # Пагинация
        offset = (search_params.page - 1) * search_params.per_page
        accounts = query.offset(offset).limit(search_params.per_page).all()
        
        return accounts, total
    
    def get_with_details(self, account_id: int) -> Optional[Account]:
        """
        Получение аккаунта с детальной информацией
        
        Args:
            account_id: ID аккаунта
            
        Returns:
            Объект Account с связанными данными или None
        """
        return self.db.query(Account).join(Status).filter(Account.id == account_id).first()
    
    def get_by_status_id(self, status_id: int) -> List[Account]:
        """
        Получение всех аккаунтов с определенным статусом
        
        Args:
            status_id: ID статуса
            
        Returns:
            Список аккаунтов
        """
        return self.db.query(Account).filter(Account.status_id == status_id).all()
    
    def get_admins(self) -> List[Account]:
        """
        Получение всех администраторов
        
        Returns:
            Список аккаунтов администраторов
        """
        return self.db.query(Account).filter(Account.is_admin == True).all()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Получение статистики по аккаунтам
        
        Returns:
            Словарь со статистикой
        """
        # Общее количество аккаунтов
        total = self.db.query(Account).count()
        
        # Количество администраторов
        admin_count = self.db.query(Account).filter(Account.is_admin == True).count()
        user_count = total - admin_count
        
        # Количество по статусам
        status_counts = {}
        statuses = self.db.query(Status).all()
        
        for status in statuses:
            count = self.db.query(Account).filter(Account.status_id == status.id).count()
            status_counts[status.name] = count
        
        # Активные/неактивные аккаунты
        active_status = self.db.query(Status).filter(Status.name == "active").first()
        active_accounts = self.db.query(Account).filter(
            Account.status_id == active_status.id
        ).count() if active_status else 0
        
        inactive_accounts = total - active_accounts
        
        return {
            "total_accounts": total,
            "admin_accounts": admin_count,
            "user_accounts": user_count,
            "active_accounts": active_accounts,
            "inactive_accounts": inactive_accounts,
            "by_status": status_counts
        }
    
    def exists(self, account_id: int) -> bool:
        """
        Проверка существования аккаунта
        
        Args:
            account_id: ID аккаунта
            
        Returns:
            True если аккаунт существует
        """
        return self.db.query(Account).filter(Account.id == account_id).first() is not None
    
    def check_login_exists(self, login: str, exclude_id: Optional[int] = None) -> bool:
        """
        Проверка существования логина
        
        Args:
            login: Логин для проверки
            exclude_id: ID аккаунта для исключения (при обновлении)
            
        Returns:
            True если логин существует
        """
        query = self.db.query(Account).filter(Account.login == login)
        if exclude_id:
            query = query.filter(Account.id != exclude_id)
        return query.first() is not None
    
    def get_accounts_with_bookings(self) -> List[Account]:
        """
        Получение аккаунтов с их бронированиями
        
        Returns:
            Список аккаунтов с бронированиями
        """
        return self.db.query(Account).join(Account.bookings).all()
    
    def get_recent_bookings(self, account_id: int, limit: int = 5) -> List[Account]:
        """
        Получение последних бронирований аккаунта
        
        Args:
            account_id: ID аккаунта
            limit: Максимальное количество бронирований
            
        Returns:
            Список аккаунтов с последними бронированиями
        """
        return self.db.query(Account).filter(Account.id == account_id).join(Account.bookings).order_by(
            desc(Account.bookings.property.primaryjoin.columns[1])
        ).limit(limit).all()