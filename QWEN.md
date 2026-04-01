# SeatReservation — Система бронирования рабочих мест

## 📋 Обзор проекта

**SeatReservation** — это полнофункциональное веб-приложение для бронирования рабочих мест с визуальным редактором помещений и интерактивной картой бронирования.

### Архитектура

```
SeatReservation/
├── SeatReservetion_front/     # Vue.js 3 + Vite frontend
├── SeatReservetion_back/      # FastAPI backend
├── run_server.py              # Скрипт управления запуском
└── qwen/work/                 # Рабочие заметки разработки
```

---

## 🚀 Быстрый старт

### Запуск сервера (рекомендуемый способ)

```bash
# Обычный запуск (проверяет наличие БД)
python run_server.py

# Запуск с пересозданием БД
python run_server.py --new
```

### Ручной запуск компонентов

**Backend:**
```bash
cd SeatReservetion_back
venv\Scripts\activate
pip install -r requirements.txt
python start.py --new  # Пересоздание БД с тестовым админом
```

**Frontend:**
```bash
cd SeatReservetion_front
npm install
npm run dev  # http://localhost:5173
```

### Тестовые учётные данные

| Роль | Логин | Пароль | Email |
|------|-------|--------|-------|
| Admin | `admin` | `admin123` | `admin@example.com` |

---

## 🛠️ Технологический стек

### Frontend (SeatReservetion_front)

| Технология | Версия | Назначение |
|------------|--------|------------|
| **Vue.js** | 3.5.22 | UI фреймворк (Composition API) |
| **Vite** | 7.1.11 | Сборщик и dev-сервер |
| **Pinia** | 3.0.3 | Хранилище состояний |
| **Vue Router** | 4.6.3 | Маршрутизация |
| **Vue Konva** | 3.1.2 | 2D-графика (canvas/SVG) |
| **Axios** | 1.13.1 | HTTP-клиент |

**Структура frontend:**
```
src/
├── components/
│   ├── admin/           # Админ-панель
│   ├── dashboard/       # Дашборд бронирования
│   ├── room-editor/     # Редактор помещений
│   ├── Header.vue
│   └── ...
├── views/
│   ├── Dashboard.vue
│   ├── Login.vue
│   ├── Profile.vue
│   └── ...
├── stores/
│   ├── auth.js          # Аутентификация
│   ├── reservations.js  # Бронирования
│   ├── roomEditor.js    # Состояние редактора
│   └── ...
├── services/
│   ├── api.js           # API клиенты
│   └── ...
└── router/
```

### Backend (SeatReservetion_back)

| Технология | Назначение |
|------------|------------|
| **FastAPI** | Веб-фреймворк |
| **SQLAlchemy** | ORM |
| **SQLite** | БД (по умолчанию) |
| **Pydantic** | Валидация данных |
| **python-jose** | JWT токены |
| **passlib[bcrypt]** | Хеширование паролей |
| **APScheduler** | Планировщик уведомлений |

**Структура backend:**
```
app/
├── api/v1/routes/
│   ├── account.py       # CRUD аккаунтов + auth
│   ├── room.py          # CRUD помещений + plan
│   ├── workspace.py     # CRUD рабочих мест
│   ├── booking.py       # CRUD бронирований
│   └── ...
├── models/
│   ├── account.py
│   ├── room.py
│   ├── workspace.py
│   ├── booking.py
│   ├── room_object.py   # Объекты на плане (туалеты, кухня...)
│   ├── wall.py          # Стены
│   └── ...
├── repositories/        # Data Access Layer
├── schemas/             # Pydantic модели
└── services/
    └── scheduler_service.py  # Уведомления
```

---

## 📁 Ключевые файлы конфигурации

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
VITE_DEV_MODE=true
```

### Backend (.env)
```env
DATABASE_URL=sqlite:///./seat_reservation.db
SECRET_KEY=<ваш-секретный-ключ>
ALLOWED_ORIGINS=["http://localhost:5173", ...]
```

---

## 🏗️ Архитектурные особенности

### Frontend

**State Management (Pinia):**
- `authStore` — аутентификация, токен, пользователь
- `reservationsStore` — бронирования
- `roomEditorStore` — состояние редактора помещений
- `notificationsStore` — уведомления

**Маршруты:**
| Путь | Компонент | Доступ |
|------|-----------|--------|
| `/login` | Login | Guest |
| `/dashboard` | Dashboard | Auth |
| `/profile` | Profile | Auth |
| `/admin` | AdminPanel | Admin |
| `/room-editor/:roomId` | RoomEditor | Admin |
| `/notifications` | Notifications | Auth |

**Особенности UI:**
- Dashboard отображает рабочие места с SVG-иконкой `desktop.svg` (60% размера)
- SVG-объекты (туалеты, кухня) отображаются с центрированием через `translate(centerX, centerY)`
- Vue Konva используется для интерактивного плана помещения

### Backend

**API Endpoints (префикс `/api/v1`):**
- `/accounts/*` — аккаунты и аутентификация
- `/rooms/*` — помещения (включая `/plan` для графического плана)
- `/workspaces/*` — рабочие места
- `/bookings/*` — бронирования
- `/statuses` — список статусов
- `/health` — проверка состояния

**Модели данных:**
- `Account` — пользователь (login, password_hash, is_admin, status_id)
- `Room` — помещение (name, address, description)
- `Workspace` — рабочее место (name, room_id, is_active)
- `Booking` — бронирование (account_id, workspace_id, date, status_id)
- `RoomObject` — объекты на плане (туалеты, кухня, раздевалка)
- `Wall`, `Door`, `Window` — элементы плана помещения

**Безопасность:**
- bcrypt хеширование паролей
- JWT-подобные токены
- CORS middleware
- Глобальный exception handler

---

## 🔧 Скрипты и команды

### Frontend
```bash
npm run dev      # Dev-сервер (Vite)
npm run build    # Сборка продакшена
npm run preview  # Preview сборки
npm test         # Vitest тесты
```

### Backend
```bash
python start.py           # Запуск с инициализацией БД
python start.py --new     # Пересоздание БД
python create_test_user.py # Создать тестового админа
```

### Управление сервером
```bash
python run_server.py      # Запуск (проверка БД)
python run_server.py -n   # Запуск с пересозданием БД
```

---

## 🧪 Тестирование

**Backend тесты:**
```bash
cd SeatReservetion_back
python test_new_api.py
python test_room_editor_api.py
```

**Frontend тесты:**
```bash
cd SeatReservetion_front
npm test
```

**API документация:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health: http://localhost:8000/health

---

## 📝 Заметки разработки

### Рабочие заметки
Хранятся в `./qwen/work/` — создавайте файлы для фиксации изменений, багов, решений.

### Журнал изменений
Используйте навык `dev-log` для автоматического ведения журнала в `./qwen/work/QWEN_DEV_LOG.md`.

### Обновление документации
- `TECH_STACK.md` — детальное описание стека
- `TEST_REPORT.md` — отчёты о тестировании
- Для обновления README/архитектуры используйте навык `readme-sync`

---

## 🎯 Основные фичи

1. **Визуальный редактор помещений** — рисование стен, размещение рабочих мест и объектов
2. **Интерактивный план** — бронирование через клик на плане помещения (vue-konva)
3. **Ролевая модель** — Admin/User с разграничением прав
4. **Уведомления** — планировщик APScheduler для напоминаний
5. **Статусы бронирований** — настраиваемая система статусов

---

## ⚠️ Известные ограничения

- SQLite по умолчанию (не для production high-load)
- OpenAPI может кэшировать endpoints (требуется перезапуск с --reload)
- Windows: возможны проблемы с кодировкой в консоли

---

## 📚 Полезные ссылки

- [Технологический стек](TECH_STACK.md)
- [Отчёт о тестировании](TEST_REPORT.md)
- [Backend README](SeatReservetion_back/README.md)
- [Схема БД](SeatReservetion_back/DATABASE_SCHEMA.md)

---

**Версия проекта:** 1.0.0  
**Последнее обновление:** Апрель 2026
