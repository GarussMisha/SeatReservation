# 📬 Настройка Email уведомлений (Resend)

## ✅ Что сделано

Интегрирован **Resend SMTP** для отправки email-уведомлений пользователям.

---

## 🚀 Быстрый старт

### 1. Настройки уже конфигурации

Файл `.env` уже обновлён:

```env
SMTP_HOST=smtp.resend.com
SMTP_PORT=465
SMTP_USER=resend
SMTP_PASSWORD=re_6mBXRPmz_4BsoQoXXSnupL8ysdpm69GyK
SMTP_FROM_EMAIL=onboarding@resend.dev
SMTP_FROM_NAME=Seat Reservation System
SMTP_USE_TLS=True
```

### 2. Тестирование

```bash
cd SeatReservetion_back
venv\Scripts\activate
python test_email.py
```

Введите email для проверки (по умолчанию `parussmikle@gmail.com`).

---

## 📧 Типы уведомлений

Система автоматически отправляет уведомления при:

| Событие | Тип | Получатель |
|---------|-----|------------|
| Отмена бронирования | `booking_cancelled` | Пользователь |
| Отключение рабочего места | `workspace_disabled` | Все с бронированиями |
| Отключение помещения | `room_disabled` | Все с бронированиями |
| Рассылка от админа | `custom` | Выбранные пользователи |

---

## 🔧 Планировщик

**APScheduler** проверяет и отправляет отложенные уведомления каждые **5 минут**.

Автоматически запускается при старте сервера:
```python
# app/main.py
start_notification_scheduler(check_interval_minutes=5)
```

---

## 📊 API для работы с уведомлениями

### Получить мои уведомления (User)
```bash
GET /api/v1/notifications/my?limit=50&skip=0
Authorization: Bearer <token>
```

### Получить все уведомления (Admin)
```bash
GET /api/v1/notifications/?limit=100&skip=0
Authorization: Bearer <admin-token>
```

### Запланировать рассылку (Admin)
```bash
POST /api/v1/notifications/schedule
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "user_ids": [1, 2, 3],
  "subject": "Важное сообщение",
  "message": "Текст сообщения",
  "scheduled_at": "2026-04-02T10:00:00"
}
```

### Статистика (Admin)
```bash
GET /api/v1/notifications/stats/overview
```

---

## 📝 Документы

- [RESEND_EMAIL_SETUP.md](RESEND_EMAIL_SETUP.md) — подробная документация
- [test_email.py](test_email.py) — тестовый скрипт

---

## ⚠️ Важно

- **Free план Resend**: 100 писем/день, 3000/мес
- Для продакшена добавьте свой домен в Resend Dashboard
- Не коммитьте `.env` с API ключом в Git!

---

**Дата обновления:** Апрель 2026  
**Статус:** ✅ Готово к использованию
