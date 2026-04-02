# 📬 Система управления уведомлениями — ПОЛНАЯ ДОКУМЕНТАЦИЯ

## 📅 Дата обновления: 1 апреля 2026

## 📊 Статус: ✅ ПОЛНОСТЬЮ РЕАЛИЗОВАНО

---

## 1. Архитектура системы

```
┌─────────────────────────────────────────────────────────┐
│  Пользователь (Frontend)                                │
│  /profile                                               │
│  ☑ Email уведомления                                    │
│  ☑ Уведомления в ЛК                                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ API: GET/PUT /api/v1/notification-settings/my/settings
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  Backend (notification_service.py)                      │
│                                                          │
│  1. Проверка настроек пользователя                      │
│     - email_enabled = True? → Отправить email           │
│     - site_enabled = True? → Создать в БД               │
│                                                          │
│  2. Если оба отключены → Игнорировать                   │
│                                                          │
│  3. Генерация данных (единожды)                         │
│     - notification_data = get_booking_cancelled_data() │
│                                                          │
│  4. Сохранение в БД (если site_enabled)                 │
│     - notification.message = json.dumps(data)           │
│                                                          │
│  5. Отправка email (если email_enabled)                 │
│     - email_service.send_email(html_content)            │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Настройки уведомлений

### 2.1. Расположение

**Страница профиля:**
```
http://localhost:5173/profile
```

**Компонент:**
```
SeatReservetion_front/src/components/profile/NotificationSettings.vue
```

### 2.2. Переключатели

| Настройка | Описание | Влияние |
|-----------|----------|---------|
| **Email уведомления** | Получать уведомления на email | Отправка email писем |
| **Уведомления в ЛК** | Показывать в браузере | Создание записей в БД |

### 2.3. Логика работы

| Email | ЛК | Результат |
|-------|----|-----------|
| ❌ | ❌ | Уведомление **игнорируется** |
| ❌ | ✅ | Только запись в БД (в ЛК) |
| ✅ | ❌ | Только email |
| ✅ | ✅ | И email, и запись в БД |

---

## 3. База данных

### 3.1. Таблица настроек пользователя

```sql
CREATE TABLE user_notification_settings (
    id INTEGER PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    email_enabled BOOLEAN DEFAULT TRUE,
    site_enabled BOOLEAN DEFAULT TRUE,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES accounts(id)
);
```

### 3.2. Таблица уведомлений

```sql
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY,
    notification_type VARCHAR(50) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,  -- JSON для ЛК
    scheduled_at DATETIME,
    sent_at DATETIME,
    status_id INTEGER NOT NULL,
    user_id INTEGER,
    created_by_id INTEGER,
    created_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES accounts(id),
    FOREIGN KEY (status_id) REFERENCES statuses(id)
);
```

---

## 4. API Endpoints

### 4.1. Пользователь

**Получить мои настройки:**
```bash
GET /api/v1/notification-settings/my/settings
Authorization: Bearer <token>

# Ответ:
{
  "user_id": 3,
  "email_enabled": true,
  "site_enabled": true
}
```

**Обновить мои настройки:**
```bash
PUT /api/v1/notification-settings/my/settings
Authorization: Bearer <token>
Content-Type: application/json

{
  "email_enabled": false,
  "site_enabled": true
}

# Ответ:
{
  "user_id": 3,
  "email_enabled": false,
  "site_enabled": true
}
```

### 4.2. Администратор (SMTP)

**Получить настройки SMTP:**
```bash
GET /api/v1/notification-settings/admin/notification-settings
Authorization: Bearer <admin-token>
```

**Обновить настройки SMTP:**
```bash
PUT /api/v1/notification-settings/admin/notification-settings
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_user": "parussmikle@gmail.com",
  "smtp_password": "app-password",
  "smtp_from_email": "parussmikle@gmail.com",
  "smtp_from_name": "Seat Reservation",
  "smtp_use_tls": true,
  "email_notifications_enabled": true
}
```

**Тестирование SMTP:**
```bash
POST /api/v1/notification-settings/admin/notification-settings/test
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "test_email": "parussmikle@gmail.com"
}
```

---

## 5. Типы уведомлений

| Тип | Триггер | Email | ЛК |
|-----|---------|-------|----|
| `booking_cancelled` | Отмена бронирования | ✅ | ✅ |
| `workspace_disabled` | Отключение места | ✅ | ✅ |
| `room_disabled` | Отключение помещения | ✅ | ✅ |
| `booking_reminder` | Напоминание (18:00) | ✅ | ✅ |

---

## 6. Форматы данных

### 6.1. JSON для ЛК

```json
{
  "type": "booking_cancelled",
  "title": "Бронирование отменено!",
  "icon": "❌",
  "greeting": "Здравствуйте, Администратор!",
  "message": "Ваше бронирование было отменено.",
  "items": [
    {"icon": "🪑", "label": "Место", "value": "Рабочее место 2_8"},
    {"icon": "🏢", "label": "Помещение", "value": "Академика Ландау д.49"},
    {"icon": "📅", "label": "Дата", "value": "2026-04-02"},
    {"icon": "⚠️", "label": "Причина", "value": "Ручная отмена"}
  ],
  "footer": "Если у вас возникли вопросы..."
}
```

### 6.2. HTML для Email

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    .header { background-color: #f44336; }
    .info-box { border-left: 4px solid #f44336; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>❌ Бронирование отменено!</h1>
    </div>
    <div class="info-box">
      <div>🪑 Место: Рабочее место 2_8</div>
      <div>🏢 Помещение: Академика Ландау д.49</div>
    </div>
  </div>
</body>
</html>
```

---

## 7. Frontend компоненты

### 7.1. NotificationSettings.vue

**Путь:**
```
src/components/profile/NotificationSettings.vue
```

**Функционал:**
- Загрузка настроек при монтировании
- Автоматическое сохранение при переключении
- Toast уведомления об успехе/ошибке
- Обработка ошибок загрузки

### 7.2. Stores

**notificationSettings.js:**
```javascript
const settingsStore = useNotificationSettingsStore()

// Методы
await settingsStore.fetchMySettings()
await settingsStore.updateMySettings({ email_enabled, site_enabled })
```

### 7.3. Services

**notificationSettings.js:**
```javascript
const notificationSettingsAPI = {
  async getMySettings(),
  async updateMySettings(data),
  async getNotificationSettings(),
  async updateNotificationSettings(data),
  async testNotificationSettings(testEmail)
}
```

---

## 8. Backend сервисы

### 8.1. notification_service.py

**Методы:**
```python
def send_booking_cancelled_notification(booking_id, reason)
def send_workspace_disabled_notification(workspace_id)
def send_room_disabled_notification(room_id)
def send_booking_reminder_notification(booking_id)
```

**Логика проверки настроек:**
```python
# Проверяем настройки пользователя
user_settings = user.notification_settings

# Если оба отключены — игнорируем
if not user_settings.email_enabled and not user_settings.site_enabled:
    return {"success": True, "message": "Уведомления отключены"}

# Создаём в БД только если site_enabled
if user_settings.site_enabled:
    notification = Notification(...)

# Отправляем email только если email_enabled
if user_settings.email_enabled:
    email_service.send_email(...)
```

### 8.2. notification_templates.py

**Функции:**
```python
def get_base_booking_data(workspace_name, room_address, booking_date)
def get_booking_cancelled_data(user_name, workspace_name, room_address, booking_date, reason)
def get_workspace_disabled_data(user_name, workspace_name, room_address, booking_date)
def get_room_disabled_data(user_name, room_name, room_address, affected_bookings)
def get_booking_reminder_data(user_name, workspace_name, room_address, booking_date)
```

**HTML генераторы:**
```python
def create_booking_cancelled_html(...)
def create_workspace_disabled_html(...)
def create_room_disabled_html(...)
def create_booking_reminder_html(...)
```

---

## 9. SMTP настройка

### 9.1. Resend (рекомендуется для разработки)

**.env:**
```env
SMTP_HOST=smtp.resend.com
SMTP_PORT=465
SMTP_USER=resend
SMTP_PASSWORD=re_6mBXRPmz_4BsoQoXXSnupL8ysdpm69GyK
SMTP_FROM_EMAIL=onboarding@resend.dev
SMTP_FROM_NAME=Seat Reservation System
SMTP_USE_TLS=True
```

**Ограничения Free плана:**
- 100 писем/день, 3000/мес
- Только на ваш email (parussmikle@gmail.com)
- Для других email нужен подтверждённый домен

### 9.2. Gmail (альтернатива)

**.env:**
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=parussmikle@gmail.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx  # App Password
SMTP_FROM_EMAIL=parussmikle@gmail.com
SMTP_FROM_NAME=Seat Reservation System
SMTP_USE_TLS=True
```

**Получение App Password:**
1. https://myaccount.google.com/security
2. Включите 2-Step Verification
3. App passwords → Создать
4. Скопируйте пароль (16 символов)

---

## 10. Тестирование

### 10.1. Проверка переключателей

**Тест 1: Email отключен**
```bash
# 1. Откройте http://localhost:5173/profile
# 2. Отключите "Email уведомления"
# 3. Отмените бронирование
# 4. Проверьте логи — нет попытки отправки email ✅
```

**Тест 2: ЛК отключен**
```bash
# 1. Откройте http://localhost:5173/profile
# 2. Отключите "Уведомления в ЛК"
# 3. Отмените бронирование
# 4. Проверьте ЛК — уведомления нет ✅
```

**Тест 3: Оба отключены**
```bash
# 1. Отключите оба переключателя
# 2. Отмените бронирование
# 3. Проверьте логи — "Уведомления отключены пользователем" ✅
```

### 10.2. Тестовые скрипты

```bash
cd SeatReservetion_back

# Тест email
python test_email.py parussmikle@gmail.com

# Тест отмены бронирования
python test_booking_cancel_notification.py

# Тест напоминаний
python test_booking_reminder.py

# Тест отключения помещения
python test_room_notification.py
```

---

## 11. Логи

### 11.1. Успешная отправка

```
INFO: notification_service: Уведомление об отмене бронирования 123 
      отправлено пользователю 3
INFO: email_service: Письмо отправлено на parussmikle@gmail.com 
      с темой 'Бронирование отменено: Рабочее место 2_8'
```

### 11.2. Уведомления отключены

```
INFO: notification_service: Пользователь 3 отключил все уведомления. 
      Уведомление не создано.
```

### 11.3. Email отключен

```
(нет логов об отправке email)
```

### 11.4. Ошибка SMTP

```
ERROR: email_service: SMTP ошибка при отправке: (550, b'You can only 
        send testing emails to your own email address...')
```

---

## 12. Файлы проекта

| Файл | Назначение |
|------|------------|
| `app/models/user_notification_settings.py` | Модель настроек пользователя |
| `app/models/notification_settings.py` | Модель глобальных настроек |
| `app/services/notification_service.py` | Логика отправки уведомлений |
| `app/services/notification_templates.py` | Шаблоны уведомлений |
| `app/services/email_service.py` | Отправка email |
| `app/api/v1/routes/notification_settings.py` | API endpoints |
| `src/components/profile/NotificationSettings.vue` | UI настроек |
| `src/stores/notificationSettings.js` | Pinia store |
| `src/services/notificationSettings.js` | API сервис |

---

## 13. Swagger UI

**Проверка endpoints:**
```
http://localhost:8000/docs
```

**Секция:** `notification-settings`

**Доступные endpoints:**
- `GET /api/v1/notification-settings/my/settings`
- `PUT /api/v1/notification-settings/my/settings`
- `GET /api/v1/notification-settings/admin/notification-settings`
- `PUT /api/v1/notification-settings/admin/notification-settings`
- `POST /api/v1/notification-settings/admin/notification-settings/test`

---

## 14. Решение проблем

### 14.1. 404 ошибка API

**Проблема:**
```
GET /notification-settings/my/settings 404 (Not Found)
```

**Решение:**
- Проверьте префикс `/api/v1/` в frontend
- Правильный путь: `/api/v1/notification-settings/my/settings`

### 14.2. Уведомления не приходят

**Проверьте:**
1. Настройки пользователя в профиле
2. Наличие email у пользователя
3. Логи сервера на ошибки SMTP
4. Настройки SMTP в `.env`

### 14.3. Ошибка SQLAlchemy

**Проблема:**
```
Could not determine join condition...
```

**Решение:**
- Проверьте отношения в моделях
- Убедитесь, что ForeignKey указаны правильно

---

## 15. Ссылки

**Репозиторий:**
```
https://github.com/GarussMisha/SeatReservation.git
```

**Документация:**
- [NOTIFICATION_SETTINGS_FINAL.md](qwen/work/NOTIFICATION_SETTINGS_FINAL.md)
- [NOTIFICATION_CODE_REVIEW_2026.md](qwen/work/NOTIFICATION_CODE_REVIEW_2026.md)

**Resend:**
- [Dashboard](https://app.resend.com)
- [Documentation](https://resend.com/docs)

---

**Документация актуальна на:** 1 апреля 2026  
**Статус:** ✅ Полностью реализовано и протестировано
