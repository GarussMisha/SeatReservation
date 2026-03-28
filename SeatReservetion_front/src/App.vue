<script setup>
import { RouterView, useRoute } from 'vue-router'
import NotificationToast from './components/NotificationToast.vue'
import Header from './components/Header.vue'
import { useAuthStore } from './stores/auth'
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import './styles/variables.css'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// Показываем Header только для авторизованных пользователей
// Исключение: страница редактора помещений (RoomEditor)
const showHeader = computed(() => {
  return authStore.isAuthenticated && route.name !== 'Login' && route.name !== 'RoomEditor'
})

// Настройки заголовка в зависимости от маршрута
const headerConfig = computed(() => {
  const isAdmin = authStore.user?.is_admin || false

  switch (route.name) {
    case 'Dashboard':
      return {
        title: 'Панель управления',
        showLogout: true,
        actions: []
      }
    case 'Booking':
      return {
        title: 'Бронирование рабочего места',
        showLogout: true,
        actions: [
          {
            key: 'back',
            text: '← Назад к дашборду',
            className: 'back-btn',
            onClick: () => router.push('/dashboard')
          },
          {
            key: 'toggle',
            text: 'Мои бронирования',
            className: 'toggle-btn',
            onClick: () => {
              // Это действие должно обрабатываться на странице Booking
              window.dispatchEvent(new CustomEvent('toggle-booking-mode'))
            }
          }
        ]
      }
    case 'Profile':
      return {
        title: 'Профиль пользователя',
        showLogout: true,
        actions: [
          {
            key: 'back',
            text: '← Назад к дашборду',
            className: 'back-btn',
            onClick: () => router.push('/dashboard')
          }
        ]
      }
    case 'AdminPanel':
      return {
        title: 'Административная панель',
        showLogout: true,
        actions: [
          {
            key: 'back',
            text: '← Назад к дашборду',
            className: 'back-btn',
            onClick: () => router.push('/dashboard')
          }
        ]
      }
    case 'Notifications':
      return {
        title: 'Мои уведомления',
        showLogout: true,
        actions: [
          {
            key: 'back',
            text: '← Назад к дашборду',
            className: 'back-btn',
            onClick: () => router.push('/dashboard')
          }
        ]
      }
    default:
      return {
        title: 'Система бронирования',
        showLogout: true,
        actions: []
      }
  }
})

// Обработчик выхода
const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div id="app">
    <Header
      v-if="showHeader"
      :title="headerConfig.title"
      :actions="headerConfig.actions"
      :show-logout="headerConfig.showLogout"
      @logout="handleLogout"
    />
    <RouterView />
    <NotificationToast />
  </div>
</template>

<style>
@import './styles/variables.css';

#app {
  font-family: var(--font-family);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--text-body);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
  -webkit-user-drag: none;
  user-drag: none;
  -khtml-user-drag: none;
  -webkit-touch-callout: none;
}

button,
.header-action-btn,
.nav-btn,
.filter-btn,
.today-btn,
.logout-btn,
.back-btn,
.toggle-btn,
.feature-action,
.cancel-btn,
.book-workspace-btn {
  -webkit-appearance: button;
  appearance: button;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
  font-family: var(--font-family);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  transition: var(--transition-base);
}

body {
  font-family: inherit;
  line-height: var(--line-height-normal);
}
</style>
