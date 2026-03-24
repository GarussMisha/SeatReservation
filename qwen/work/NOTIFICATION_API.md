# API уведомлений (Notifications)

## Обзор

Система уведомлений позволяет отправлять пользователям email-уведомления о различных событиях в системе бронирования рабочих мест.

### Типы уведомлений

| Тип | Описание | Триггер |
|-----|----------|---------|
| `booking_cancelled` | Отмена бронирования | Админ отменяет бронирование |
| `workspace_disabled` | Рабочее место недоступно | Админ отключает рабочее место (`is_active: false`) |
| `room_disabled` | Помещение недоступно | Админ меняет статус помещения с `available` на другой |
| `custom` | Произвольное уведомление | Админ создает рассылку вручную |

---

## Настройка SMTP

Перед использованием необходимо настроить SMTP-сервер в `.env` файле бэкенда:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@seatreservation.com
SMTP_FROM_NAME=Seat Reservation System
SMTP_USE_TLS=True
```

### Для Gmail

1. Включите двухфакторную аутентификацию
2. Создайте App Password: https://myaccount.google.com/apppasswords
3. Используйте App Password вместо обычного пароля

---

## API Endpoints

### 1. Получить мои уведомления (пользователь)

**GET** `/api/v1/notifications/my`

Требует аутентификации.

**Параметры запроса:**
- `limit` (int, optional): Количество записей (по умолчанию 50, макс 100)
- `skip` (int, optional): Пропуск записей (по умолчанию 0)

**Пример запроса:**
```javascript
GET /api/v1/notifications/my?limit=20&skip=0
Authorization: Bearer <token>
```

**Пример ответа:**
```json
{
  "notifications": [
    {
      "id": 1,
      "type": "booking_cancelled",
      "subject": "Отмена бронирования: Место-101 на 2026-03-25",
      "message": "<html>...</html>",
      "scheduled_at": null,
      "sent_at": "2026-03-24T10:30:00",
      "created_at": "2026-03-24T10:29:55",
      "status_name": "sent",
      "user_id": 5
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 20
}
```

---

### 2. Получить все уведомления (админ)

**GET** `/api/v1/notifications/`

Требует прав администратора.

**Параметры запроса:**
- `notification_type` (string, optional): Фильтр по типу
- `status_id` (int, optional): Фильтр по статусу
- `user_id` (int, optional): Фильтр по пользователю
- `limit` (int, optional): Лимит записей (по умолчанию 100)
- `skip` (int, optional): Пропуск записей

**Пример запроса:**
```javascript
GET /api/v1/notifications/?notification_type=booking_cancelled&limit=50
Authorization: Bearer <admin-token>
```

---

### 3. Получить уведомление по ID (админ)

**GET** `/api/v1/notifications/{notification_id}`

Требует прав администратора.

**Пример ответа:**
```json
{
  "id": 1,
  "notification_type": "booking_cancelled",
  "subject": "Отмена бронирования: Место-101 на 2026-03-25",
  "message": "<html>...</html>",
  "scheduled_at": null,
  "sent_at": "2026-03-24T10:30:00",
  "created_at": "2026-03-24T10:29:55",
  "status_id": 3,
  "status_name": "sent",
  "user_id": 5,
  "created_by_id": null,
  "recipient_name": "Иван Петров",
  "creator_name": null
}
```

---

### 4. Запланировать рассылку (админ)

**POST** `/api/v1/notifications/schedule`

Требует прав администратора.

**Тело запроса:**
```json
{
  "user_ids": [1, 2, 3, 4, 5],
  "subject": "Технические работы в офисе",
  "message": "Уважаемые коллеги! 25 марта офис будет закрыт на технические работы.",
  "scheduled_at": "2026-03-25T09:00:00"
}
```

**Параметры:**
- `user_ids` (array[int]): Список ID пользователей для рассылки
- `subject` (string): Тема сообщения (макс 255 символов)
- `message` (string): Текст сообщения
- `scheduled_at` (datetime): Время отправки (UTC, должно быть в будущем)

**Пример ответа:**
```json
{
  "message": "Создано 5 отложенных уведомлений",
  "notifications_created": 5,
  "notification_ids": [10, 11, 12, 13, 14],
  "scheduled_at": "2026-03-25T09:00:00"
}
```

---

### 5. Массовая отправка уведомлений (админ)

**POST** `/api/v1/notifications/bulk-send`

Требует прав администратора.

**Тело запроса (немедленная отправка):**
```json
{
  "user_ids": [1, 2, 3],
  "subject": "Важное объявление",
  "message": "Текст сообщения...",
  "send_now": true
}
```

**Тело запроса (отложенная отправка):**
```json
{
  "user_ids": [1, 2, 3],
  "subject": "Важное объявление",
  "message": "Текст сообщения...",
  "send_now": false,
  "scheduled_at": "2026-03-25T09:00:00"
}
```

---

### 6. Повторная отправка уведомления (админ)

**POST** `/api/v1/notifications/{notification_id}/resend`

Требует прав администратора.

**Пример ответа:**
```json
{
  "message": "Уведомление успешно отправлено повторно",
  "sent_at": "2026-03-24T11:00:00"
}
```

---

### 7. Отменить уведомление (админ)

**DELETE** `/api/v1/notifications/{notification_id}`

Требует прав администратора.

Нельзя отменить уже отправленное уведомление.

**Пример ответа:** `204 No Content`

---

### 8. Получить статистику уведомлений (админ)

**GET** `/api/v1/notifications/stats/overview`

Требует прав администратора.

**Пример ответа:**
```json
{
  "total_notifications": 150,
  "pending_notifications": 10,
  "sent_notifications": 135,
  "failed_notifications": 3,
  "scheduled_notifications": 5,
  "notifications_by_type": {
    "booking_cancelled": 80,
    "workspace_disabled": 30,
    "room_disabled": 20,
    "custom": 20
  }
}
```

---

### 9. Отправить ожидающие уведомления (админ)

**POST** `/api/v1/notifications/send-pending`

Требует прав администратора.

Ручной запуск отправки всех запланированных уведомлений, время которых пришло.

**Пример ответа:**
```json
{
  "success": true,
  "message": "Обработано: 5, отправлено: 5, ошибок: 0, пропущено: 0",
  "processed": 5,
  "sent": 5,
  "failed": 0,
  "skipped": 0
}
```

---

## Автоматические уведомления

### При отмене бронирования

Когда администратор отменяет бронирование через `POST /api/v1/bookings/{booking_id}/cancel`, система автоматически отправляет пользователю email с информацией:

- Имя пользователя
- Название рабочего места
- Название и адрес помещения
- Дата бронирования

### При отключении рабочего места

Когда администратор меняет `is_active` на `false` через `PUT /api/v1/workspaces/{workspace_id}`, система автоматически уведомляет всех пользователей с активными бронированиями этого места.

### При отключении помещения

Когда администратор меняет статус помещения с `available` на другой через `PUT /api/v1/rooms/{room_id}`, система автоматически уведомляет всех пользователей с активными бронированиями рабочих мест в этом помещении.

---

## Статусы уведомлений

| Статус | Описание |
|--------|----------|
| `pending` | Ожидает отправки |
| `sent` | Успешно отправлено |
| `failed` | Ошибка отправки |
| `cancelled` | Отменено админом |

---

## Примеры использования на фронтенде

### React: Получение уведомлений пользователя

```javascript
import { useEffect, useState } from 'react';
import axios from 'axios';

function NotificationsPanel() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const response = await axios.get('/api/v1/notifications/my', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        setNotifications(response.data.notifications);
      } catch (error) {
        console.error('Ошибка загрузки уведомлений:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchNotifications();
  }, []);

  if (loading) return <div>Загрузка...</div>;

  return (
    <div className="notifications-panel">
      <h2>Мои уведомления</h2>
      {notifications.map(notif => (
        <div key={notif.id} className="notification-item">
          <h3>{notif.subject}</h3>
          <p>Статус: {notif.status_name}</p>
          <p>Дата: {new Date(notif.created_at).toLocaleString()}</p>
        </div>
      ))}
    </div>
  );
}
```

### React: Создание рассылки (админ)

```javascript
import { useState } from 'react';
import axios from 'axios';

function BroadcastForm() {
  const [formData, setFormData] = useState({
    user_ids: [],
    subject: '',
    message: '',
    scheduled_at: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const response = await axios.post(
        '/api/v1/notifications/schedule',
        formData,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('admin-token')}`
          }
        }
      );
      alert(`Рассылка создана: ${response.data.notifications_created} уведомлений`);
    } catch (error) {
      console.error('Ошибка создания рассылки:', error);
      alert('Ошибка: ' + error.response?.data?.detail);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Тема"
        value={formData.subject}
        onChange={e => setFormData({...formData, subject: e.target.value})}
        required
      />
      <textarea
        placeholder="Сообщение"
        value={formData.message}
        onChange={e => setFormData({...formData, message: e.target.value})}
        required
      />
      <input
        type="datetime-local"
        value={formData.scheduled_at}
        onChange={e => setFormData({...formData, scheduled_at: e.target.value})}
        required
      />
      <button type="submit">Запланировать рассылку</button>
    </form>
  );
}
```

### Vue 3: Получение уведомлений

```vue
<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const notifications = ref([]);
const loading = ref(true);

const fetchNotifications = async () => {
  try {
    const response = await axios.get('/api/v1/notifications/my', {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    });
    notifications.value = response.data.notifications;
  } catch (error) {
    console.error('Ошибка:', error);
  } finally {
    loading.value = false;
  }
};

onMounted(fetchNotifications);
</script>

<template>
  <div class="notifications">
    <h2>Уведомления</h2>
    <div v-if="loading">Загрузка...</div>
    <div v-else>
      <div v-for="notif in notifications" :key="notif.id" class="notification">
        <h3>{{ notif.subject }}</h3>
        <p>Статус: {{ notif.status_name }}</p>
      </div>
    </div>
  </div>
</template>
```

---

## Рекомендации по UI

### Панель уведомлений пользователя

- Отображать список уведомлений с иконками типов
- Показывать статус цветом (зеленый - отправлено, красный - ошибка, желтый - ожидает)
- Добавить пагинацию для больших списков
- Возможность отметить как прочитанное

### Админ-панель: Создание рассылки

- Выбор пользователей через чекбоксы или мульти-селект
- Предпросмотр письма перед отправкой
- Выбор даты/времени для отложенной отправки
- Статистика отправленных уведомлений

### Админ-панель: Управление уведомлениями

- Таблица со всеми уведомлениями
- Фильтры по типу, статусу, пользователю, дате
- Возможность повторной отправки
- Просмотр деталей уведомления

---

## Диагностика проблем

### Уведомления не отправляются

1. Проверьте настройки SMTP в `.env`
2. Убедитесь, что у пользователей заполнен email
3. Проверьте логи бэкенда на ошибки SMTP

### Ошибка аутентификации SMTP

- Для Gmail используйте App Password, а не обычный пароль
- Включите двухфакторную аутентификацию

### Уведомления отправляются с задержкой

- Планировщик проверяет уведомления каждые 5 минут (настраивается)
- Для немедленной отправки используйте `send-pending` endpoint

---

## Ссылки

- [Схема базы данных](../SeatReservetion_back/DATABASE_SCHEMA.md)
- [API документация](http://localhost:8000/docs) (Swagger UI)
