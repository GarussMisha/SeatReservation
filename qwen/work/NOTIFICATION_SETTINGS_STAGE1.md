# ✅ Этап 1: База данных настроек уведомлений

## 📅 Дата: 1 апреля 2026

## 📊 Статус: ✅ ВЫПОЛНЕНО

---

## 1. Созданные файлы

### 1.1. Модели БД

**`app/models/user_notification_settings.py`**
```python
class UserNotificationSettings(BaseModel):
    user_id: int  # ID пользователя (уникальный)
    email_enabled: bool  # Включены ли email уведомления
    site_enabled: bool  # Включены ли уведомления на сайте
```

**`app/models/notification_settings.py`**
```python
class NotificationSettings(BaseModel):
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    smtp_from_email: str
    smtp_from_name: str
    smtp_use_tls: bool
    email_notifications_enabled: bool
```

### 1.2. Схемы Pydantic

**`app/schemas/notification_settings.py`**
- `UserNotificationSettingsResponse` — ответ настроек пользователя
- `UserNotificationSettingsUpdate` — обновление настроек пользователя
- `NotificationSettingsResponse` — ответ глобальных настроек
- `NotificationSettingsUpdate` — обновление настроек SMTP
- `NotificationSettingsTestRequest` — тестирование SMTP

### 1.3. Обновлённые файлы

| Файл | Изменения |
|------|-----------|
| `app/models/__init__.py` | Добавлен импорт новых моделей |
| `app/models/account.py` | Добавлено отношение `notification_settings` |
| `app/models/notification.py` | Добавлено отношение `user_settings` |
| `app/core/database.py` | Обновлена инициализация (создание настроек по умолчанию) |

---

## 2. Структура БД

### 2.1. Таблица `user_notification_settings`

| Колонка | Тип | Описание |
|---------|-----|----------|
| `id` | INTEGER | Primary Key |
| `user_id` | INTEGER | Foreign Key → accounts.id (UNIQUE) |
| `email_enabled` | BOOLEAN | Включены ли email уведомления |
| `site_enabled` | BOOLEAN | Включены ли уведомления на сайте |
| `created_at` | DATETIME | Дата создания |
| `updated_at` | DATETIME | Дата обновления |

### 2.2. Таблица `notification_settings`

| Колонка | Тип | Описание |
|---------|-----|----------|
| `id` | INTEGER | Primary Key |
| `smtp_host` | VARCHAR(255) | SMTP хост |
| `smtp_port` | INTEGER | SMTP порт |
| `smtp_user` | VARCHAR(255) | SMTP пользователь |
| `smtp_password` | VARCHAR(255) | SMTP пароль |
| `smtp_from_email` | VARCHAR(255) | Email отправителя |
| `smtp_from_name` | VARCHAR(255) | Имя отправителя |
| `smtp_use_tls` | BOOLEAN | Использовать TLS |
| `email_notifications_enabled` | BOOLEAN | Глобально включены ли email уведомления |
| `created_at` | DATETIME | Дата создания |
| `updated_at` | DATETIME | Дата обновления |

---

## 3. Настройки по умолчанию

### 3.1. Глобальные настройки

При первом запуске создаются настройки:

```python
NotificationSettings(
    smtp_host="smtp.resend.com",
    smtp_port=465,
    smtp_user="resend",
    smtp_password="",  # Пустой пароль - админ должен настроить
    smtp_from_email="onboarding@resend.dev",
    smtp_from_name="Seat Reservation System",
    smtp_use_tls=True,
    email_notifications_enabled=True
)
```

### 3.2. Настройки пользователя

При создании пользователя автоматически создаются настройки:

```python
UserNotificationSettings(
    user_id=<id_пользователя>,
    email_enabled=True,
    site_enabled=True
)
```

---

## 4. Проверка работы

### 4.1. Проверка импорта

```bash
cd SeatReservetion_back
venv\Scripts\python.exe -c "
from app.models import NotificationSettings, UserNotificationSettings
print('✅ Модели импортируются корректно')
"
```

### 4.2. Проверка создания таблиц

```bash
python start.py --new
```

**Ожидаемый вывод:**
```
✅ Создано 20 стандартных статусов
✅ Настройки уведомлений по умолчанию созданы
✅ Тестовый администратор создан успешно!
```

---

## 5. Следующие шаги

### Этап 2: Backend API (🔴 Высокий приоритет)

**Файлы для создания:**
- `app/api/v1/routes/notification_settings.py`
- `app/schemas/notification_settings.py` (частично готово)

**Endpoints для пользователя:**
```bash
GET  /api/v1/notifications/settings          # Получить мои настройки
PUT  /api/v1/notifications/settings          # Обновить мои настройки
```

**Endpoints для админа:**
```bash
GET  /api/v1/admin/notification-settings     # Получить настройки SMTP
PUT  /api/v1/admin/notification-settings     # Обновить настройки SMTP
POST /api/v1/admin/notification-settings/test # Тестовое письмо
```

---

## 6. Связанные документы

- [NOTIFICATION_CODE_REVIEW_2026.md](NOTIFICATION_CODE_REVIEW_2026.md) — полное ревью
- [NOTIFICATION_API.md](NOTIFICATION_API.md) — документация системы уведомлений

---

**Этап 1 завершён!** ✅

**Следующий шаг:** Реализация Backend API (Этап 2).
