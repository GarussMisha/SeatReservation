"""
Главное FastAPI приложение для системы бронирования рабочих мест
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import create_tables, engine
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Создаем таблицы и инициализируем данные при запуске
    try:
        from app.core.database import create_and_initialize_tables
        create_and_initialize_tables()
    except Exception as e:
        print(f"⚠️  Ошибка при инициализации базы данных: {e}")
        print("🔄 Продолжаем запуск...")

    # Запускаем планировщик уведомлений
    try:
        from app.services.scheduler_service import start_notification_scheduler
        start_notification_scheduler(check_interval_minutes=5)
        print("✅ Планировщик уведомлений запущен (проверка каждые 5 мин)")
    except Exception as e:
        print(f"⚠️  Ошибка при запуске планировщика уведомлений: {e}")

    yield

    # Очистка при завершении работы
    print("👋 Завершение работы приложения")
    
    # Останавливаем планировщик
    try:
        from app.services.scheduler_service import stop_notification_scheduler
        stop_notification_scheduler()
        print("✅ Планировщик уведомлений остановлен")
    except Exception as e:
        print(f"⚠️  Ошибка при остановке планировщика: {e}")


# Создаем FastAPI приложение
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API для системы бронирования рабочих мест",
    debug=settings.debug,
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": f"Добро пожаловать в {settings.app_name}",
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Проверка состояния API"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Глобальный обработчик исключений"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Внутренняя ошибка сервера",
            "detail": str(exc) if settings.debug else "Произошла ошибка"
        }
    )


# Подключаем API роуты
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )