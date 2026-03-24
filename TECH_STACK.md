# 🛠️ Технологический стек проекта SeatReservation

## 📋 Обзор

Проект **SeatReservation** - это полнофункциональное веб-приложение для бронирования рабочих мест, построенное на современном технологическом стеке с разделением на фронтенд и бэкенд.

---

## 🎨 Frontend (SeatReservetion_front)

### Основные технологии

| Технология | Версия | Описание |
|------------|--------|----------|
| **Vue.js** | 3.5.22 | Прогрессивный JavaScript-фреймворк для построения пользовательских интерфейсов |
| **Vite** | 7.1.11 | Быстрый сборщик и dev-сервер нового поколения |
| **Vue Router** | 4.6.3 | Официальный роутер для Vue.js (навигация между страницами) |
| **Pinia** | 3.0.3 | Официальное хранилище состояний для Vue 3 (замена Vuex) |
| **Axios** | 1.13.1 | HTTP-клиент для выполнения API запросов |

### Инструменты разработки

- **@vitejs/plugin-vue** (6.0.1) - Официальный плагин Vue для Vite
- **vite-plugin-vue-devtools** (8.0.3) - Интеграция Vue DevTools в браузере
- **Node.js** - Минимальная версия: 20.19.0 или 22.12.0+

### Архитектурные особенности

- **SPA (Single Page Application)** - Одностраничное приложение
- **Composition API** - Современный подход Vue 3
- **Модульная структура**:
  - `components/` - Переиспользуемые компоненты
  - `views/` - Страницы приложения
  - `router/` - Конфигурация маршрутизации
  - `stores/` - Pinia хранилища состояний
  - `services/` - API клиенты и бизнес-логика
- **Алиасы путей**: `@/` указывает на `src/`

### Скрипты запуска front

```bash
cd SeatReservetion_front
npm install
npm run dev      # Запуск dev-сервера (обычно http://localhost:5173)
npm run build    # Сборка для продакшена
npm run preview  # Предпросмотр production-сборки
```

---

## ⚙️ Backend (SeatReservetion_back)

### Основные технологии

| Технология | Версия | Описание |
|------------|--------|----------|
| **FastAPI** | latest | Современный веб-фреймворк для создания API на Python |
| **SQLAlchemy** | latest | ORM (Object-Relational Mapping) для работы с базой данных |
| **Uvicorn** | latest | ASGI сервер для запуска FastAPI приложения |
| **Pydantic** | latest | Валидация данных и настройки через Settings |
| **Python** | 3.8+ | Язык программирования |

### База данных

- **SQLite** (по умолчанию) - Легковесная встроенная БД для разработки
- **PostgreSQL** (поддержка) - Через psycopg2-binary для продакшена

### Безопасность и аутентификация

| Библиотека | Назначение |
|------------|------------|
| **python-jose[cryptography]** | Генерация и валидация JWT токенов |
| **passlib[bcrypt]** (1.7.4) | Хеширование паролей |
| **bcrypt** (4.0.1) | Криптографические функции |
| **python-multipart** | Обработка форм и файлов |

### Миграции и конфигурация

- **Alembic** - Инструмент для миграций базы данных
- **pydantic-settings** - Управление настройками через .env файлы

### Архитектура бэкенда

```
┌─────────────────────────────────────────┐
│         FastAPI Application             │
├─────────────────────────────────────────┤
│  API Routes (/api/v1/...)               │
│  ├── accounts (CRUD + auth)             │
│  ├── rooms (CRUD)                       │
│  ├── workspaces (CRUD)                  │
│  ├── bookings (CRUD)                    │
│  ├── statuses (список)                  │
│  └── sync (синхронизация)               │
├─────────────────────────────────────────┤
│  Services (бизнес-логика)               │
│  └── booking_status_sync.py             │
├─────────────────────────────────────────┤
│  Repositories (доступ к данным)         │
│  ├── account_repository                 │
│  ├── booking_repository                 │
│  └── workspace_repository               │
├─────────────────────────────────────────┤
│  Models (SQLAlchemy ORM)                │
│  ├── Account                            │
│  ├── Room                               │
│  ├── Workspace                          │
│  ├── Booking                            │
│  └── Status                             │
├─────────────────────────────────────────┤
│  Schemas (Pydantic валидация)           │
│  └── Request/Response модели            │
├─────────────────────────────────────────┤
│  Core (ядро)                            │
│  ├── config.py (настройки)              │
│  ├── database.py (подключение)          │
│  └── security.py (JWT, bcrypt)          │
└─────────────────────────────────────────┘
         ↓
    SQLite / PostgreSQL
```

### Паттерны и подходы

- **Repository Pattern** - Абстракция слоя работы с данными
- **Dependency Injection** - Через FastAPI зависимости (`Depends`)
- **Lifespan Events** - Инициализация БД при старте
- **CORS Middleware** - Для взаимодействия с фронтендом
- **Global Exception Handler** - Централизованная обработка ошибок
- **Authentication Flow**:
  - Регистрация/логин
  - JWT-подобные токены
  - Роли: Admin / User

### API документация

FastAPI автоматически генерирует документацию:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Скрипты запуска back:

```bash
cd SeatReservetion_back
python -m venv venv 
venv\Scripts\activate

pip install -r requeriments

# Обычный запуск
python start.py

# Пересоздание БД
python start.py --new

# Создание тестового админа
python create_test_user.py
```

---

## 🔗 Интеграция Frontend ↔ Backend

### Взаимодействие

```
Vue.js Frontend (port 5173)
        ↓ HTTP/HTTPS
     Axios
        ↓
FastAPI Backend (port 8000)
        ↓
   SQLAlchemy
        ↓
  SQLite/PostgreSQL
```

### CORS конфигурация

Backend настроен на прием запросов от фронтенда:
```python
ALLOWED_ORIGINS=[
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174"
]
```

### Аутентификация

1. Frontend отправляет credentials → `/api/v1/accounts/login`
2. Backend возвращает токен
3. Frontend сохраняет токен (Pinia store)
4. Все последующие запросы содержат `Authorization: Bearer {token}`

---

### Тестовые данные

После первого запуска бэкенда создается администратор:
- **Login**: `admin`
- **Password**: `admin123`

---

## 🏗️ Дополнительные инструменты

### Версионность

- **Git** - Система контроля версий
- **Node.js** (20.19.0+) - Runtime для фронтенда
- **Python** (3.8+) - Runtime для бэкенда

### IDE / Редакторы

Рекомендуемые расширения:
- **Vue**: Volar (официальное расширение для Vue 3)
- **Python**: Pylance, Python Extension Pack
- **HTTP**: REST Client или Thunder Client

### Будущие улучшения

- [ ] **Docker** - Контейнеризация приложения
- [ ] **Docker Compose** - Оркестрация frontend + backend + DB
- [ ] **Nginx** - Reverse proxy для продакшена
- [ ] **pytest** - Unit и интеграционные тесты
- [ ] **Vitest** - Тесты для Vue компонентов
- [ ] **CI/CD** - GitHub Actions / GitLab CI
- [ ] **TypeScript** - Типизация для frontend
- [ ] **Redis** - Кеширование и сессии

---

## 📊 Сравнение стека

| Аспект | Технология | Альтернативы |
|--------|------------|--------------|
| Frontend Framework | Vue 3 | React, Angular, Svelte |
| Frontend Build Tool | Vite | Webpack, Parcel, Rollup |
| State Management | Pinia | Vuex, Redux, Zustand |
| Backend Framework | FastAPI | Django, Flask, Express.js |
| ORM | SQLAlchemy | Prisma, TypeORM, Sequelize |
| Database | SQLite/PostgreSQL | MySQL, MongoDB, Redis |
| Authentication | JWT (python-jose) | OAuth2, Auth0, Firebase Auth |

---

## 🎯 Ключевые особенности стека

### Преимущества

✅ **Производительность**: Vite для быстрой разработки, FastAPI для быстрой обработки API
✅ **Типобезопасность**: Pydantic схемы на бэкенде
✅ **Современность**: Vue 3 Composition API, FastAPI async
✅ **Автодокументация**: Swagger/ReDoc из коробки
✅ **Масштабируемость**: Модульная архитектура
✅ **Безопасность**: bcrypt, JWT, CORS
✅ **DX (Developer Experience)**: HMR, автоперезагрузка, devtools

### Применение

Этот стек идеален для:
- SaaS приложений
- Внутренних корпоративных систем
- MVP и стартапов
- Систем бронирования и управления ресурсами

---

**Документация актуальна на**: 2026
**Версия проекта**: 1.0.0
