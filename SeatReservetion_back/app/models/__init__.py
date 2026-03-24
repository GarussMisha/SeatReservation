"""
Импорт всех моделей базы данных
"""
from app.core.base import Base
from .account import Account
from .booking import Booking
from .notification import Notification
from .room import Room
from .status import Status
from .workspace import Workspace

__all__ = [
    "Base",
    "Account",
    "Booking",
    "Notification",
    "Room",
    "Status",
    "Workspace",
]