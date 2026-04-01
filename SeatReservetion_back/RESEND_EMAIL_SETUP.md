# 📬 Настройка Resend для отправки уведомлений

## 📋 Обзор

Интеграция с **Resend** — современным email-сервисом для разработчиков. Resend предоставляет SMTP-сервер для отправки транзакционных писем.

---

## ✅ Что уже настроено

### 1. **Обновлены файлы конфигурации**

#### `.env` (Backend)
```env
SMTP_HOST=smtp.resend.com
SMTP_PORT=465
SMTP_USER=resend
SMTP_PASSWORD=re_6mBXRPmz_4BsoQoXXSnupL8ysdpm69GyK
SMTP_FROM_EMAIL=onboarding@resend.dev
SMTP_FROM_NAME=Seat Reservation System
SMTP_USE_TLS=True
```

#### `app/core/config.py`
- Обновлены значения по умолчанию для Resend
- Порт изменён на 465 (SSL)
- SMTP_USER установлен в "resend"

#### `app/services/email_service.py`
- Исправлен порядок подключения: теперь используется `SMTP_SSL` для порта 465
- Поддержка как SSL (465), так и TLS (587)

---

## 🔑 Получение API ключа Resend

### Шаг 1: Регистрация
1. Перейдите на [resend.com](https://resend.com)
2. Зарегистрируйтесь через GitHub или email
3. Подтвердите email

### Шаг 2: Создание домена (опционально, для продакшена)

**Для разработки** можно использовать тестовый домен `onboarding@resend.dev`

**Для продакшена:**
1. В личном кабинете перейдите в **Domains**
2. Нажмите **Add Domain**
3. Введите ваш домен (например, `seatreservation.com`)
4. Добавьте DNS записи:
   ```
   Type: MX
   Name: @
   Value: feedback-smtp.us-east-1.amazonses.com
   Priority: 10
   
   Type: TXT
   Name: @
   Value: v=spf1 include:resend.com ~all
   ```

### Шаг 3: Получение API ключа
1. Перейдите в **API Keys**
2. Нажмите **Create API Key**
3. Дайте имя (например, "Production")
4. Скопируйте ключ (начинается с `re_`)

---

## 🚀 Быстрая проверка

### Тестовый скрипт

Создайте файл `test_email.py` в корне backend:

```python
"""Тест отправки email через Resend"""
import sys
sys.path.insert(0, '.')

from app.services.email_service import email_service

# Тестовые данные
to_email = "parussmikle@gmail.com"
subject = "🧪 Тестовое уведомление SeatReservation"
html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #2196f3; color: white; padding: 20px; text-align: center; }
        .content { background-color: #f9f9f9; padding: 20px; margin-top: 10px; }
        .success-box { background-color: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✅ Тестовое уведомление</h1>
        </div>
        <div class="content">
            <p>Здравствуйте!</p>
            
            <div class="success-box">
                <strong>Отлично!</strong> Система уведомлений работает корректно.
            </div>
            
            <p>Это тестовое письмо от системы бронирования рабочих мест SeatReservation.</p>
            
            <p>Если вы получили это письмо, значит SMTP-настройки настроены правильно.</p>
            
            <p>С уважением,<br>Команда Seat Reservation System</p>
        </div>
    </div>
</body>
</html>
"""

# Отправка
print("📬 Отправка тестового письма...")
result = email_service.send_email(
    to_email=to_email,
    subject=subject,
    html_content=html_content
)

if result["success"]:
    print("✅ Письмо успешно отправлено!")
    print(f"📅 Время отправки: {result['sent_at']}")
else:
    print(f"❌ Ошибка: {result['message']}")
```

### Запуск теста

```bash
cd SeatReservetion_back
venv\Scripts\activate
python test_email.py
```

---

## 📝 Типы уведомлений

Система автоматически отправляет уведомления при событиях:

### 1. **Отмена бронирования** (`booking_cancelled`)
- **Когда:** Админ отменяет бронирование
- **Получатель:** Пользователь, чьё бронирование отменено
- **Шаблон:** Красный дизайн с деталями бронирования

### 2. **Отключение рабочего места** (`workspace_disabled`)
- **Когда:** Админ отключает рабочее место (`is_active = false`)
- **Получатели:** Все пользователи с активными бронированиями на этом месте
- **Шаблон:** Оранжевый дизайн

### 3. **Отключение помещения** (`room_disabled`)
- **Когда:** Админ отключает помещение
- **Получатели:** Все пользователи с бронированиями в этом помещении
- **Шаблон:** Фиолетовый дизайн со списком затронутых бронирований

### 4. **Произвольная рассылка** (`custom`)
- **Когда:** Админ создаёт рассылку через API
- **Получатели:** Выбранные пользователи
- **Шаблон:** Синий дизайн с кастомным сообщением

---

## 🔧 Планировщик уведомлений

### Автоматическая отправка

**APScheduler** проверяет отложенные уведомления каждые **5 минут**:

```python
# app/services/scheduler_service.py
def start_notification_scheduler(check_interval_minutes: int = 5):
    scheduler_service.start(check_interval_minutes)
```

### Ручная отправка (Админ)

Через API:
```bash
POST /api/v1/notifications/send-pending
Authorization: Bearer <admin-token>
```

---

## 📊 Мониторинг

### Проверка статуса уведомлений

**API endpoint для админа:**
```bash
GET /api/v1/notifications/stats/overview
```

**Ответ:**
```json
{
  "total_notifications": 150,
  "pending_notifications": 5,
  "sent_notifications": 140,
  "failed_notifications": 3,
  "scheduled_notifications": 2,
  "notifications_by_type": {
    "booking_cancelled": 80,
    "workspace_disabled": 40,
    "custom": 30
  }
}
```

### Логирование

Логи отправленных писем:
```
INFO:app.services.email_service:Письмо отправлено на user@example.com с темой 'Отмена бронирования'
INFO:app.services.notification_service:Уведомление об отмене бронирования 123 отправлено пользователю 456
```

---

## ⚠️ Возможные проблемы и решения

### 1. **Ошибка аутентификации**
```
SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted')
```

**Решение:**
- Проверьте API ключ в `.env` (должен начинаться с `re_`)
- Убедитесь, что `SMTP_USER=resend`
- Перезапустите сервер после изменений

### 2. **Ошибка подключения**
```
SMTPConnectError: (421, b'4.7.0 Try again later')
```

**Решение:**
- Проверьте интернет-соединение
- Resend может временно блокировать при частых запросах
- Используйте задержки между отправками

### 3. **Письма не приходят**
**Проверка:**
1. Проверьте спам-папку
2. Убедитесь, что email подтверждён в Resend
3. Проверьте логи приложения

### 4. **Отправка на Gmail не работает**
**Решение:**
- Для тестов используйте `onboarding@resend.dev` как отправителя
- Для продакшена добавьте и подтвердите домен в Resend

---

## 🔐 Безопасность

### Защита API ключа

**НЕ коммитьте `.env` в Git!**

```bash
# .gitignore
.env
*.pyc
__pycache__/
```

### Смена ключа в продакшене

1. Создайте новый ключ в Resend Dashboard
2. Обновите `.env` на сервере
3. Перезапустите приложение

---

## 📈 Тарифы Resend

| План | Лимит | Цена |
|------|-------|------|
| **Free** | 100 писем/день, 3000/мес | Бесплатно |
| **Pro** | 50,000 писем/мес | $20/мес |
| **Business** | 100,000+ писем/мес | от $100/мес |

**Для разработки:** Free плана достаточно (~100 писем/день)

---

## 🧪 Тестирование локально

### 1. Запуск сервера
```bash
cd SeatReservetion_back
python run_server.py
```

### 2. Создание тестового бронирования
1. Войдите как админ
2. Создайте бронирование
3. Отмените его

### 3. Проверка
- Проверьте email получателя
- Проверьте логи сервера
- Проверьте `/api/v1/notifications/my`

---

## 📚 Дополнительные ресурсы

- [Resend Documentation](https://resend.com/docs)
- [Resend SMTP Guide](https://resend.com/docs/send-with-smtp)
- [Resend Dashboard](https://app.resend.com)
- [Resend API Reference](https://resend.com/docs/api-reference)

---

## ✅ Чек-лист настройки

- [ ] Зарегистрироваться на resend.com
- [ ] Получить API ключ
- [ ] Обновить `.env` (SMTP_HOST, SMTP_PASSWORD)
- [ ] Обновить `app/core/config.py` (если нужно)
- [ ] Запустить тестовый скрипт
- [ ] Проверить получение письма
- [ ] Протестировать уведомления в приложении

---

**Настроено:** Апрель 2026  
**Версия:** Resend SMTP Integration  
**Статус:** ✅ Готово к использованию
