"""
Импорт всех Pydantic схем
"""
from .account import (
    AccountCreate,
    AccountUpdate,
    AccountResponse,
    AccountSearchParams,
    AccountLogin,
    AccountLoginResponse,
)
from .booking import (
    BookingCreate,
    BookingUpdate,
    BookingResponse,
    BookingSearchParams,
    BookingStats,
)
from .room import (
    RoomCreate,
    RoomUpdate,
    RoomResponse,
    RoomSearchParams,
    RoomStats,
    RoomBulkUpdate,
)
from .workspace import (
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceResponse,
    WorkspaceSearchParams,
    WorkspaceStats,
)
from .notification import (
    NotificationCreateBase,
    NotificationScheduleCreate,
    NotificationResponse,
    NotificationListResponse,
    NotificationStats,
    NotificationBulkSendRequest,
    NotificationFilter,
)

__all__ = [
    # Account
    "AccountCreate",
    "AccountUpdate",
    "AccountResponse",
    "AccountSearchParams",
    "AccountLogin",
    "AccountLoginResponse",
    # Booking
    "BookingCreate",
    "BookingUpdate",
    "BookingResponse",
    "BookingSearchParams",
    "BookingStats",
    # Room
    "RoomCreate",
    "RoomUpdate",
    "RoomResponse",
    "RoomSearchParams",
    "RoomStats",
    "RoomBulkUpdate",
    # Workspace
    "WorkspaceCreate",
    "WorkspaceUpdate",
    "WorkspaceResponse",
    "WorkspaceSearchParams",
    "WorkspaceStats",
    # Notification
    "NotificationCreateBase",
    "NotificationScheduleCreate",
    "NotificationResponse",
    "NotificationListResponse",
    "NotificationStats",
    "NotificationBulkSendRequest",
    "NotificationFilter",
]
