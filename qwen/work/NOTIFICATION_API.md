# 📬 Система уведомлений — Полная документация

## 📅 Дата обновления: 1 апреля 2026

## 📊 Статус: ✅ РЕАЛИЗОВАНО

---

## 1. Архитектура системы

```
┌─────────────────────────────────────────────────────────┐
│  Backend (notification_service.py)                      │
│                                                          │
│  notification_data = get_booking_cancelled_data(...)   │  ← Данные (JSON)
│  html_content = create_booking_cancelled_html(...)     │  ← HTML для Email
│                                                          │
│  # Сохраняем JSON в БД                                  │
│  notification.message = json.dumps(notification_data)  │
│                                                          │
│  # Отправляем HTML по почте                             │
│  email_service.send_email(html_content=html_content)   │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ JSON строка в БД
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  Backend (notification.py - API)                        │
│                                                          │
│  # Парсим JSON перед отправкой                          │
│  message_data = json.loads(notification.message)       │
│                                                          │
│  return {"message": message_data, ...}  ← JSON объект  │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ JSON объект
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  Frontend (Notifications.vue)                           │
│                                                          │
│  # message уже объект (распарсен на backend)            │
│  const data = notification.message  ← JSON объект      │
│                                                          │
│  # Отображаем структурированно                          │
│  <div>{{ data.greeting }}</div>                        │
│  <div v-for="item in data.items">...</div>             │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Типы уведомлений

| Тип | Событие | Получатель | Триггер |
|-----|---------|------------|---------|
| `booking_cancelled` | Отмена бронирования | Пользователь | Админ отменяет бронь |
| `workspace_disabled` | Отключение рабочего места | Пользователь с бронью | `is_active = false` |
| `room_disabled` | Отключение помещения | Пользователи с бронями | `status: active → inactive` |
| `booking_reminder` | Напоминание о бронировании | Пользователь | За 6 часов до начала (18:00) |
| `custom` | Произвольная рассылка | Выбранные пользователи | Админ создаёт рассылку |

---

## 3. Шаблоны уведомлений

### 3.1. Данные для Frontend (JSON)

**Файл:** `app/services/notification_templates.py`

#### Отмена бронирования
```python
{
    "type": "booking_cancelled",
    "title": "Бронирование отменено!",
    "icon": "❌",
    "greeting": "Здравствуйте, {user_name}!",
    "message": "Ваше бронирование было отменено.",
    "items": [
        {"icon": "🪑", "label": "Место", "value": "{workspace_name}"},
        {"icon": "🏢", "label": "Помещение", "value": "{room_address}"},
        {"icon": "📅", "label": "Дата", "value": "{booking_date}"},
        {"icon": "⚠️", "label": "Причина", "value": "{reason}"}
    ],
    "footer": "Если у вас возникли вопросы..."
}
```

#### Напоминание о бронировании
```python
{
    "type": "booking_reminder",
    "title": "Напоминание о бронировании!",
    "icon": "📅",
    "greeting": "Здравствуйте, {user_name}!",
    "message": "Напоминаем вам о предстоящем бронировании.",
    "items": [
        {"icon": "🪑", "label": "Место", "value": "{workspace_name}"},
        {"icon": "🏢", "label": "Помещение", "value": "{room_address}"},
        {"icon": "📅", "label": "Дата", "value": "{booking_date}"}
    ],
    "footer": "Желаем продуктивного дня!"
}
```

---

### 3.2. HTML для Email

**Файл:** `app/services/notification_templates.py`

Генерируется отдельно для каждого типа уведомления и отправляется только по email.

**Пример:**
```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .header { background-color: #f44336; color: white; }
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
            <div>🏢 Помещение: Академика Лаврентьева, 10</div>
        </div>
    </div>
</body>
</html>
```

---

## 4. Настройка SMTP

### 4.1. Resend (рекомендуется для разработки)

**Файл:** `.env`

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
- Для отправки на другие email нужен подтверждённый домен

### 4.2. Gmail (альтернатива)

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

## 5. Планировщик задач

### 5.1. Запуск

**Файл:** `app/main.py`

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запуск при старте
    start_notification_scheduler(check_interval_minutes=5)
    yield
    # Остановка при завершении
    stop_notification_scheduler()
```

### 5.2. Задачи

| Задача | Интервал | Описание |
|--------|----------|----------|
| `send_pending_notifications` | каждые 5 мин | Отправка отложенных уведомлений |
| `send_booking_reminders` | каждый час (17:00-23:00) | Напоминания за 6 часов до начала |

---

## 6. API Endpoints

### 6.1. Пользователь

```bash
# Получить мои уведомления
GET /api/v1/notifications/my?limit=50&skip=0
Authorization: Bearer <token>

# Ответ:
{
  "notifications": [
    {
      "id": 42,
      "notification_type": "booking_cancelled",
      "subject": "Бронирование отменено: Рабочее место 2_8",
      "message": {  # ← JSON объект (не строка!)
        "type": "booking_cancelled",
        "title": "Бронирование отменено!",
        "greeting": "Здравствуйте, Администратор!",
        "items": [...]
      },
      "created_at": "2026-04-01T19:00:00",
      "status_name": "sent"
    }
  ],
  "total": 10
}
```

### 6.2. Администратор

```bash
# Получить все уведомления
GET /api/v1/notifications/?limit=100&skip=0
Authorization: Bearer <admin-token>

# Запланировать рассылку
POST /api/v1/notifications/schedule
{
  "user_ids": [1, 2, 3],
  "subject": "Важное сообщение",
  "message": "Текст сообщения",
  "scheduled_at": "2026-04-02T10:00:00"
}

# Статистика
GET /api/v1/notifications/stats/overview

# Ответ:
{
  "total_notifications": 150,
  "pending_notifications": 5,
  "sent_notifications": 140,
  "failed_notifications": 3,
  "scheduled_notifications": 2,
  "notifications_by_type": {
    "booking_cancelled": 80,
    "booking_reminder": 40,
    "custom": 30
  }
}
```

---

## 7. Frontend

### 7.1. Отображение уведомлений

**Файл:** `src/views/Notifications.vue`

**Структурированное отображение:**
```vue
<div v-if="isJsonNotification(notification.message)" class="notification-structured">
  <div class="notification-greeting">{{ getNotificationGreeting(message) }}</div>
  <div class="notification-main-text">{{ getNotificationMessage(message) }}</div>
  
  <div class="notification-items">
    <div v-for="item in getNotificationItems(message)" :key="item.label">
      <span class="item-icon">{{ item.icon }}</span>
      <span class="item-label">{{ item.label }}:</span>
      <span class="item-value">{{ item.value }}</span>
    </div>
  </div>
  
  <div class="notification-footer-text">{{ getNotificationFooter(message) }}</div>
</div>
```

**CSS стили:**
```css
.notification-items {
  background-color: #f9fafb;
  border-left: 3px solid #667eea;
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 4px;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.item-icon {
  font-size: 1.1rem;
  min-width: 1.5rem;
}

.item-label {
  font-weight: 600;
  color: #555;
  min-width: 120px;
}
```

---

## 8. Тестирование

### 8.1. Тест email

```bash
cd SeatReservetion_back
python test_email.py parussmikle@gmail.com
```

### 8.2. Тест напоминаний

```bash
python test_booking_reminder.py
```

### 8.3. Тест отмены бронирования

```bash
python test_booking_cancel_notification.py
```

### 8.4. Тест отключения помещения

```bash
python test_room_notification.py
```

---

## 9. Файлы проекта

| Файл | Назначение |
|------|------------|
| `app/services/notification_templates.py` | Шаблоны уведомлений (JSON + HTML) |
| `app/services/notification_service.py` | Логика отправки уведомлений |
| `app/services/email_service.py` | Отправка email через SMTP |
| `app/services/scheduler_service.py` | Планировщик задач (APScheduler) |
| `app/api/v1/routes/notification.py` | API endpoints для уведомлений |
| `src/views/Notifications.vue` | Страница уведомлений |
| `src/stores/serverNotifications.js` | Pinia store для уведомлений |

---

## 10. Важные замечания

### 10.1. Формат хранения в БД

**Новые уведомления:** JSON строка
```json
{"type":"booking_cancelled","title":"Бронирование отменено!",...}
```

**Старые уведомления:** HTML строка
```html
<!DOCTYPE html><html><head><style>...
```

**Frontend автоматически определяет формат** и отображает:
- JSON → структурированно с иконками
- HTML → как текст (с удалением тегов)

### 10.2. Часовой пояс

Сервер сохраняет время в **локальном часовом поясе** (Екатеринбург, UTC+5).

Frontend отображает время сервера "как есть" без конвертации.

### 10.3. Лимиты Resend

| План | Лимит | Цена |
|------|-------|------|
| Free | 100/день, 3000/мес | Бесплатно |
| Pro | 50,000/мес | $20/мес |
| Business | 100,000+/мес | от $100/мес |

---

## 11. Решение проблем

### 11.1. Уведомления не отправляются

**Проверьте:**
1. Настроен ли SMTP в `.env`
2. Есть ли у пользователя email
3. Логи сервера на наличие ошибок

### 11.2. Уведомления отображаются как HTML

**Причина:** Это старые уведомления (до рефакторинга).

**Решение:** Создайте новое уведомление (отмените бронирование) — оно отобразится структурированно.

### 11.3. Напоминания не приходят

**Проверьте:**
1. Запущен ли планировщик (логи при старте сервера)
2. Есть ли бронирования на завтра
3. Текущее время (17:00-23:00 для напоминаний)

---

## 12. Ссылки

- [Resend Dashboard](https://app.resend.com)
- [Resend Documentation](https://resend.com/docs)
- [Resend SMTP Guide](https://resend.com/docs/send-with-smtp)

---

**Документация актуальна на:** 1 апреля 2026  
**Статус:** ✅ Полностью реализовано и протестировано
