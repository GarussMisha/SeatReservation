# SeatReservetion_front

Frontend-приложение системы бронирования рабочих мест **SeatReservation**, построенное на **Vue 3** и **Vite**.

## 📋 Описание

Одностраничное веб-приложение (SPA) для управления бронированием рабочих мест. Предоставляет пользователям удобный интерфейс для:
- Просмотра доступных рабочих мест
- Бронирования мест на определенные даты
- Управления своими бронированиями
- Администрирования системы (для администраторов)

## 🛠️ Технологический стек

| Технология | Версия | Назначение |
|------------|--------|------------|
| **Vue.js** | ^3.5.22 | Основной фреймворк |
| **Vite** | ^7.1.11 | Сборщик и dev-сервер |
| **Vue Router** | ^4.6.3 | Маршрутизация между страницами |
| **Pinia** | ^3.0.3 | Хранилище состояний (state management) |
| **Axios** | ^1.13.1 | HTTP-клиент для API запросов |

## 📁 Структура проекта

```
src/
├── components/     # Переиспользуемые Vue-компоненты
├── views/          # Страницы приложения
│   ├── Login.vue       # Страница входа
│   ├── Dashboard.vue   # Главная панель
│   ├── Booking.vue     # Управление бронированиями
│   ├── Profile.vue     # Профиль пользователя
│   ├── AdminPanel.vue  # Панель администратора
│   └── NotFound.vue    # Страница 404
├── router/         # Конфигурация маршрутизации
├── stores/         # Pinia хранилища
│   ├── auth.js         # Аутентификация
│   ├── reservations.js # Бронирования
│   ├── notifications.js# Уведомления
│   └── counter.js      # Пример
├── services/       # API клиенты
│   └── api.js        # HTTP-клиент для backend
├── App.vue         # Корневой компонент
└── main.js         # Точка входа приложения
```

## 🚀 Быстрый старт

### Установка зависимостей

```sh
npm install
```

### Запуск dev-сервера

```sh
npm run dev
```

Приложение будет доступно по адресу: **http://localhost:5173**

### Сборка для продакшена

```sh
npm run build
```

### Предпросмотр production-сборки

```sh
npm run preview
```

## 🔗 Интеграция с Backend

Приложение взаимодействует с backend API через Axios:

- **Backend API**: `http://localhost:8000/api/v1/`
- **Аутентификация**: JWT-токены (сохраняются в Pinia store)
- **CORS**: Настроен на стороне backend

### Основные эндпоинты

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/accounts/login` | Вход в систему |
| POST | `/accounts/register` | Регистрация |
| GET | `/workspaces` | Список рабочих мест |
| GET | `/bookings` | Список бронирований |
| POST | `/bookings` | Создать бронирование |

## 🏗️ Архитектура

```
┌─────────────────────────────────────┐
│         Vue.js Components           │
│  (Dashboard, Booking, Profile...)   │
├─────────────────────────────────────┤
│         Pinia Stores                │
│  (auth, reservations, notifications)│
├─────────────────────────────────────┤
│      Vue Router (навигация)         │
├─────────────────────────────────────┤
│       Services (api.js)             │
│         Axios HTTP Client           │
└─────────────────────────────────────┘
              ↓ HTTP/HTTPS
┌─────────────────────────────────────┐
│    Backend API (FastAPI, :8000)     │
└─────────────────────────────────────┘
```

## 🔐 Аутентификация

1. Пользователь вводит credentials на странице `/login`
2. Backend возвращает JWT-токен
3. Токен сохраняется в Pinia store (`auth.js`)
4. Все последующие запросы содержат `Authorization: Bearer {token}`

## 📦 Рекомендуемые расширения VS Code

- **[Vue (Official)](https://marketplace.visualstudio.com/items?itemName=Vue.volar)** — официальное расширение для Vue 3 (отключите Vetur)
- **[Vue.js devtools](https://chromewebstore.google.com/detail/vuejs-devtools/nhdogjmejiglipccpnnnanhbledajbpd)** — DevTools для браузера

## 🔗 Полезные ссылки

- [Vue.js Docs](https://vuejs.org/)
- [Vite Docs](https://vite.dev/)
- [Vue Router Docs](https://router.vuejs.org/)
- [Pinia Docs](https://pinia.vuejs.org/)
- [Axios Docs](https://axios-http.com/)

## 📝 Зависимости

### Основные

```json
{
  "vue": "^3.5.22",
  "vue-router": "^4.6.3",
  "pinia": "^3.0.3",
  "axios": "^1.13.1"
}
```

### Dev-зависимости

```json
{
  "@vitejs/plugin-vue": "^6.0.1",
  "vite": "^7.1.11",
  "vite-plugin-vue-devtools": "^8.0.3"
}
```

## 🖥️ Требования к Node.js

- **Node.js**: ^20.19.0 || >=22.12.0
- **npm**: последний стабильный

---

**Версия проекта**: 1.0.0
**Связанный проект**: [Backend API](../SeatReservetion_back/README.md)
