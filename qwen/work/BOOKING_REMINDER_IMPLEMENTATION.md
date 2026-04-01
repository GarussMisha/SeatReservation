# ✅ Реализация напоминаний о бронировании за 6 часов

## 📅 Дата: 1 апреля 2026

## 📊 Статус: ✅ РЕАЛИЗОВАНО

---

## 1. Что было добавлено

### 1.1. Новый тип уведомления

**`booking_reminder`** — напоминание о предстоящем бронировании

**Когда отправляется:**
- За 6 часов до начала бронирования (в 18:00 за 00:00 следующего дня)
- Только для подтверждённых бронирований (`status_id = 13 confirmed`)
- Только если у пользователя есть email

---

## 2. Реализованные компоненты

### 2.1. Email шаблон

**Файл:** `app/services/email_service.py`

```python
@staticmethod
def create_booking_reminder_html(
    user_name: str,
    workspace_name: str,
    room_name: str,
    room_address: str,
    booking_date: str
) -> str:
    """Создание HTML шаблона для напоминания о бронировании"""
```

**Пример письма:**
```
📅 Напоминание о бронировании

Здравствуйте, Администратор Системы!

⏰ Не забудьте посетить офис завтра!

Напоминаем вам о предстоящем бронировании рабочего места.

Детали бронирования:
🪑 Рабочее место: Рабочее место 1
🏢 Помещение: Дом 2
📍 Адрес: Тестовый адрес
📅 Дата: 2026-04-02

Желаем продуктивного дня!

С уважением,
Команда Seat Reservation System
```

---

### 2.2. Метод отправки

**Файл:** `app/services/notification_service.py`

```python
def send_booking_reminder_notification(self, booking_id: int) -> Dict[str, Any]:
    """Отправка напоминания о предстоящем бронировании"""
```

**Логика:**
1. Получает бронирование по ID
2. Проверяет наличие пользователя, рабочего места, помещения
3. Проверяет наличие email у пользователя
4. Создаёт HTML-письмо
5. Создаёт уведомление в БД (статус `pending`)
6. Отправляет email через SMTP
7. Обновляет статус на `sent` или `failed`

---

### 2.3. Задача планировщика

**Файл:** `app/services/scheduler_service.py`

```python
def _send_booking_reminders_task(self):
    """
    Проверка бронирований и отправка напоминаний за 6 часов до начала
    Вызывается планировщиком каждый час
    """
```

**Логика:**
1. Проверяет текущее время (работает только с 17:00 до 23:00)
2. Находит все подтверждённые бронирования на завтра
3. Для каждого бронирования проверяет, не отправлялось ли напоминание за последние 24 часа
4. Отправляет напоминание через `send_booking_reminder_notification()`
5. Логирует результат

**Время работы:**
- Проверяется каждый час
- Активно с 17:00 до 23:00 (чтобы отправить напоминание в 18:00)
- Для бронирований на следующий день

---

### 2.4. Регистрация в планировщике

**Файл:** `app/services/scheduler_service.py`

```python
def start(self, check_interval_minutes: int = 5):
    # Задача 1: Проверка pending уведомлений (каждые 5 минут)
    self.scheduler.add_job(
        func=self._send_pending_notifications_task,
        trigger=IntervalTrigger(minutes=check_interval_minutes),
        ...
    )
    
    # Задача 2: Напоминания о бронированиях (каждый час)
    self.scheduler.add_job(
        func=self._send_booking_reminders_task,
        trigger=IntervalTrigger(hours=1),
        id='send_booking_reminders',
        ...
    )
```

---

## 3. Вспомогательные методы

### 3.1. Устранение дублирования кода

**Файл:** `app/services/notification_service.py`

```python
def _get_or_create_pending_status(self) -> Status:
    """Получить или создать статус 'pending'"""
    pending_status = self._get_status_by_name("pending")
    if not pending_status:
        pending_status = Status(name="pending", description="Ожидает отправки")
        self.db.add(pending_status)
        self.db.commit()
        self.db.refresh(pending_status)
    return pending_status
```

**Используется в:**
- `send_booking_cancelled_notification()`
- `send_booking_reminder_notification()`
- `send_workspace_disabled_notification()`
- `send_room_disabled_notification()`
- `send_pending_notifications()`

---

## 4. Тестирование

### 4.1. Тестовый скрипт

**Файл:** `test_booking_reminder.py`

**Проверяет:**
1. Создание бронирования на завтра
2. Отправку напоминания
3. Проверку создания уведомления в БД
4. Проверку отправки email

**Запуск:**
```bash
cd SeatReservetion_back
venv\Scripts\activate
python test_booking_reminder.py
```

**Результат:**
```
============================================================
 ИТОГИ ТЕСТА
============================================================
 ТЕСТ ПРОЙДЕН!

 Напоминание было создано и отправлено.
 Проверьте email ящик пользователя.
============================================================
```

---

## 5. Проверка работы

### Сценарий 1: Бронирование на завтра

**Дано:**
- Пользователь: `admin` (email: `parussmikle@gmail.com`)
- Бронирование: завтра (2026-04-02) с 00:00 до 23:59
- Статус: `confirmed`

**Когда:**
- Сегодня 18:00 (2026-04-01 18:00)

**Что происходит:**
1. Планировщик проверяет бронирования каждый час
2. В 18:00 находит бронирование на завтра
3. Проверяет, что напоминание ещё не отправлялось
4. Создаёт уведомление в БД
5. Отправляет email через Resend/Gmail
6. Обновляет статус на `sent`

**Результат:**
```
✅ Напоминание отправлено успешно!
- Тип: booking_reminder
- Тема: Напоминание: бронирование на 2026-04-02
- Статус: sent
- Email: parussmikle@gmail.com
```

---

### Сценарий 2: Отключение места/помещения

**Дано:**
- У пользователя есть активное бронирование
- Админ отключает рабочее место (`is_active = false`)
- ИЛИ админ отключает помещение (`status: active → inactive`)

**Когда:**
- Сразу при изменении статуса

**Что происходит:**
1. API обнаруживает изменение статуса
2. Вызывает `send_workspace_disabled_notification()` или `send_room_disabled_notification()`
3. Находит все активные бронирования на этом месте/в помещении
4. Отправляет уведомления всем пользователям

**Результат:**
```
✅ Уведомление отправлено
- Тип: workspace_disabled или room_disabled
- Статус: sent
```

---

## 6. Логирование

### 6.1. Успешная отправка

```
INFO:app.services.notification_service:Напоминание о бронировании 123 отправлено пользователю 456
INFO:app.services.scheduler_service:Напоминания о бронированиях: всего=5, отправлено=5, ошибок=0
```

### 6.2. Ошибка отправки

```
WARNING:app.services.notification_service:У пользователя 456 нет email для напоминания
ERROR:app.services.scheduler_service:Ошибка в задаче напоминаний: SMTP ошибка при отправке
```

---

## 7. Изменённые файлы

| Файл | Изменения |
|------|-----------|
| `app/services/email_service.py` | Добавлен `create_booking_reminder_html()` |
| `app/services/notification_service.py` | Добавлен `send_booking_reminder_notification()`, `_get_or_create_pending_status()` |
| `app/services/scheduler_service.py` | Добавлена задача `_send_booking_reminders_task()`, регистрация в `start()` |
| `test_booking_reminder.py` | Новый тестовый скрипт |

---

## 8. Чек-лист реализации

- [x] HTML-шаблон для напоминания
- [x] Метод отправки `send_booking_reminder_notification()`
- [x] Вспомогательный метод `_get_or_create_pending_status()`
- [x] Задача планировщика `_send_booking_reminders_task()`
- [x] Регистрация задачи в планировщике
- [x] Тестовый скрипт
- [x] Логирование
- [x] Документация

---

## 9. Проверка перед продакшеном

### 9.1. Настройка SMTP

```env
# Для Resend
SMTP_HOST=smtp.resend.com
SMTP_PORT=465
SMTP_USER=resend
SMTP_PASSWORD=re_6mBXRPmz_4BsoQoXXSnupL8ysdpm69GyK
SMTP_FROM_EMAIL=onboarding@resend.dev
SMTP_FROM_NAME=Seat Reservation System

# ИЛИ для Gmail
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=parussmikle@gmail.com
SMTP_PASSWORD=app-password-из-google
SMTP_FROM_EMAIL=parussmikle@gmail.com
SMTP_FROM_NAME=Seat Reservation System
```

### 9.2. Проверка работы планировщика

```bash
# Запуск сервера
python run_server.py

# В логах должно быть:
✅ Планировщик уведомлений запущен (проверка каждые 5 мин)
Напоминания о бронированиях проверяются каждый час (17:00-23:00)
```

### 9.3. Тестирование

```bash
# Тест напоминаний
python test_booking_reminder.py

# Тест отмены бронирования
python test_booking_cancel_notification.py

# Тест отключения помещения
python test_room_notification.py
```

---

## 10. Итоговая архитектура

```
┌─────────────────────────────────────────────────────────┐
│                  Scheduler Service                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Задача 1: pending уведомления (каждые 5 мин)     │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Задача 2: напоминания (каждый час, 17:00-23:00) │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Notification Service                        │
│  - send_booking_cancelled_notification()                │
│  - send_booking_reminder_notification() ← НОВОЕ         │
│  - send_workspace_disabled_notification()               │
│  - send_room_disabled_notification()                    │
│  - _get_or_create_pending_status() ← НОВОЕ             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Email Service                           │
│  - create_booking_cancelled_html()                      │
│  - create_booking_reminder_html() ← НОВОЕ              │
│  - create_workspace_disabled_html()                     │
│  - create_room_disabled_html()                          │
│  - send_email() (SMTP Resend/Gmail)                     │
└─────────────────────────────────────────────────────────┘
```

---

**Реализовано:** 1 апреля 2026  
**Статус:** ✅ Готово к использованию  
**Следующий шаг:** Протестировать на реальном сервере
