# SeatReservation API

REST API для системы бронирования рабочих мест, построенное на **FastAPI**.

## 📁 Актуальная структура проекта

```
SeatReservetion_back/
├── .env                           # Переменные окружения (DATABASE_URL=sqlite:///./seat_reservation.db)
├── create_test_user.py            # Скрипт создания тестового администратора
├── DATABASE_SCHEMA.md             # Детальная схема базы данных
├── README.md                      # Документация проекта
├── requirements.txt               # Зависимости Python (FastAPI, SQLAlchemy, etc.)
├── start.py                       # Основной скрипт запуска (с опцией --new для пересоздания БД)
└── app/                           # Основная папка приложения
    ├── __init__.py
    ├── main.py                    # Точка входа FastAPI (с lifespan, CORS, health checks)
    ├── api/
    │   ├── __init__.py
    │   ├── deps.py                # Зависимости (get_db, get_current_user)
    │   └── v1/
    │       ├── __init__.py
    │       ├── router.py          # Объединение роутеров (/api/v1)
    │       └── routes/
    │           ├── account.py     # CRUD аккаунтов, auth (login/register)
    │           ├── booking.py     # CRUD бронирований
    │           ├── room.py        # CRUD помещений (комнат)
    │           ├── status.py      # Управление статусами
    │           ├── sync.py        # Синхронизация статусов бронирований
    │           └── workspace.py   # CRUD рабочих мест
    ├── core/
    │   ├── __init__.py
    │   ├── base.py                # Базовый класс моделей (id, created_at)
    │   ├── config.py              # Pydantic Settings (.env), константы
    │   ├── database.py            # Engine, Session, create_tables, init data, admin
    │   └── security.py            # Хеширование паролей (bcrypt), токены (custom JWT-like)
    ├── models/                    # SQLAlchemy модели
    │   ├── __init__.py
    │   ├── base.py                # BaseModel
    │   ├── account.py             # Аккаунты (login, password_hash, is_admin, FIO, email)
    │   ├── booking.py             # Бронирования (date, account_id, workspace_id, status)
    │   ├── room.py                # Помещения (name, address, description, status)
    │   ├── status.py              # Универсальные статусы (name, description)
    │   └── workspace.py           # Рабочие места (name, is_active, room_id)
    ├── repositories/              # Репозитории (Data Access Layer)
    │   ├── __init__.py
    │   ├── account_repository.py
    │   ├── booking_repository.py
    │   └── workspace_repository.py
    ├── schemas/                   # Pydantic схемы (Create, Update, Response)
    │   ├── __init__.py
    │   ├── account.py
    │   ├── booking.py
    │   ├── room.py
    │   └── workspace.py
    └── services/                  # Бизнес-логика
        └── booking_status_sync.py # Синхронизация статусов бронирований
```

## ✅ Полностью реализовано

### Основной функционал
- **База данных**: SQLite (по умолчанию) / PostgreSQL, авто-создание таблиц и статусов при запуске
- **Модели**: Account, Status, Room, Workspace, Booking (см. [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md))
- **Аутентификация**: Регистрация/логин, JWT-подобные токены, роли (admin/user)
- **API эндпоинты** (/api/v1/...):
  | Префикс | Описание | Аутентификация |
  |---------|----------|----------------|
  | /accounts | CRUD аккаунтов, login/register | Частично |
  | /rooms | CRUD помещений | Да |
  | /workspaces | CRUD рабочих мест | Да |
  | /bookings | CRUD бронирований | Да |
  | /statuses | Список статусов | Нет |
  | /sync | Синхронизация статусов | Admin |
- **Безопасность**: bcrypt хеши, CORS, глобальный exception handler
- **Инициализация**: Авто-создание тестового admin (login: `admin`, пароль: `admin123`)

### Тестовый администратор
```
python create_test_user.py
# Или автоматически при первом запуске start.py
```

## 🚀 Быстрый запуск

```bash
# 1. Установка зависимостей
pip install -r requirements.txt

# 2. Запуск (создаст БД + admin)
python start.py

# Пересоздать БД полностью
python start.py --new

# API Docs: http://localhost:8000/docs
# Health: http://localhost:8000/health
```

**Тестовый вход**:
- Login: `admin`
- Password: `admin123`
- Роль: Admin

## 🔧 Конфигурация (.env)

```env
DATABASE_URL=sqlite:///./seat_reservation.db
SECRET_KEY=your-secret-key-here  # Изменить!
ALLOWED_ORIGINS=["http://localhost:5173"]
DEBUG=True
```

## 📊 Схема БД

Детальная [схема таблиц и связей](DATABASE_SCHEMA.md) с примерами статусов.

## 🏗️ Архитектура

```
Request → API Routes → Repositories → Models (SQLAlchemy) → SQLite/PG
     ↓
Pydantic Schemas (валидация) + Security (auth)
```

- **Repository Pattern**: Абстракция БД
- **Lifespan events**: Авто-init БД
- **CORS**: Для фронтенда (Vite/Vue)
- **Pagination/Search**: В репозиториях

## 📈 Дорожная карта (будущее)

- [ ] Docker (Dockerfile + docker-compose.yml)
- [ ] Alembic миграции
- [ ] Unit тесты (pytest)
- [ ] Rate limiting
- [ ] Email уведомления
- [ ] Frontend интеграция

## 🔗 Полезные ссылки

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [Pydantic](https://docs.pydantic.dev/)

**Версия**: 1.0.0 (полностью рабочая)