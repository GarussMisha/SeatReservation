# 🔍 Code Review: Система уведомлений и нотификаций

## 📅 Дата: 1 апреля 2026

## 📊 Статус: ✅ ТРЕБУЕТСЯ ДОРАБОТКА

---

## 1. Архитектура системы

### 1.1. Компоненты

```
┌─────────────────────────────────────────────────────────┐
│                  Notification Service                    │
│  - send_booking_cancelled_notification()                │
│  - send_workspace_disabled_notification()               │
│  - send_room_disabled_notification()                    │
│  - send_pending_notifications()                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Scheduler Service                       │
│  - Проверка каждые 5 минут                               │
│  - Отправка pending уведомлений                         │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Анализ текущего функционала

### ✅ Реализовано

| Уведомление | Триггер | Статус |
|-------------|---------|--------|
| Отмена бронирования | Админ отменяет бронь | ✅ Работает |
| Отключение рабочего места | `is_active = false` | ✅ Работает |
| Отключение помещения | `status: active → inactive` | ✅ Работает |
| Рассылка от админа | Через API | ✅ Работает |

### ❌ НЕ реализовано

| Уведомление | Ожидалось | Статус |
|-------------|-----------|--------|
| **Напоминание за 6 часов** | За 6 часов до начала бронирования | ❌ **ОТСУТСТВУЕТ** |

---

## 3. Найденные проблемы

### 3.1. Критичные

#### ❌ Проблема 1: Отсутствует напоминание за 6 часов

**Описание:**
- Пользователь забронировал место на завтра (с 00:00 до 23:59)
- В 18:00 сегодня должно прийти напоминание на email
- **Код напоминания ОТСУТСТВУЕТ**

**Где должно быть:**
```python
# app/services/notification_service.py
# НЕТ метода send_booking_reminder_notification()

# app/services/scheduler_service.py
# НЕТ задачи для проверки предстоящих бронирований
```

**Решение:**
Создать новый метод и задачу планировщика (см. раздел 5)

---

#### ❌ Проблема 2: Планировщик отправляет только pending уведомления

**Файл:** `app/services/scheduler_service.py`

```python
def _send_pending_notifications_task(self):
    """Задача для отправки отложенных уведомлений"""
    db = SessionLocal()
    notification_service = NotificationService(db)
    result = notification_service.send_pending_notifications()  # ← Только pending
```

**Проблема:**
- Планировщик проверяет ТОЛЬКО уведомления со статусом `pending`
- Для напоминаний за 6 часов нужна ОТДЕЛЬНАЯ задача
- Нет логики проверки предстоящих бронирований

**Решение:**
Добавить новую задачу `_send_booking_reminders_task()` (см. раздел 5)

---

### 3.2. Избыточность кода

#### ⚠️ Дублирование проверки статусов

**Файл:** `app/services/notification_service.py`

В каждом методе повторяется код получения статуса "pending":

```python
# send_booking_cancelled_notification (строка 81)
pending_status = self._get_status_by_name("pending")
if not pending_status:
    pending_status = Status(name="pending", description="Ожидает отправки")
    self.db.add(pending_status)
    self.db.commit()
    self.db.refresh(pending_status)

# send_workspace_disabled_notification (строка ~233)
# send_room_disabled_notification (строка ~391)
# send_pending_notifications (строка ~571)
```

**Решение:**
Создать вспомогательный метод:
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

---

#### ⚠️ Одинаковая логика отправки email

**Файл:** `app/services/notification_service.py`

В каждом методе повторяется:
```python
# Создаем HTML письмо
html_content = self.email_service.create_XXX_html(...)

# Создаем запись уведомления
notification = Notification(
    notification_type=...,
    subject=...,
    message=html_content,
    scheduled_at=None,
    status_id=pending_status.id,
    user_id=user.id,
    created_by_id=None
)

self.db.add(notification)
self.db.commit()

# Отправляем email
email_result = self.email_service.send_email(...)
```

**Решение:**
Создать базовый метод `_create_and_send_notification()`:
```python
def _create_and_send_notification(
    self,
    user: Account,
    notification_type: str,
    subject: str,
    html_content: str
) -> Dict[str, Any]:
    """Создать уведомление и отправить email"""
    pending_status = self._get_or_create_pending_status()
    
    notification = Notification(
        notification_type=notification_type,
        subject=subject,
        message=html_content,
        scheduled_at=None,
        status_id=pending_status.id,
        user_id=user.id,
        created_by_id=None
    )
    
    self.db.add(notification)
    self.db.commit()
    self.db.refresh(notification)
    
    email_result = self.email_service.send_email(
        to_email=user.email,
        subject=subject,
        html_content=html_content
    )
    
    # Обновляем статус
    if email_result["success"]:
        sent_status = self._get_status_by_name("sent")
        if sent_status:
            notification.status_id = sent_status.id
            notification.sent_at = datetime.now(timezone.utc)
            self.db.commit()
    
    return {
        "success": True,
        "notification_id": notification.id,
        "email_sent": email_result["success"]
    }
```

---

### 3.3. Логические ошибки

#### ⚠️ Проблема 3: Уведомление при отмене бронирования отправляется СЛИШКОМ ПОЗДНО

**Файл:** `app/api/v1/routes/booking.py` (строка 685)

```python
# Изменяем статус бронирования на "отменено"
booking.status_id = cancelled_status.id
db.commit()

# Отправляем уведомление пользователю
notification_service.send_booking_cancelled_notification(booking_id=booking.id)
```

**Проблема:**
- Уведомление отправляется ПОСЛЕ изменения статуса на `cancelled`
- Если email не отправится, пользователь не узнает об отмене
- Нет проверки, что у пользователя есть email

**Решение:**
Проверять email ДО изменения статуса:
```python
# Проверяем email пользователя
user = db.query(Account).filter(Account.id == booking.account_id).first()
if not user or not user.email:
    logger.warning(f"У пользователя {user.id} нет email для уведомления")
    # Но продолжаем отмену - это не критично

# Изменяем статус
booking.status_id = cancelled_status.id
db.commit()

# Отправляем уведомление
notification_service.send_booking_cancelled_notification(booking_id=booking.id)
```

---

#### ⚠️ Проблема 4: Нет проверки на активные бронирования при отключении места

**Файл:** `app/api/v1/routes/workspace.py` (строка 267-279)

```python
# Проверяем, меняется ли is_active с True на False
send_notification = False
if 'is_active' in update_data:
    if workspace.is_active == True and update_data['is_active'] == False:
        send_notification = True

# ...

if send_notification:
    notification_service.send_workspace_disabled_notification(...)
```

**Проблема:**
- Уведомление отправляется ВСЕГДА при отключении места
- НЕ проверяется, есть ли активные бронирования на этом месте
- Может отправляться "пустое" уведомление (нет затронутых пользователей)

**Решение:**
Проверять наличие активных бронирований ПЕРЕД отправкой:
```python
if send_notification:
    # Проверяем наличие активных бронирований
    from app.models.booking import Booking
    from app.models.status import BookingStatuses
    
    active_bookings = db.query(Booking).filter(
        Booking.workspace_id == workspace.id,
        Booking.status_id.in_([BookingStatuses.PENDING, BookingStatuses.CONFIRMED])
    ).all()
    
    if active_bookings:  # Отправляем только если есть активные брони
        notification_service.send_workspace_disabled_notification(...)
    else:
        logger.info(f"Нет активных бронирований на workspace {workspace.id}")
```

---

## 4. Проверка работы при подключенном SMTP

### 4.1. Сценарий 1: Помещение/место стало inactive

**Когда сработает:**
```python
# app/api/v1/routes/room.py (строка 268-281)
if old_status_id == active_status_id and new_status_id == inactive_status_id:
    send_notification = True

if send_notification:
    notification_service.send_room_disabled_notification(room_id=room.id)
```

**Результат:**
- ✅ Уведомление создаётся в БД
- ✅ Email отправляется через Resend/Gmail SMTP
- ✅ Статус меняется на `sent` или `failed`

**Проверка:**
```bash
python test_room_notification.py
```

---

### 4.2. Сценарий 2: Напоминание за 6 часов

**Когда должно сработать:**
- Бронирование на завтра (2026-04-02)
- Сегодня 18:00 (2026-04-01 18:00)
- **ДО бронирования осталось 6 часов**

**Результат:**
- ❌ **НЕ РАБОТАЕТ** - код отсутствует

**Что нужно добавить:**
```python
# app/services/notification_service.py
def send_booking_reminder_notification(self, booking_id: int) -> Dict[str, Any]:
    """Отправка напоминания о предстоящем бронировании"""
    # ... (см. раздел 5.1)

# app/services/scheduler_service.py
def _send_booking_reminders_task(self):
    """Проверка бронирований за 6 часов до начала"""
    # ... (см. раздел 5.2)
```

---

## 5. Необходимые доработки

### 5.1. Напоминание за 6 часов (Backend)

**Файл:** `app/services/notification_service.py`

Добавить новый метод после `send_booking_cancelled_notification`:

```python
def send_booking_reminder_notification(self, booking_id: int) -> Dict[str, Any]:
    """
    Отправка напоминания о предстоящем бронировании
    
    Args:
        booking_id: ID бронирования
    
    Returns:
        Результат отправки
    """
    result = {
        "success": False,
        "message": "",
        "notification_id": None,
        "email_sent": False
    }
    
    try:
        # Получаем бронирование
        booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            result["message"] = f"Бронирование {booking_id} не найдено"
            return result
        
        # Получаем связанные данные
        user = self.db.query(Account).filter(Account.id == booking.account_id).first()
        workspace = self.db.query(Workspace).filter(Workspace.id == booking.workspace_id).first()
        room = self.db.query(Room).filter(Room.id == workspace.room_id).first() if workspace else None
        
        if not user or not workspace or not room:
            result["message"] = "Недостаточно данных для отправки уведомления"
            return result
        
        if not user.email:
            result["message"] = "У пользователя нет email"
            logger.warning(f"У пользователя {user.id} нет email для напоминания")
            return result
        
        # Получаем статус "pending"
        pending_status = self._get_or_create_pending_status()
        
        # Создаем HTML письмо
        html_content = self.email_service.create_booking_reminder_html(
            user_name=self._get_user_name(user),
            workspace_name=workspace.name,
            room_name=room.name,
            room_address=room.address or "Не указан",
            booking_date=booking.booking_date.isoformat() if booking.booking_date else "Н/Д"
        )
        
        subject = f"Напоминание: бронирование на {booking.booking_date}"
        
        # Создаем уведомление
        notification = Notification(
            notification_type="booking_reminder",
            subject=subject,
            message=html_content,
            scheduled_at=None,
            status_id=pending_status.id,
            user_id=user.id,
            created_by_id=None
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        result["notification_id"] = notification.id
        
        # Отправляем email
        email_result = self.email_service.send_email(
            to_email=user.email,
            subject=subject,
            html_content=html_content
        )
        
        if email_result["success"]:
            result["email_sent"] = True
            sent_status = self._get_status_by_name("sent")
            if sent_status:
                notification.status_id = sent_status.id
                notification.sent_at = datetime.now(timezone.utc)
                self.db.commit()
        
        result["success"] = True
        result["message"] = "Напоминание отправлено"
        logger.info(f"Напоминание о бронировании {booking_id} отправлено пользователю {user.id}")
        
    except Exception as e:
        self.db.rollback()
        result["message"] = f"Ошибка: {str(e)}"
        logger.error(f"Ошибка при отправке напоминания: {e}")
    
    return result
```

---

### 5.2. Задача планировщика для напоминаний

**Файл:** `app/services/scheduler_service.py`

Добавить новую задачу:

```python
def _send_booking_reminders_task(self):
    """
    Проверка бронирований и отправка напоминаний за 6 часов
    Вызывается планировщиком каждый час
    """
    logger.debug("Запуск задачи проверки напоминаний о бронированиях")
    
    db = SessionLocal()
    try:
        from app.models.booking import Booking
        from app.models.status import BookingStatuses
        from datetime import timedelta
        
        # Вычисляем временное окно: бронирования на завтра
        # Напоминание отправляется в 18:00 за 6 часов до начала (00:00)
        now = datetime.now(timezone.utc)
        
        # Находим все CONFIRMED бронирования на завтра
        tomorrow = (now + timedelta(days=1)).date()
        
        bookings = db.query(Booking).filter(
            Booking.booking_date == tomorrow,
            Booking.status_id == BookingStatuses.CONFIRMED
        ).all()
        
        reminders_sent = 0
        reminders_failed = 0
        
        for booking in bookings:
            # Проверяем, не отправляли ли уже напоминание сегодня
            already_reminded = db.query(Notification).filter(
                Notification.user_id == booking.account_id,
                Notification.notification_type == "booking_reminder",
                Notification.created_at >= now - timedelta(hours=24)
            ).first()
            
            if already_reminded:
                logger.debug(f"Напоминание уже отправлено для booking {booking.id}")
                continue
            
            # Отправляем напоминание
            notification_service = NotificationService(db)
            result = notification_service.send_booking_reminder_notification(
                booking_id=booking.id
            )
            
            if result["success"]:
                reminders_sent += 1
            else:
                reminders_failed += 1
        
        logger.info(
            f"Напоминания о бронированиях: "
            f"всего={len(bookings)}, отправлено={reminders_sent}, "
            f"ошибок={reminders_failed}"
        )
        
    except Exception as e:
        logger.error(f"Ошибка в задаче напоминаний: {e}")
    finally:
        db.close()
```

---

### 5.3. Регистрация задачи в планировщике

**Файл:** `app/services/scheduler_service.py`

Обновить метод `start()`:

```python
def start(self, check_interval_minutes: int = 5):
    """Запуск планировщика задач"""
    if self._is_running:
        logger.warning("Планировщик уже запущен")
        return
    
    try:
        self.scheduler = BackgroundScheduler()
        
        # Задача 1: Проверка pending уведомлений (каждые 5 минут)
        self.scheduler.add_job(
            func=self._send_pending_notifications_task,
            trigger=IntervalTrigger(minutes=check_interval_minutes),
            id='send_pending_notifications',
            name='Отправка отложенных уведомлений',
            replace_existing=True,
            misfire_grace_time=60
        )
        
        # Задача 2: Напоминания о бронированиях (каждый час в 00 минут)
        self.scheduler.add_job(
            func=self._send_booking_reminders_task,
            trigger=IntervalTrigger(hours=1),
            id='send_booking_reminders',
            name='Напоминания о бронированиях',
            replace_existing=True,
            misfire_grace_time=300
        )
        
        self.scheduler.start()
        self._is_running = True
        
        logger.info(f"Планировщик запущен. Проверка уведомлений каждые {check_interval_minutes} мин.")
        logger.info("Напоминания о бронированиях проверяются каждый час")
        
    except Exception as e:
        logger.error(f"Ошибка при запуске планировщика: {e}")
        self._is_running = False
```

---

### 5.4. HTML-шаблон для напоминания

**Файл:** `app/services/email_service.py`

Добавить новый метод после `create_room_disabled_html`:

```python
@staticmethod
def create_booking_reminder_html(
    user_name: str,
    workspace_name: str,
    room_name: str,
    room_address: str,
    booking_date: str
) -> str:
    """
    Создание HTML шаблона для напоминания о бронировании
    
    Args:
        user_name: Имя пользователя
        workspace_name: Название рабочего места
        room_name: Название помещения
        room_address: Адрес помещения
        booking_date: Дата бронирования
    
    Returns:
        HTML строка
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #2196f3; color: white; padding: 20px; text-align: center; }}
            .content {{ background-color: #f9f9f9; padding: 20px; margin-top: 10px; }}
            .info-box {{ background-color: white; border-left: 4px solid #2196f3; padding: 15px; margin: 15px 0; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            h1 {{ margin: 0; font-size: 24px; }}
            h2 {{ color: #2196f3; font-size: 18px; }}
            .detail {{ margin: 10px 0; }}
            .label {{ font-weight: bold; color: #555; }}
            .reminder-badge {{ 
                background-color: #fff3cd; 
                border: 2px solid #ffc107; 
                padding: 10px; 
                border-radius: 5px; 
                margin: 15px 0;
                text-align: center;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📅 Напоминание о бронировании</h1>
            </div>
            <div class="content">
                <p>Здравствуйте, <strong>{user_name}</strong>!</p>
                
                <div class="reminder-badge">
                    ⏰ Не забудьте посетить офис завтра!
                </div>
                
                <p>Напоминаем вам о предстоящем бронировании рабочего места.</p>
                
                <div class="info-box">
                    <h2>Детали бронирования:</h2>
                    <div class="detail">
                        <span class="label">🪑 Рабочее место:</span> {workspace_name}
                    </div>
                    <div class="detail">
                        <span class="label">🏢 Помещение:</span> {room_name}
                    </div>
                    <div class="detail">
                        <span class="label">📍 Адрес:</span> {room_address or 'Не указан'}
                    </div>
                    <div class="detail">
                        <span class="label">📅 Дата:</span> {booking_date}
                    </div>
                </div>
                
                <p>Желаем продуктивного дня!</p>
                
                <p>С уважением,<br>Команда Seat Reservation System</p>
            </div>
            <div class="footer">
                <p>Это автоматическое напоминание. Если вы больше не хотите получать уведомления, обратитесь к администратору.</p>
            </div>
        </div>
    </body>
    </html>
    """
```

---

## 6. Итоговый чек-лист

### ✅ Реализовано
- [x] Уведомление об отмене бронирования
- [x] Уведомление об отключении рабочего места
- [x] Уведомление об отключении помещения
- [x] Планировщик для pending уведомлений
- [x] SMTP интеграция (Resend/Gmail)

### ❌ Требуется доработка
- [ ] Добавить метод `send_booking_reminder_notification()`
- [ ] Добавить задачу `_send_booking_reminders_task()`
- [ ] Зарегистрировать задачу в планировщике
- [ ] Добавить HTML-шаблон `create_booking_reminder_html()`
- [ ] Создать тестовый скрипт `test_booking_reminder.py`

### ⚠️ Рекомендуется улучшить
- [ ] Убрать дублирование кода (создать `_create_and_send_notification()`)
- [ ] Добавить проверку на активные бронирования при отключении места
- [ ] Добавить логирование всех отправленных уведомлений
- [ ] Создать дашборд админа для просмотра статистики уведомлений

---

## 7. Проверка работы

### Тест 1: Отмена бронирования
```bash
cd SeatReservetion_back
python test_booking_cancel_notification.py
```

### Тест 2: Отключение помещения
```bash
python test_room_notification.py
```

### Тест 3: Напоминание (после доработки)
```bash
python test_booking_reminder.py
```

---

**Ревью выполнено:** 1 апреля 2026  
**Статус:** ⚠️ Требуется доработка (напоминания за 6 часов)  
**Приоритет:** 🔴 Высокий (критичный функционал)
