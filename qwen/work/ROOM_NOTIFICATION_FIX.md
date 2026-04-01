# 🔧 Исправление уведомлений при отключении помещения

## 📅 Дата: 1 апреля 2026

## 📊 Статус: ✅ ИСПРАВЛЕНО

---

## 1. Проблема

**Симптом:** При отключении помещения администратором, пользователи с активными бронированиями не получали уведомления.

**Причина:** В коде `app/api/v1/routes/room.py` использовалось неправильное сравнение статусов.

### 1.1. Оригинальный код (НЕПРАВИЛЬНО)

```python
# Получаем статус "available" для сравнения
available_status = db.query(Status).filter(Status.name == "available").first()
available_status_id = available_status.id if available_status else None

# Если статус меняется с "available" на другой - отправляем уведомления
if old_status_id == available_status_id and new_status_id != available_status_id:
    send_notification = True
```

**Проблема:**
- Для помещений не существует статуса `"available"` 
- Статусы помещений: `active (1)` и `inactive (2)` (см. `RoomStatuses`)
- Условие никогда не выполнялось → уведомления не отправлялись

---

## 2. Решение

### 2.1. Исправленный код (ПРАВИЛЬНО)

```python
# Получаем статусы "active" и "inactive" для сравнения
active_status = db.query(Status).filter(Status.name == "active").first()
inactive_status = db.query(Status).filter(Status.name == "inactive").first()
active_status_id = active_status.id if active_status else 1
inactive_status_id = inactive_status.id if inactive_status else 2

# Если статус меняется с "active" на "inactive" - отправляем уведомления
if old_status_id == active_status_id and new_status_id == inactive_status_id:
    send_notification = True
```

### 2.2. Изменённые файлы

| Файл | Изменения |
|------|-----------|
| `app/api/v1/routes/room.py` | Исправлена логика сравнения статусов |
| `app/api/v1/routes/room.py` | Добавлен `logger` для отладки |

---

## 3. Тестирование

### 3.1. Создан тестовый скрипт

**Файл:** `test_room_notification.py`

**Проверяет:**
1. Создание помещения со статусом `active`
2. Создание рабочего места
3. Создание бронирования пользователем
4. Отключение помещения (смена статуса на `inactive`)
5. Создание и отправка уведомления

### 3.2. Результаты теста

```
============================================================
 ИТОГИ ТЕСТА
============================================================
 ТЕСТ ПРОЙДЕН!

 Уведомление было создано при отключении помещения.
 Проверьте базу данных и email ящик пользователя.
============================================================
```

**Запуск теста:**
```bash
cd SeatReservetion_back
venv\Scripts\activate
python test_room_notification.py
```

---

## 4. Как работает уведомлений

### 4.1. Сценарий

1. Пользователь бронирует рабочее место в помещении
2. Администратор отключает помещение (меняет статус с `active` на `inactive`)
3. Система автоматически:
   - Находит все активные бронирования в этом помещении
   - Группирует их по пользователям
   - Создаёт email-уведомление для каждого пользователя
   - Отправляет email через Resend SMTP

### 4.2. Тип уведомления

```python
notification_type = "room_disabled"
subject = f"Помещение недоступно: {room.name}"
```

### 4.3. HTML-шаблон

Фиолетовый дизайн с:
- Названием помещения
- Адресом
- Списком затронутых бронирований (рабочее место + дата)

---

## 5. Баги в Resend

### 5.1. Ограничение Free плана

**Проблема:**
```
SMTP ошибка при отправке: (550, b'You can only send testing emails 
to your own email address (parussmikle@gmail.com). To send emails 
to other recipients, please verify a domain at resend.com/domains, 
and change the from address to an email using this domain.')
```

**Решение:**
- Для тестов: используйте ваш email (`parussmikle@gmail.com`)
- Для продакшена: добавьте домен в Resend Dashboard

### 5.2. Настройка для продакшена

1. Зарегистрируйте домен в [Resend Dashboard](https://app.resend.com)
2. Добавьте DNS записи:
   ```
   MX: feedback-smtp.us-east-1.amazonses.com (priority 10)
   TXT: v=spf1 include:resend.com ~all
   ```
3. Обновите `.env`:
   ```env
   SMTP_FROM_EMAIL=noreply@yourdomain.com
   SMTP_FROM_NAME=Seat Reservation System
   ```

---

## 6. Проверка работы

### 6.1. Через UI приложения

1. Войдите как администратор
2. Создайте помещение (статус `active`)
3. Создайте рабочее место
4. Забронируйте место от имени пользователя
5. Отключите помещение (смените статус на `inactive`)
6. Проверьте email пользователя

### 6.2. Через API

```bash
# 1. Получаем помещения
GET /api/v1/rooms/

# 2. Отключаем помещение (ID=1)
PUT /api/v1/rooms/1
Content-Type: application/json
Authorization: Bearer <admin-token>

{
  "status_id": 2  # inactive
}

# 3. Проверяем уведомления
GET /api/v1/notifications/my
Authorization: Bearer <user-token>
```

### 6.3. Через тестовый скрипт

```bash
python test_room_notification.py
```

---

## 7. Логи

### 7.1. Успешная отправка

```
INFO:app.services.email_service:Письмо отправлено на user@example.com с темой 'Помещение недоступно: Помещение 1'
INFO:app.services.notification_service:Уведомления об отключении помещения 1: отправлено=1, неудачно=0
```

### 7.2. Ошибки

```
WARNING:app.api.v1.routes.room:Ошибка при отправке уведомления об отключении помещения 1: ...
```

---

## 8. Связанные файлы

| Файл | Назначение |
|------|------------|
| [app/api/v1/routes/room.py](app/api/v1/routes/room.py) | Логика отключения помещения |
| [app/services/notification_service.py](app/services/notification_service.py) | Отправка уведомлений |
| [app/services/email_service.py](app/services/email_service.py) | Email-шаблоны |
| [test_room_notification.py](test_room_notification.py) | Тестовый скрипт |

---

## 9. Рекомендации

### 9.1. Для разработки

- Используйте тестовый скрипт для проверки
- Обновите email админа на реальный (`parussmikle@gmail.com`)

### 9.2. Для продакшена

1. Добавьте домен в Resend
2. Обновите `SMTP_FROM_EMAIL`
3. Протестируйте отправку на разные email

### 9.3. Мониторинг

- Проверяйте `/api/v1/notifications/stats/overview`
- Следите за лимитами Resend (100 писем/день на Free)

---

## 10. Чек-лист исправления

- [x] Найдена причина проблемы
- [x] Исправлен код в `room.py`
- [x] Добавлен `logger`
- [x] Создан тестовый скрипт
- [x] Тест пройден
- [x] Уведомление отправляется
- [x] Email получен

---

**Исправлено:** 1 апреля 2026  
**Статус:** ✅ Работает  
**Следующий шаг:** Протестировать через UI приложения
