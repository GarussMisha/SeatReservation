# 📧 Инструкция по настройке email-уведомлений

## Обзор

Система уведомлений отправляет email пользователям о различных событиях:
- Отмена бронирования
- Отключение рабочего места
- Отключение помещения
- Произвольные рассылки от администратора

---

## 🔧 Настройка SMTP

### 1. Откройте файл `.env`

Файл находится в папке `SeatReservetion_back/.env`

### 2. Заполните SMTP настройки

```env
# =============================================================================
# НАСТРОЙКИ EMAIL / SMTP
# =============================================================================

# SMTP сервер для отправки уведомлений по email
SMTP_HOST=smtp.gmail.com

# SMTP порт (587 для TLS, 465 для SSL)
SMTP_PORT=587

# SMTP пользователь (ваш email)
SMTP_USER=ваш-email@gmail.com

# SMTP пароль (App Password для Gmail)
SMTP_PASSWORD=ваш-app-password

# Email отправителя (будет отображаться в поле "От кого")
SMTP_FROM_EMAIL=ваш-email@gmail.com

# Имя отправителя (будет отображаться вместо email)
SMTP_FROM_NAME=Seat Reservation System

# Использовать TLS (True для большинства сервисов)
SMTP_USE_TLS=True
```

---

## 📮 Настройка для популярных почтовых сервисов

### Gmail

#### Шаг 1: Включите двухфакторную аутентификацию

1. Перейдите в [Аккаунт Google](https://myaccount.google.com/)
2. Выберите **Безопасность** → **Двухэтапная аутентификация**
3. Включите двухфакторную аутентификацию

#### Шаг 2: Создайте App Password

1. Перейдите на страницу [App Passwords](https://myaccount.google.com/apppasswords)
2. Выберите приложение: **Mail**
3. Выберите устройство: **Other (Custom name)**
4. Введите имя: `Seat Reservation`
5. Нажмите **Generate**
6. Скопируйте 16-значный пароль (без пробелов)

#### Шаг 3: Заполните .env

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=ваш-email@gmail.com
SMTP_PASSWORD=abcdefghij123456  # 16-значный App Password
SMTP_FROM_EMAIL=ваш-email@gmail.com
SMTP_FROM_NAME=Seat Reservation System
SMTP_USE_TLS=True
```

---

### Yandex Mail

#### Шаг 1: Включите двухфакторную аутентификацию

1. Перейдите в [Паспорт Яндекс](https://passport.yandex.ru/profile)
2. Выберите **Безопасность** → **Двухфакторная аутентификация**
3. Включите двухфакторную аутентификацию

#### Шаг 2: Создайте пароль для внешних приложений

1. Перейдите в [Пароли для внешних приложений](https://passport.yandex.ru/profile/access)
2. Нажмите **Создать новый пароль**
3. Введите название: `Seat Reservation`
4. Скопируйте пароль

#### Шаг 3: Заполните .env

```env
SMTP_HOST=smtp.yandex.ru
SMTP_PORT=587
SMTP_USER=ваш-email@yandex.ru
SMTP_PASSWORD=пароль-для-внешних-приложений
SMTP_FROM_EMAIL=ваш-email@yandex.ru
SMTP_FROM_NAME=Seat Reservation System
SMTP_USE_TLS=True
```

---

### Outlook / Hotmail

#### Шаг 1: Включите двухфакторную аутентификацию

1. Перейдите в [Безопасность Microsoft](https://account.microsoft.com/security)
2. Выберите **Дополнительные параметры безопасности**
3. Включите двухфакторную проверку

#### Шаг 2: Создайте пароль приложения

1. Перейдите на страницу [Пароли приложений](https://account.microsoft.com/security/app-passwords)
2. Нажмите **Создать новый пароль**
3. Скопируйте пароль

#### Шаг 3: Заполните .env

```env
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USER=ваш-email@outlook.com
SMTP_PASSWORD=пароль-приложения
SMTP_FROM_EMAIL=ваш-email@outlook.com
SMTP_FROM_NAME=Seat Reservation System
SMTP_USE_TLS=True
```

---

### Mail.ru

#### Шаг 1: Включите двухфакторную аутентификацию

1. Перейдите в [Настройки Mail.ru](https://e.mail.ru/settings/)
2. Выберите **Безопасность** → **Двухфакторная аутентификация**
3. Включите двухфакторную аутентификацию

#### Шаг 2: Создайте пароль для внешних приложений

1. Перейдите в [Пароли для внешних приложений](https://e.mail.ru/settings/external)
2. Нажмите **Создать новый пароль**
3. Введите название: `Seat Reservation`
4. Скопируйте пароль

#### Шаг 3: Заполните .env

```env
SMTP_HOST=smtp.mail.ru
SMTP_PORT=587
SMTP_USER=ваш-email@mail.ru
SMTP_PASSWORD=пароль-для-внешних-приложений
SMTP_FROM_EMAIL=ваш-email@mail.ru
SMTP_FROM_NAME=Seat Reservation System
SMTP_USE_TLS=True
```

---

## 🧪 Проверка работы

### 1. Перезапустите сервер

```bash
cd SeatReservetion_back
python start.py
```

### 2. Проверьте логи

При запуске сервера проверьте, что нет ошибок SMTP:
```
✅ Планировщик уведомлений запущен (проверка каждые 5 мин)
```

### 3. Отправьте тестовое уведомление

#### Через Swagger UI:

1. Откройте http://localhost:8000/docs
2. Найдите endpoint `POST /api/v1/notifications/schedule`
3. Нажмите **Try it out**
4. Заполните данные:
   ```json
   {
     "user_ids": [1],
     "subject": "Тестовое уведомление",
     "message": "Это тестовое сообщение. Если вы его получили - настройка работает!",
     "scheduled_at": "2026-03-24T18:00:00"
   }
   ```
5. Нажмите **Execute**
6. Проверьте email пользователя с ID=1

#### Через API:

```bash
curl -X POST "http://localhost:8000/api/v1/notifications/schedule" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_ids": [1],
    "subject": "Тестовое уведомление",
    "message": "Это тестовое сообщение",
    "scheduled_at": "2026-03-24T18:00:00"
  }'
```

### 4. Проверьте статистику

```bash
GET /api/v1/notifications/stats/overview
```

Пример ответа:
```json
{
  "total_notifications": 1,
  "pending_notifications": 1,
  "sent_notifications": 0,
  "failed_notifications": 0,
  "scheduled_notifications": 1,
  "notifications_by_type": {
    "custom": 1
  }
}
```

---

## 🚨 Диагностика проблем

### Уведомления не отправляются

#### 1. Проверьте логи сервера

Ищите ошибки SMTP:
```
SMTP Authentication Error
SMTP Connect Error
```

#### 2. Проверьте настройки в .env

```bash
# Проверьте что все поля заполнены
cat .env | grep SMTP
```

#### 3. Проверьте статусы уведомлений в БД

```sql
SELECT 
    id,
    notification_type,
    subject,
    status_id,
    scheduled_at,
    sent_at,
    user_id
FROM notifications
ORDER BY created_at DESC
LIMIT 10;
```

#### 4. Проверьте что у пользователя есть email

```sql
SELECT id, login, email, first_name, last_name
FROM accounts
WHERE id = 1;
```

---

### Ошибка аутентификации SMTP

**Симптомы:**
```
SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted')
```

**Решение:**
1. Убедитесь что используете **App Password**, а не обычный пароль
2. Проверьте что включена двухфакторная аутентификация
3. Для Gmail: https://myaccount.google.com/apppasswords
4. Для Yandex: https://passport.yandex.ru/profile/access

---

### Ошибка подключения к SMTP

**Симптомы:**
```
SMTPConnectError: (421, b'Service not available')
```

**Решение:**
1. Проверьте правильность SMTP_HOST и SMTP_PORT
2. Проверьте интернет-соединение
3. Попробуйте другой порт (465 для SSL вместо 587 для TLS)

```env
# Для SSL
SMTP_PORT=465
SMTP_USE_TLS=False
```

---

### Письма попадают в спам

**Решение:**
1. Добавьте email отправителя в контакты
2. Проверьте SPF/DKIM записи домена (для корпоративной почты)
3. Используйте доменный email вместо gmail.com

---

## 📊 Типы уведомлений

### Автоматические уведомления

| Событие | Когда отправляется | Получатели |
|---------|-------------------|------------|
| Отмена бронирования | В 18:00 накануне даты бронирования | Пользователь |
| Отключение рабочего места | В 18:00 накануне первого дня бронирования | Все пользователи с бронированиями |
| Отключение помещения | В 18:00 накануне первого дня бронирования | Все пользователи с бронированиями |

### Ручные уведомления

Администратор может создать рассылку через API:

```json
POST /api/v1/notifications/schedule
{
  "user_ids": [1, 2, 3],
  "subject": "Важное объявление",
  "message": "Текст сообщения",
  "scheduled_at": "2026-03-25T09:00:00"
}
```

---

## 🔐 Безопасность

### Никогда не коммитьте .env в git!

Файл `.env` содержит чувствительные данные. Убедитесь что он в `.gitignore`:

```bash
# Проверьте .gitignore
cat .gitignore | grep env
```

Должно быть:
```
.env
```

### Используйте переменные окружения в production

Вместо `.env` файла используйте переменные окружения:

```bash
export SMTP_USER=your-email@gmail.com
export SMTP_PASSWORD=your-app-password
```

---

## 📈 Мониторинг

### Проверка статистики через API

```bash
GET /api/v1/notifications/stats/overview
```

### Проверка через БД

```sql
-- Количество уведомлений по статусам
SELECT 
    s.name as status,
    COUNT(n.id) as count
FROM notifications n
JOIN statuses s ON n.status_id = s.id
GROUP BY s.name;

-- Последние 10 уведомлений
SELECT 
    n.id,
    n.notification_type,
    n.subject,
    s.name as status,
    n.scheduled_at,
    n.sent_at,
    a.email as recipient_email
FROM notifications n
JOIN statuses s ON n.status_id = s.id
JOIN accounts a ON n.user_id = a.id
ORDER BY n.created_at DESC
LIMIT 10;
```

---

## 📚 Дополнительные ресурсы

- [Настройка Gmail App Password](https://support.google.com/accounts/answer/185833)
- [Настройка Yandex App Password](https://yandex.ru/support/passport/authorization/app-passwords.html)
- [SMTP протокол](https://datatracker.ietf.org/doc/html/rfc5321)

---

## ❓ FAQ

### Можно ли использовать обычный пароль вместо App Password?

**Нет.** Большинство почтовых сервисов требуют App Password для внешних приложений.

### Сколько стоит отправка email?

Бесплатно для личных аккаунтов Gmail, Yandex, Mail.ru с лимитами:
- Gmail: 500 писем/день
- Yandex: 1000 писем/день
- Mail.ru: 100 писем/день

### Можно ли отправлять HTML письма?

**Да.** Система автоматически генерирует красивые HTML-письма с шаблонами.

### Как отключить уведомления?

Закомментируйте вызовы `notification_service` в API endpoints или установите `SMTP_USER=""` в `.env`.

### Работает ли отправка в режиме отладки?

**Да.** Уведомления работают независимо от режима `DEBUG`.

---

## 🎯 Примеры использования

### Пример 1: Отмена бронирования админом

```python
# POST /api/v1/bookings/1/cancel
# Автоматически создается уведомление
# Отправляется в 18:00 накануне даты бронирования
```

### Пример 2: Отключение рабочего места

```python
# PUT /api/v1/workspaces/5
# {
#   "is_active": false
# }
# Автоматически создаются уведомления всем пользователям
# с бронированиями этого места
```

### Пример 3: Массовая рассылка

```python
# POST /api/v1/notifications/schedule
{
  "user_ids": [1, 2, 3, 4, 5],
  "subject": "Офис закрывается на ремонт",
  "message": "Уважаемые коллеги! С 1 мая офис будет закрыт...",
  "scheduled_at": "2026-04-30T18:00:00"
}
```

---

## ✅ Чек-лист настройки

- [ ] Заполнен `.env` файл
- [ ] Включена двухфакторная аутентификация
- [ ] Создан App Password
- [ ] SMTP настройки проверены
- [ ] Сервер перезапущен
- [ ] Тестовое письмо отправлено
- [ ] Тестовое письмо получено
- [ ] `.env` добавлен в `.gitignore`

---

**Готово!** 🎉 Система уведомлений настроена и готова к работе!
