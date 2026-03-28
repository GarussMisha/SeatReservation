<template>
  <div class="notifications-dropdown" v-click-outside="closeDropdown">
    <!-- Кнопка-колокольчик -->
    <button class="notification-bell-btn" @click="toggleDropdown" :class="{ 'has-unread': hasUnread }">
      <svg class="bell-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
      </svg>
      <span v-if="unreadCount > 0" class="unread-badge">{{ unreadCount > 9 ? '9+' : unreadCount }}</span>
    </button>

    <!-- Выпадающий список -->
    <transition name="dropdown">
      <div v-if="isOpen" class="dropdown-content">
        <div class="dropdown-header">
          <h3>Уведомления</h3>
          <button v-if="notifications.length > 0" @click="markAllAsRead" class="mark-all-read">
            Прочитать все
          </button>
        </div>

        <div v-if="isLoading" class="dropdown-loading">
          <div class="loading-spinner"></div>
          <p>Загрузка...</p>
        </div>

        <div v-else-if="notifications.length === 0" class="dropdown-empty">
          <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
          </svg>
          <p>Нет уведомлений</p>
        </div>

        <div v-else class="dropdown-list">
          <div
            v-for="notification in notifications"
            :key="notification.id"
            :class="['notification-item', notification.status_name === 'pending' ? 'unread' : 'read']"
          >
            <div class="notification-icon" :class="getNotificationIconClass(notification.notification_type)">
              <svg v-if="notification.notification_type === 'booking_cancelled'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
              </svg>
              <svg v-else-if="notification.notification_type === 'workspace_disabled'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
              </svg>
              <svg v-else-if="notification.notification_type === 'room_disabled'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
              </svg>
            </div>
            <div class="notification-content">
              <div class="notification-title">{{ notification.subject }}</div>
              <div class="notification-time">{{ formatTime(notification.created_at) }}</div>
            </div>
          </div>
        </div>

        <div v-if="notifications.length > 0" class="dropdown-footer">
          <router-link to="/notifications" class="view-all-link">
            Все уведомления →
          </router-link>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useServerNotificationStore } from '../stores/serverNotifications'

const router = useRouter()
const route = useRoute()
const notificationStore = useServerNotificationStore()

const isOpen = ref(false)
const isLoading = ref(false)

const notifications = computed(() => notificationStore.notifications)
const unreadCount = computed(() => notificationStore.unreadCount)
const hasUnread = computed(() => notificationStore.hasUnreadNotifications)

// Закрываем dropdown при переходе на страницу уведомлений
watch(() => route.name, (newName) => {
  if (newName === 'Notifications') {
    isOpen.value = false
  }
})

// Директива для закрытия при клике вне
const vClickOutside = {
  beforeMount(el, binding) {
    el.clickOutsideEvent = (event) => {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value()
      }
    }
    document.addEventListener('click', el.clickOutsideEvent)
  },
  unmounted(el) {
    document.removeEventListener('click', el.clickOutsideEvent)
  }
}

const toggleDropdown = async () => {
  isOpen.value = !isOpen.value
  if (isOpen.value && notifications.value.length === 0) {
    await loadNotifications()
  }
}

const closeDropdown = () => {
  isOpen.value = false
}

const loadNotifications = async () => {
  isLoading.value = true
  try {
    await notificationStore.fetchMyNotifications(5, 0)
  } catch (error) {
    console.error('Ошибка загрузки уведомлений:', error)
  } finally {
    isLoading.value = false
  }
}

const markAllAsRead = () => {
  // В будущем можно добавить API метод для массового прочтения
  notificationStore.unreadCount = 0
}

const getNotificationIconClass = (type) => {
  const classes = {
    booking_cancelled: 'icon-cancelled',
    workspace_disabled: 'icon-warning',
    room_disabled: 'icon-warning',
    custom: 'icon-info'
  }
  return classes[type] || 'icon-default'
}

const formatTime = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date

  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return 'Только что'
  if (minutes < 60) return `${minutes} мин. назад`
  if (hours < 24) return `${hours} ч. назад`
  if (days < 7) return `${days} дн. назад`

  return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' })
}

// Загружаем уведомления при монтировании компонента
onMounted(() => {
  // Периодическая проверка новых уведомлений (каждые 30 секунд)
  const interval = setInterval(() => {
    if (!isOpen.value) {
      notificationStore.fetchMyNotifications(1, 0)
    }
  }, 30000)

  onUnmounted(() => {
    clearInterval(interval)
  })
})
</script>

<style scoped>
.notifications-dropdown {
  position: relative;
  display: inline-block;
}

.notification-bell-btn {
  position: relative;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  transition: all 0.2s;
  color: #ffffff;
  backdrop-filter: blur(10px);
}

.notification-bell-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  color: #ffffff;
  transform: scale(1.05);
}

.notification-bell-btn.has-unread {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.25);
  animation: bell-shake 0.5s ease-in-out;
}

.bell-icon {
  width: 1.5rem;
  height: 1.5rem;
}

.unread-badge {
  position: absolute;
  top: 0;
  right: 0;
  background: #ef4444;
  color: white;
  font-size: 0.7rem;
  font-weight: 600;
  min-width: 1.25rem;
  height: 1.25rem;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(239, 68, 68, 0.4);
}

.dropdown-content {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  width: 24rem;
  max-height: 28rem;
  background: white;
  border-radius: 1rem;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
  border: 1px solid #e5e7eb;
  overflow: hidden;
  z-index: 1000;
}

.dropdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.dropdown-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
}

.mark-all-read {
  background: none;
  border: none;
  color: #3b82f6;
  font-size: 0.875rem;
  cursor: pointer;
  padding: 0;
  transition: color 0.2s;
}

.mark-all-read:hover {
  color: #2563eb;
  text-decoration: underline;
}

.dropdown-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  color: #6b7280;
}

.loading-spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.dropdown-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  color: #9ca3af;
  text-align: center;
}

.empty-icon {
  width: 4rem;
  height: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.dropdown-empty p {
  margin: 0;
  font-size: 0.95rem;
}

.dropdown-list {
  max-height: 20rem;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #f3f4f6;
  cursor: pointer;
  transition: background 0.2s;
}

.notification-item:hover {
  background: #f9fafb;
}

.notification-item.unread {
  background: #eff6ff;
}

.notification-item.unread:hover {
  background: #dbeafe;
}

.notification-icon {
  flex-shrink: 0;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.notification-icon svg {
  width: 20px;
  height: 20px;
}

.notification-icon.icon-cancelled {
  background: #fee2e2;
}

.notification-icon.icon-warning {
  background: #fef3c7;
}

.notification-icon.icon-info {
  background: #dbeafe;
}

.notification-icon.icon-default {
  background: #f3f4f6;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-size: 0.9rem;
  font-weight: 500;
  color: #111827;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.notification-time {
  font-size: 0.75rem;
  color: #6b7280;
}

.dropdown-footer {
  padding: 0.75rem 1.25rem;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
  text-align: center;
}

.view-all-link {
  color: #3b82f6;
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  transition: color 0.2s;
}

.view-all-link:hover {
  color: #2563eb;
}

/* Dropdown transition */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Bell shake animation */
@keyframes bell-shake {
  0%, 100% { transform: rotate(0deg); }
  10%, 30%, 50%, 70%, 90% { transform: rotate(-10deg); }
  20%, 40%, 60%, 80% { transform: rotate(10deg); }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Scrollbar */
.dropdown-list::-webkit-scrollbar {
  width: 6px;
}

.dropdown-list::-webkit-scrollbar-track {
  background: #f3f4f6;
}

.dropdown-list::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

.dropdown-list::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>
