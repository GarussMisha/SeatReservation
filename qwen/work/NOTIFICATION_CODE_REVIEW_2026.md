# 🔍 Code Review: Система уведомлений

## 📅 Дата: 1 апреля 2026

## 📊 Статус: ✅ ТРЕБУЕТСЯ ДОРАБОТКА

---

## 1. Текущая архитектура

### 1.1. Направления уведомлений

| Направление | Реализация | Статус |
|-------------|------------|--------|
| **Email** | `email_service.py` + HTML шаблоны | ✅ Работает |
| **Сайт (frontend)** | JSON данные + Vue компонент | ✅ Работает |

### 1.2. Поток данных

```
┌─────────────────────────────────────────────────────────┐
│  notification_service.py                                │
│                                                          │
│  1. get_booking_cancelled_data() → JSON (для БД)       │
│  2. create_booking_cancelled_html() → HTML (для email) │
│                                                          │
│  3. Сохраняет JSON в БД                                 │
│  4. Отправляет HTML по email                            │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Найденные проблемы

### 2.1. ❌ Отсутствует управление уведомлениями

**Проблема:**
- Нет настроек "вкл/выкл" для email уведомлений
- Нет настроек "вкл/выкл" для уведомлений на сайте
- Пользователь не может управлять своими уведомлениями

**Где должно быть:**
- Таблица БД `user_notification_settings` (user_id, email_enabled, site_enabled)
- API endpoints для управления настройками
- UI в личном кабинете пользователя

---

### 2.2. ❌ Отсутствует централизованная конфигурация SMTP

**Проблема:**
- Настройки SMTP в `.env` файле
- Админ не может изменить настройки через UI
- Нет проверки настроек SMTP

**Где должно быть:**
- Таблица БД `notification_settings` (smtp_host, smtp_port, smtp_user, smtp_password)
- UI в админ-панели для настройки SMTP
- API endpoints для обновления настроек

---

### 2.3. ⚠️ Дублирование данных в шаблонах

**Файл:** `app/services/notification_templates.py`

**Проблема:**
Одни и те же данные определяются дважды:
- `get_booking_cancelled_data()` — JSON для frontend
- `create_booking_cancelled_html()` — HTML для email

**Пример дублирования:**
```python
# JSON
"items": [
    {"icon": "🪑", "label": "Место", "value": workspace_name},
    {"icon": "🏢", "label": "Помещение", "value": room_address},
]

# HTML (дублируется)
<div class="detail">
    <span class="label">🪑 Место:</span>
    <span class="value">{workspace_name}</span>
</div>
```

**Решение:**
Создать базовые данные один раз, генерировать JSON и HTML из одного источника.

---

### 2.4. ⚠️ Нет проверки наличия email перед отправкой

**Файл:** `app/services/notification_service.py`

**Проблема:**
```python
if not user.email:
    result["message"] = "У пользователя нет email"
    logger.warning(...)
    return result  # Просто выход, но уведомление в БД сохраняется
```

**Решение:**
Не создавать уведомление в БД, если email не настроен и отправка невозможна.

---

### 2.5. ⚠️ Мёртвый код: send_email_batch()

**Файл:** `app/services/email_service.py`

**Проблема:**
Метод `send_email_batch()` существует, но **нигде не используется**.

```python
def send_email_batch(
    self,
    recipients: List[Dict[str, str]],
    subject: str,
    html_content: str,
    text_content: Optional[str] = None
) -> Dict[str, Any]:
    """Массовая рассылка email"""
    # ... код ...
```

**Где должен использоваться:**
- Рассылка от админа (`POST /api/v1/notifications/schedule`)

**Решение:**
- Либо использовать в `send_pending_notifications()`
- Либо удалить как мёртвый код

---

### 2.6. ⚠️ Планировщик не проверяет настройки

**Файл:** `app/services/scheduler_service.py`

**Проблема:**
```python
def _send_booking_reminders_task(self):
    # Отправляет напоминания ВСЕМ пользователям
    # Нет проверки:
    # - Включены ли email уведомления у пользователя
    # - Настроен ли SMTP
```

**Решение:**
Добавить проверку настроек пользователя перед отправкой.

---

## 3. Рекомендуемая архитектура

### 3.1. База данных

**Новые таблицы:**

```sql
-- Настройки уведомлений пользователя
CREATE TABLE user_notification_settings (
    id INTEGER PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    email_enabled BOOLEAN DEFAULT TRUE,
    site_enabled BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES accounts(id)
);

-- Глобальные настройки уведомлений
CREATE TABLE notification_settings (
    id INTEGER PRIMARY KEY,
    smtp_host VARCHAR(255),
    smtp_port INTEGER,
    smtp_user VARCHAR(255),
    smtp_password VARCHAR(255),
    smtp_from_email VARCHAR(255),
    smtp_from_name VARCHAR(255),
    smtp_use_tls BOOLEAN DEFAULT TRUE
);
```

---

### 3.2. Обновлённый поток данных

```
┌─────────────────────────────────────────────────────────┐
│  notification_service.py                                │
│                                                          │
│  1. Проверка настроек пользователя                      │
│     - email_enabled = True?                             │
│     - site_enabled = True?                              │
│                                                          │
│  2. Проверка настроек SMTP                              │
│     - SMTP настроен?                                    │
│                                                          │
│  3. Генерация данных (один раз)                         │
│     - notification_data = get_booking_cancelled_data() │
│                                                          │
│  4. Сохранение в БД (всегда)                            │
│     - notification.message = json.dumps(data)           │
│                                                          │
│  5. Отправка email (если включено)                      │
│     - IF email_enabled AND SMTP configured:             │
│         html = create_booking_cancelled_html(data)      │
│         email_service.send_email(html)                  │
└─────────────────────────────────────────────────────────┘
```

---

### 3.3. API Endpoints

**Пользователь:**
```bash
# Получить мои настройки уведомлений
GET /api/v1/notifications/settings
Authorization: Bearer <token>

# Обновить мои настройки
PUT /api/v1/notifications/settings
{
  "email_enabled": true,
  "site_enabled": true
}
```

**Админ:**
```bash
# Получить глобальные настройки SMTP
GET /api/v1/admin/notification-settings

# Обновить настройки SMTP
PUT /api/v1/admin/notification-settings
{
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_user": "...",
  "smtp_password": "...",
  "smtp_from_email": "noreply@example.com",
  "smtp_from_name": "Site Name"
}

# Проверить настройки SMTP (тестовое письмо)
POST /api/v1/admin/notification-settings/test
{
  "test_email": "admin@example.com"
}
```

---

### 3.4. Frontend

**Страница настроек пользователя:**
```
http://localhost:5173/profile/notifications

┌─────────────────────────────────────────┐
│ Настройки уведомлений                   │
├─────────────────────────────────────────┤
│ ☑ Email уведомления                     │
│   Получать уведомления на email         │
│                                         │
│ ☑ Уведомления на сайте                  │
│   Показывать уведомления в браузере     │
├─────────────────────────────────────────┤
│              [Сохранить]                │
└─────────────────────────────────────────┘
```

**Админ-панель (SMTP настройки):**
```
http://localhost:5173/admin/notifications

┌─────────────────────────────────────────┐
│ Настройки SMTP сервера                  │
├─────────────────────────────────────────┤
│ SMTP Host:     [smtp.gmail.com      ]   │
│ SMTP Port:     [587                 ]   │
│ SMTP User:     [noreply@example.com]   │
│ SMTP Password: [••••••••••••••••   ]   │
│ From Email:    [noreply@example.com]   │
│ From Name:     [Site Name           ]   │
│ Use TLS:       [☑]                      │
├─────────────────────────────────────────┤
│ [Сохранить]  [Отправить тестовое письмо]│
└─────────────────────────────────────────┘
```

---

## 4. План доработок

### Этап 1: База данных (Приоритет: 🔴 Высокий)

**Файлы:**
- `app/models/notification_settings.py` (новая)
- `app/models/user_notification_settings.py` (новая)
- `app/core/database.py`

**Задачи:**
1. Создать модели БД
2. Добавить миграции
3. Создать данные по умолчанию

---

### Этап 2: Backend API (Приоритет: 🔴 Высокий)

**Файлы:**
- `app/api/v1/routes/notification_settings.py` (новая)
- `app/api/v1/routes/admin.py` (обновление)
- `app/schemas/notification_settings.py` (новая)

**Задачи:**
1. Создать endpoints для пользователя
2. Создать endpoints для админа
3. Обновить `notification_service.py` для проверки настроек

---

### Этап 3: Frontend (Приоритет: 🟡 Средний)

**Файлы:**
- `src/views/NotificationSettings.vue` (новая)
- `src/components/admin/NotificationSettings.vue` (новая)
- `src/stores/notificationSettings.js` (новая)

**Задачи:**
1. Страница настроек пользователя
2. Страница настроек SMTP в админ-панели
3. Store для управления настройками

---

### Этап 4: Рефакторинг (Приоритет: 🟢 Низкий)

**Файлы:**
- `app/services/notification_templates.py`

**Задачи:**
1. Убрать дублирование данных
2. Создать базовый класс для шаблонов
3. Генерировать JSON и HTML из одного источника

**Пример:**
```python
class BaseNotificationTemplate:
    def __init__(self, user_name, workspace_name, room_address, booking_date):
        self.data = {
            "workspace_name": workspace_name,
            "room_address": room_address,
            "booking_date": booking_date
        }
    
    def get_json(self):
        """JSON для frontend"""
        return {
            "items": [
                {"icon": "🪑", "label": "Место", "value": self.data["workspace_name"]},
                {"icon": "🏢", "label": "Помещение", "value": self.data["room_address"]}
            ]
        }
    
    def get_html(self):
        """HTML для email"""
        return f"""
        <div>
            <div>🪑 Место: {self.data["workspace_name"]}</div>
            <div>🏢 Помещение: {self.data["room_address"]}</div>
        </div>
        """
```

---

### Этап 5: Удаление мёртвого кода (Приоритет: 🟢 Низкий)

**Файлы:**
- `app/services/email_service.py`

**Задачи:**
1. Удалить `send_email_batch()` (или использовать)
2. Обновить документацию

---

## 5. Итоговый чек-лист

### Критичные проблемы
- [ ] Нет управления уведомлениями (вкл/выкл)
- [ ] Нет UI для настройки SMTP
- [ ] Планировщик не проверяет настройки

### Дублирование кода
- [ ] Шаблоны уведомлений (JSON + HTML) дублируют данные

### Мёртвый код
- [ ] `send_email_batch()` не используется

### Документация
- [ ] Обновить документацию с новыми настройками

---

## 6. Рекомендации

### 6.1. Немедленные действия

1. **Создать таблицу `user_notification_settings`**
   - Позволит пользователям отключать email уведомления
   - Снизит нагрузку на SMTP

2. **Добавить проверку SMTP настроек**
   - Перед отправкой проверять `email_service.is_configured()`
   - Логировать ошибки настройки

3. **Удалить `send_email_batch()`**
   - Если не используется — удалить
   - Если нужен — добавить использование

---

### 6.2. Краткосрочные улучшения

1. **Страница настроек пользователя**
   - Позволит управлять своими уведомлениями
   - Улучшит UX

2. **Админ-панель для SMTP**
   - Админ сможет менять настройки без доступа к `.env`
   - Тестовое письмо для проверки

---

### 6.3. Долгосрочные улучшения

1. **Рефакторинг шаблонов**
   - Убрать дублирование
   - Упростить поддержку

2. **Расширенные настройки**
   - Настройки по типам уведомлений
   - "Тихие часы" (не отправлять ночью)

---

**Ревью выполнено:** 1 апреля 2026  
**Статус:** ⚠️ Требуется доработка  
**Приоритет:** 🔴 Высокий (настройки пользователя)
