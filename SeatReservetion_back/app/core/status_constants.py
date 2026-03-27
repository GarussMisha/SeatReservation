"""
Константы статусов для всех сущностей системы
Определяют какие статусы разрешены для каждой сущности
"""

# =============================================================================
# ACCOUNT STATUSES (Статусы пользователей)
# =============================================================================
class AccountStatuses:
    """Статусы аккаунтов пользователей"""
    ACTIVE = 1      # Активен
    INACTIVE = 2    # Не активен
    BLOCKED = 3     # Заблокирован
    ON_LEAVE = 4    # В отпуске
    SICK = 5        # На больничном
    TERMINATED = 6  # Уволен
    
    # Список разрешённых статусов для Account
    ALLOWED = [ACTIVE, INACTIVE, BLOCKED, ON_LEAVE, SICK, TERMINATED]
    
    # Названия
    NAMES = {
        ACTIVE: 'active',
        INACTIVE: 'inactive',
        BLOCKED: 'blocked',
        ON_LEAVE: 'on_leave',
        SICK: 'sick',
        TERMINATED: 'terminated'
    }


# =============================================================================
# ROOM STATUSES (Статусы помещений)
# =============================================================================
class RoomStatuses:
    """Статусы помещений"""
    ACTIVE = 1      # Активно
    INACTIVE = 2    # Не активно
    
    # Список разрешённых статусов для Room
    ALLOWED = [ACTIVE, INACTIVE]
    
    # Названия
    NAMES = {
        ACTIVE: 'active',
        INACTIVE: 'inactive'
    }


# =============================================================================
# WORKSPACE STATUSES (Статусы рабочих мест)
# =============================================================================
class WorkspaceStatuses:
    """Статусы рабочих мест"""
    FREE = 10           # Свободно
    OCCUPIED = 11       # Занято
    INACTIVE = 2        # Не активно
    AVAILABLE = 7       # Доступно (аналог free)
    MAINTENANCE = 8     # На обслуживании
    UNAVAILABLE = 9     # Недоступно
    
    # Список разрешённых статусов для Workspace
    ALLOWED = [FREE, OCCUPIED, INACTIVE, AVAILABLE, MAINTENANCE, UNAVAILABLE]
    
    # Названия
    NAMES = {
        FREE: 'free',
        OCCUPIED: 'occupied',
        INACTIVE: 'inactive',
        AVAILABLE: 'available',
        MAINTENANCE: 'maintenance',
        UNAVAILABLE: 'unavailable'
    }
    
    # Маппинг на frontend статусы
    FRONTEND_MAP = {
        FREE: 'available',
        AVAILABLE: 'available',
        OCCUPIED: 'booked',
        INACTIVE: 'inactive',
        MAINTENANCE: 'inactive',
        UNAVAILABLE: 'inactive'
    }


# =============================================================================
# BOOKING STATUSES (Статусы бронирований)
# =============================================================================
class BookingStatuses:
    """Статусы бронирований"""
    PENDING = 12      # Ожидает
    CONFIRMED = 13    # Подтверждено (активно)
    CANCELLED = 14    # Отменено
    COMPLETED = 15    # Завершено
    
    # Список разрешённых статусов для Booking
    ALLOWED = [PENDING, CONFIRMED, CANCELLED, COMPLETED]
    
    # Названия
    NAMES = {
        PENDING: 'pending',
        CONFIRMED: 'confirmed',
        CANCELLED: 'cancelled',
        COMPLETED: 'completed'
    }
    
    # Активные статусы (бронь считается активной)
    ACTIVE = [PENDING, CONFIRMED]
    
    # Неактивные статусы (бронь не активна)
    INACTIVE = [CANCELLED, COMPLETED]


# =============================================================================
# NOTIFICATION STATUSES (Статусы уведомлений)
# =============================================================================
class NotificationStatuses:
    """Статусы уведомлений"""
    PENDING = 12      # Ожидает отправки
    SENT = 16         # Отправлено
    FAILED = 17       # Не отправлено
    CANCELLED = 14    # Отменено
    
    # Список разрешённых статусов для Notification
    ALLOWED = [PENDING, SENT, FAILED, CANCELLED]
    
    # Названия
    NAMES = {
        PENDING: 'pending',
        SENT: 'sent',
        FAILED: 'failed',
        CANCELLED: 'cancelled'
    }


# =============================================================================
# WORKSPACE ON PLAN STATUSES (Статусы рабочих мест на плане)
# =============================================================================
class WorkspaceOnPlanStatuses:
    """Статусы рабочих мест на плане"""
    FREE = 10           # Свободно
    OCCUPIED = 11       # Занято
    INACTIVE = 2        # Не активно
    
    # Список разрешённых статусов для WorkspaceOnPlan
    ALLOWED = [FREE, OCCUPIED, INACTIVE]
    
    # Названия
    NAMES = {
        FREE: 'free',
        OCCUPIED: 'occupied',
        INACTIVE: 'inactive'
    }


# =============================================================================
# HELPER FUNCTIONS (Вспомогательные функции)
# =============================================================================

def get_allowed_statuses(entity_type: str) -> list:
    """
    Получить список разрешённых статусов для сущности
    
    Args:
        entity_type: Тип сущности ('account', 'room', 'workspace', 'booking', 'notification')
    
    Returns:
        Список разрешённых ID статусов
    """
    mapping = {
        'account': AccountStatuses.ALLOWED,
        'room': RoomStatuses.ALLOWED,
        'workspace': WorkspaceStatuses.ALLOWED,
        'booking': BookingStatuses.ALLOWED,
        'notification': NotificationStatuses.ALLOWED,
        'workspace_on_plan': WorkspaceOnPlanStatuses.ALLOWED
    }
    
    return mapping.get(entity_type.lower(), [])


def is_valid_status(entity_type: str, status_id: int) -> bool:
    """
    Проверить валидность статуса для сущности
    
    Args:
        entity_type: Тип сущности
        status_id: ID статуса
    
    Returns:
        True если статус валиден
    """
    return status_id in get_allowed_statuses(entity_type)


def get_status_name(entity_type: str, status_id: int) -> str:
    """
    Получить название статуса для сущности
    
    Args:
        entity_type: Тип сущности
        status_id: ID статуса
    
    Returns:
        Название статуса или None
    """
    mapping = {
        'account': AccountStatuses.NAMES,
        'room': RoomStatuses.NAMES,
        'workspace': WorkspaceStatuses.NAMES,
        'booking': BookingStatuses.NAMES,
        'notification': NotificationStatuses.NAMES,
        'workspace_on_plan': WorkspaceOnPlanStatuses.NAMES
    }
    
    status_dict = mapping.get(entity_type.lower(), {})
    return status_dict.get(status_id)
