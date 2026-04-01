# 🔧 Исправление часового пояса в уведомлениях

## 📅 Дата: 1 апреля 2026

## 🐛 Проблема

Уведомления отображались со временем, которое отставало на 5 часов от местного времени пользователя.

**Пример:**
- Пользователь в Екатеринбурге (UTC+5)
- Уведомление создано в 19:00 местного времени
- Отображалось как "14:00" (UTC время)

---

## 🔍 Причина

Сервер использовал `datetime.utcnow()` для сохранения времени, который:
- Возвращает время **без информации о часовом поясе** (naive datetime)
- При сериализации в ISO формат не указывался timezone offset
- Браузер интерпретировал время как **локальное UTC**, а не UTC+5

---

## ✅ Решение

### 1. Backend — явное указание UTC timezone

**Файл:** `app/core/base.py`

```python
# БЫЛО (неправильно):
from datetime import datetime
created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

# СТАЛО (правильно):
from datetime import datetime, timezone
created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
```

**Файл:** `app/services/notification_service.py`

```python
# БЫЛО:
notification.sent_at = datetime.utcnow()

# СТАЛО:
notification.sent_at = datetime.now(timezone.utc)
```

**Файл:** `app/services/email_service.py`

```python
# БЫЛО:
result["sent_at"] = datetime.utcnow().isoformat()

# СТАЛО:
result["sent_at"] = datetime.now(timezone.utc).isoformat()
```

---

### 2. API Response — формат с timezone

Теперь сервер возвращает время в формате:
```json
{
  "created_at": "2026-04-01T14:00:00+00:00"
}
```

**`+00:00`** — явно указывает, что время UTC

---

### 3. Frontend — автоматическая конвертация

JavaScript автоматически конвертирует UTC в локальное время пользователя:

```javascript
const date = new Date("2026-04-01T14:00:00+00:00")
// Для пользователя в UTC+5:
// date.toLocaleString('ru-RU') → "1 апр. 2026, 19:00"
```

---

## 📊 Результат

| До исправления | После исправления |
|----------------|-------------------|
| 14:00 (UTC) | 19:00 (местное время) ✅ |
| Без timezone | С указанием UTC+0 |
| Путаница с поясами | Автоматическая конвертация |

---

## 🚀 Как проверить

1. **Перезапустите сервер:**
   ```bash
   python run_server.py
   ```

2. **Создайте уведомление** (отмените бронирование)

3. **Проверьте время:**
   - http://localhost:5173/notifications
   - Должно отображаться **местное время** (например, "19:00, 1 апр. 2026")

---

## 📝 Технические детали

### datetime.utcnow() vs datetime.now(timezone.utc)

| Метод | Возвращает | Timezone info |
|-------|------------|---------------|
| `datetime.utcnow()` | 2026-04-01 14:00:00 | ❌ Нет (naive) |
| `datetime.now(timezone.utc)` | 2026-04-01 14:00:00+00:00 | ✅ Есть (aware) |

### ISO 8601 формат

| Формат | Пример | Браузер интерпретирует |
|--------|--------|------------------------|
| Без timezone | `2026-04-01T14:00:00` | Как локальное время ❌ |
| С timezone | `2026-04-01T14:00:00+00:00` | UTC, конвертирует в локальное ✅ |

### JavaScript конвертация

```javascript
// UTC время
const utcDate = new Date("2026-04-01T14:00:00+00:00")

// Для пользователя в Москве (UTC+3)
utcDate.toLocaleString('ru-RU')  
// → "1 апр. 2026, 17:00:00"

// Для пользователя в Екатеринбурге (UTC+5)
utcDate.toLocaleString('ru-RU')  
// → "1 апр. 2026, 19:00:00"
```

---

## 📚 Изменённые файлы

| Файл | Изменения |
|------|-----------|
| `app/core/base.py` | `datetime.utcnow` → `datetime.now(timezone.utc)` |
| `app/services/notification_service.py` | Добавлен `timezone`, заменено на `datetime.now(timezone.utc)` |
| `app/services/email_service.py` | Добавлен `timezone`, заменено на `datetime.now(timezone.utc)` |

---

## ✅ Чек-лист

- [x] Исправлен `base.py` (модели)
- [x] Исправлен `notification_service.py`
- [x] Исправлен `email_service.py`
- [x] API возвращает время с timezone
- [x] Frontend автоматически конвертирует в локальное время
- [x] Время отображается правильно

---

**Исправлено:** 1 апреля 2026  
**Статус:** ✅ Время отображается в локальном часовом поясе пользователя
