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
from .room_object import RoomObject
from .workspace_on_plan import WorkspaceOnPlan
from .wall import Wall
from .door import Door
from .window import Window

__all__ = [
    "Base",
    "Account",
    "Booking",
    "Notification",
    "Room",
    "Status",
    "Workspace",
    "RoomObject",
    "WorkspaceOnPlan",
    "Wall",
    "Door",
    "Window",
]