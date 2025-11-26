"""
Главный роутер для API v1
Объединяет все маршруты версии 1 API системы бронирования рабочих мест
Подключает все основные API эндпоинты для управления аккаунтами,
рабочими местами, помещениями и бронированиями
"""
from fastapi import APIRouter

# Импортируем все роуты
from app.api.v1.routes.account import router as account_router
from app.api.v1.routes.workspace import router as workspace_router
from app.api.v1.routes.room import router as room_router
from app.api.v1.routes.booking import router as booking_router
from app.api.v1.routes.sync import router as sync_router
from app.api.v1.routes.status import router as status_router

# Создаем главный роутер API v1
api_router = APIRouter()

# Подключаем все роуты с соответствующими префиксами и тегами
api_router.include_router(account_router, prefix="/accounts", tags=["accounts"])
api_router.include_router(room_router, prefix="/rooms", tags=["rooms"])
api_router.include_router(workspace_router, prefix="/workspaces", tags=["workspaces"])
api_router.include_router(booking_router, prefix="/bookings", tags=["bookings"])
api_router.include_router(sync_router, prefix="/sync", tags=["sync"])
api_router.include_router(status_router, prefix="/statuses", tags=["statuses"])