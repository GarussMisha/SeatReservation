# Инструкция по активации системы уведомлений

## 1. Установка зависимостей

```bash
cd SeatReservetion_back
pip install -r requirements.txt
```

Или вручную:
```bash
pip install APScheduler>=3.10.0
```

## 2. Настройка SMTP

Откройте файл `.env` и заполните SMTP настройки:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=ваш-email@gmail.com
SMTP_PASSWORD=ваш-app-password
SMTP_FROM_EMAIL=noreply@seatreservation.com
SMTP_FROM_NAME=Seat Reservation System
SMTP_USE_TLS=True
```

### Для Gmail:
1. Включите двухфакторную аутентификацию
2. Создайте App Password: https://myaccount.google.com/apppasswords
3. Используйте App Password вместо обычного пароля

## 3. Создание таблицы notifications

Таблица будет создана автоматически при следующем запуске сервера, так как модель добавлена в систему.

Если таблицы не создаются автоматически, можно создать вручную через SQLAlchemy:

```python
from app.core.database import engine
from app.models.notification import Notification

# Создать таблицу
Notification.__table__.create(engine)
```

## 4. Создание статусов для уведомлений

При запуске сервера статусы создаются автоматически. Если нужно создать вручную:

```python
from app.core.database import SessionLocal
from app.models.status import Status

db = SessionLocal()

statuses = [
    Status(name="pending", description="Ожидает отправки"),
    Status(name="sent", description="Отправлено"),
    Status(name="failed", description="Ошибка отправки"),
    Status(name="cancelled", description="Отменено")
]

for status in statuses:
    db.merge(status)  # merge вместо add для обновления существующих

db.commit()
db.close()
```

## 5. Запуск сервера

```bash
cd SeatReservetion_back
python start.py
```

Или:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 6. Проверка работы

### Проверка API:
Откройте Swagger UI: http://localhost:8000/docs

Проверьте новые endpoints:
- `GET /api/v1/notifications/my` - мои уведомления
- `GET /api/v1/notifications/` - все уведомления (админ)
- `POST /api/v1/notifications/schedule` - запланировать рассылку (админ)
- `GET /api/v1/notifications/stats/overview` - статистика (админ)

### Проверка автоматических уведомлений:

1. **Отмена бронирования:**
   - Отмените бронирование через API или фронтенд
   - Пользователь должен получить email

2. **Отключение рабочего места:**
   - Измените `is_active` на `false` у рабочего места
   - Все пользователи с активными бронированиями этого места получат email

3. **Отключение помещения:**
   - Измените статус помещения с `available` на другой
   - Все пользователи с бронированиями в этом помещении получат email

## 7. Настройка планировщика

Планировщик проверяет отложенные уведомления каждые 5 минут.

Для изменения интервала откройте `app/main.py` и измените параметр:

```python
start_notification_scheduler(check_interval_minutes=10)  # каждые 10 минут
```

## 8. Мониторинг

### Логи планировщика:
Планировщик пишет логи в консоль при запуске и остановке.

### Проверка отложенных уведомлений:
```sql
SELECT * FROM notifications WHERE scheduled_at IS NOT NULL;
```

### Статистика через API:
```bash
GET /api/v1/notifications/stats/overview
```

## 9. Возможные проблемы

### Уведомления не отправляются
- Проверьте логи на ошибки SMTP
- Убедитесь, что у пользователей заполнен email
- Проверьте настройки SMTP в `.env`

### Ошибка аутентификации SMTP
- Для Gmail используйте App Password, а не обычный пароль
- Убедитесь, что включена двухфакторная аутентификация

### Планировщик не запускается
- Проверьте, что APScheduler установлен: `pip list | grep APScheduler`
- Проверьте логи при старте сервера

## 10. Документация

Полная документация API уведомлений находится в файле:
`qwen/work/NOTIFICATION_API.md`

Swagger документация доступна по адресу:
http://localhost:8000/docs
