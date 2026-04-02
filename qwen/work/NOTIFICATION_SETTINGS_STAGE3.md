# ✅ Этап 3: Frontend для настроек уведомлений

## 📅 Дата: 1 апреля 2026

## 📊 Статус: ✅ ВЫПОЛНЕНО

---

## 1. Созданные файлы

### 1.1. Сервисы

**`src/services/notificationSettings.js`**

API сервис для работы с настройками уведомлений:

```javascript
notificationSettingsAPI.getMySettings()
notificationSettingsAPI.updateMySettings(data)
notificationSettingsAPI.getNotificationSettings()
notificationSettingsAPI.updateNotificationSettings(data)
notificationSettingsAPI.testNotificationSettings(testEmail)
```

### 1.2. Store

**`src/stores/notificationSettings.js`**

Pinia store для управления состоянием настроек:

```javascript
const settingsStore = useNotificationSettingsStore()

// Методы
await settingsStore.fetchMySettings()
await settingsStore.updateMySettings(data)
await settingsStore.fetchSmtpSettings()
await settingsStore.updateSmtpSettings(data)
await settingsStore.testSmtpSettings(testEmail)
```

### 1.3. Страница настроек пользователя

**`src/views/NotificationSettings.vue`**

Страница управления настройками уведомлений:
- Переключатель "Email уведомления"
- Переключатель "Уведомления на сайте"
- Кнопка сохранения
- Информационная карточка

### 1.4. Обновлённые файлы

| Файл | Изменения |
|------|-----------|
| `src/router/index.js` | Добавлен маршрут `/profile/notifications` |
| `src/services/api.js` | Добавлен экспорт `notificationSettingsAPI` |

---

## 2. Страница настроек

### 2.1. Расположение

```
http://localhost:5173/profile/notifications
```

### 2.2. Функционал

**Email уведомления:**
- Вкл/Выкл получение уведомлений на email
- Показывает email пользователя

**Уведомления на сайте:**
- Вкл/Выкл отображение уведомлений в браузере
- Колокольчик в шапке сайта

**Сохранение:**
- Кнопка "Сохранить изменения"
- Индикатор загрузки при сохранении
- Toast уведомления об успехе/ошибке

---

## 3. Примеры использования

### 3.1. Открыть страницу настроек

```javascript
// Переход на страницу
router.push('/profile/notifications')
```

### 3.2. Загрузка настроек

```javascript
const settingsStore = useNotificationSettingsStore()
await settingsStore.fetchMySettings()

// settingsStore.userSettings содержит:
{
  "user_id": 3,
  "email_enabled": true,
  "site_enabled": true
}
```

### 3.3. Обновление настроек

```javascript
const settingsStore = useNotificationSettingsStore()
await settingsStore.updateMySettings({
  email_enabled: false,
  site_enabled: true
})
```

---

## 4. Интеграция с Profile

**Рекомендуется добавить ссылку в Profile.vue:**

```vue
<router-link to="/profile/notifications" class="settings-link">
  <svg>...</svg>
  Настройки уведомлений
</router-link>
```

---

## 5. Проверка работы

### 5.1. Запуск dev-сервера

```bash
cd SeatReservetion_front
npm run dev
```

### 5.2. Проверка страницы

1. Войдите в систему
2. Перейдите на `/profile/notifications`
3. Измените настройки
4. Нажмите "Сохранить"
5. Проверьте Toast уведомление

### 5.3. Проверка API

```bash
# Получить настройки
curl http://localhost:8000/api/v1/my/settings \
  -H "Authorization: Bearer TOKEN"

# Обновить настройки
curl -X PUT http://localhost:8000/api/v1/my/settings \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email_enabled": false}'
```

---

## 6. Следующие шаги

### Этап 4: Админ-панель для SMTP (🟡 Средний приоритет)

**Файлы для создания:**
- `src/components/admin/SmtpSettings.vue` — компонент настроек SMTP
- Интеграция в `src/views/AdminPanel.vue`

**Функционал:**
- Форма настройки SMTP (host, port, user, password)
- Кнопка "Сохранить"
- Кнопка "Отправить тестовое письмо"
- Проверка настроек

---

## 7. Связанные документы

- [NOTIFICATION_SETTINGS_STAGE1.md](NOTIFICATION_SETTINGS_STAGE1.md) — Этап 1 (База данных)
- [NOTIFICATION_SETTINGS_STAGE2.md](NOTIFICATION_SETTINGS_STAGE2.md) — Этап 2 (Backend API)
- [NOTIFICATION_CODE_REVIEW_2026.md](NOTIFICATION_CODE_REVIEW_2026.md) — полное ревью

---

**Этап 3 завершён!** ✅

**Следующий шаг:** Админ-панель для настройки SMTP (Этап 4).
