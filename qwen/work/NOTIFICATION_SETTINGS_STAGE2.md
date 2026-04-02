# ✅ Этап 2: Backend API для настроек уведомлений

## 📅 Дата: 1 апреля 2026

## 📊 Статус: ✅ ВЫПОЛНЕНО

---

## 1. Созданные файлы

### 1.1. API Routes

**`app/api/v1/routes/notification_settings.py`**

API endpoints для управления настройками уведомлений:

| Endpoint | Метод | Доступ | Описание |
|----------|-------|--------|----------|
| `/api/v1/my/settings` | GET | User | Получить мои настройки |
| `/api/v1/my/settings` | PUT | User | Обновить мои настройки |
| `/api/v1/admin/notification-settings` | GET | Admin | Получить глобальные настройки |
| `/api/v1/admin/notification-settings` | PUT | Admin | Обновить настройки SMTP |
| `/api/v1/admin/notification-settings/test` | POST | Admin | Тестовое письмо |

---

## 2. API Endpoints

### 2.1. Пользователь

#### Получить мои настройки

```bash
GET /api/v1/my/settings
Authorization: Bearer <token>
```

**Ответ:**
```json
{
  "user_id": 3,
  "email_enabled": true,
  "site_enabled": true
}
```

---

#### Обновить мои настройки

```bash
PUT /api/v1/my/settings
Authorization: Bearer <token>
Content-Type: application/json

{
  "email_enabled": false,
  "site_enabled": true
}
```

**Ответ:**
```json
{
  "user_id": 3,
  "email_enabled": false,
  "site_enabled": true
}
```

---

### 2.2. Администратор

#### Получить глобальные настройки

```bash
GET /api/v1/admin/notification-settings
Authorization: Bearer <admin-token>
```

**Ответ:**
```json
{
  "id": 1,
  "smtp_host": "smtp.resend.com",
  "smtp_port": 465,
  "smtp_user": "resend",
  "smtp_from_email": "onboarding@resend.dev",
  "smtp_from_name": "Seat Reservation System",
  "smtp_use_tls": true,
  "email_notifications_enabled": true
}
```

---

#### Обновить настройки SMTP

```bash
PUT /api/v1/admin/notification-settings
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_user": "parussmikle@gmail.com",
  "smtp_password": "app-password-1234",
  "smtp_from_email": "parussmikle@gmail.com",
  "smtp_from_name": "Seat Reservation",
  "smtp_use_tls": true,
  "email_notifications_enabled": true
}
```

---

#### Тестирование SMTP

```bash
POST /api/v1/admin/notification-settings/test
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "test_email": "parussmikle@gmail.com"
}
```

**Ответ:**
```json
{
  "success": true,
  "message": "Тестовое письмо успешно отправлено!",
  "sent_at": "2026-04-01T19:00:00"
}
```

---

## 3. Обновлённые файлы

| Файл | Изменения |
|------|-----------|
| `app/api/v1/router.py` | Добавлен импорт и регистрация `notification_settings_router` |

---

## 4. Проверка работы

### 4.1. Проверка импорта

```bash
cd SeatReservetion_back
venv\Scripts\python.exe -c "
from app.api.v1.routes.notification_settings import router
print('✅ API Routes импортируются корректно')
"
```

### 4.2. Запуск сервера

```bash
python run_server.py
```

**Проверка Swagger UI:**
1. Откройте http://localhost:8000/docs
2. Найдите секцию **"notification-settings"**
3. Проверьте endpoints:
   - `GET /my/settings`
   - `PUT /my/settings`
   - `GET /admin/notification-settings`
   - `PUT /admin/notification-settings`
   - `POST /admin/notification-settings/test`

---

## 5. Примеры использования

### 5.1. Пользователь отключает email уведомления

```bash
curl -X PUT http://localhost:8000/my/settings \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email_enabled": false}'
```

### 5.2. Админ настраивает Gmail SMTP

```bash
curl -X PUT http://localhost:8000/admin/notification-settings \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_user": "parussmikle@gmail.com",
    "smtp_password": "xxxx-xxxx-xxxx-xxxx",
    "smtp_from_email": "parussmikle@gmail.com",
    "smtp_from_name": "Seat Reservation",
    "smtp_use_tls": true
  }'
```

### 5.3. Админ тестирует SMTP

```bash
curl -X POST http://localhost:8000/admin/notification-settings/test \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"test_email": "parussmikle@gmail.com"}'
```

---

## 6. Следующие шаги

### Этап 3: Frontend (🟡 Средний приоритет)

**Файлы для создания:**
- `src/views/NotificationSettings.vue` — страница настроек пользователя
- `src/components/admin/NotificationSettings.vue` — страница настроек SMTP
- `src/stores/notificationSettings.js` — Pinia store

**Endpoints для интеграции:**
- `GET /api/v1/my/settings` — загрузка настроек
- `PUT /api/v1/my/settings` — сохранение настроек
- `GET /api/v1/admin/notification-settings` — загрузка SMTP
- `PUT /api/v1/admin/notification-settings` — сохранение SMTP
- `POST /api/v1/admin/notification-settings/test` — тестовое письмо

---

## 7. Связанные документы

- [NOTIFICATION_SETTINGS_STAGE1.md](NOTIFICATION_SETTINGS_STAGE1.md) — Этап 1 (База данных)
- [NOTIFICATION_CODE_REVIEW_2026.md](NOTIFICATION_CODE_REVIEW_2026.md) — полное ревью
- [NOTIFICATION_API.md](NOTIFICATION_API.md) — документация системы уведомлений

---

**Этап 2 завершён!** ✅

**Следующий шаг:** Реализация Frontend (Этап 3).
