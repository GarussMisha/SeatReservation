<template>
  <div class="notifications-page">
    <!-- Фоновая декорация -->
    <div class="background-decoration">
      <div class="floating-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
        <div class="shape shape-4"></div>
      </div>
    </div>

    <div class="notifications-container">
      <!-- Заголовок -->
      <div class="page-header">
        <div class="header-content">
          <h1>
            <svg class="page-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
            </svg>
            Мои уведомления
          </h1>
          <p class="subtitle">История всех ваших уведомлений</p>
        </div>
        <div class="header-actions">
          <button @click="refreshNotifications" class="refresh-btn" :disabled="isLoading">
            <svg class="btn-icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
            Обновить
          </button>
          <button
            v-if="hasUnread"
            @click="markAllAsRead"
            class="mark-read-btn"
          >
            <svg class="btn-icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
            </svg>
            Прочитать все
          </button>
        </div>
      </div>

      <!-- Статистика -->
      <div v-if="!isLoading && notifications.length > 0" class="stats-cards">
        <div class="stat-card unread">
          <div class="stat-value">{{ unreadCount }}</div>
          <div class="stat-label">Непрочитанные</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ totalNotifications }}</div>
          <div class="stat-label">Всего</div>
        </div>
      </div>

      <!-- Основной контент -->
      <main class="notifications-content">
        <!-- Загрузка -->
        <div v-if="isLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Загрузка уведомлений...</p>
        </div>

        <!-- Пусто -->
        <div v-else-if="notifications.length === 0" class="empty-state">
          <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
          </svg>
          <h2>Нет уведомлений</h2>
          <p>У вас пока нет уведомлений</p>
        </div>

        <!-- Список уведомлений -->
        <div v-else class="notifications-list">
          <!-- Фильтры -->
          <div class="filters">
            <button
              v-for="filter in filters"
              :key="filter.value"
              @click="activeFilter = filter.value"
              :class="['filter-btn', { active: activeFilter === filter.value }]"
            >
              {{ filter.label }}
            </button>
          </div>

          <!-- Уведомления -->
          <div class="list">
            <div
              v-for="notification in filteredNotifications"
              :key="notification.id"
              :class="['notification-card', isNotificationUnread(notification) ? 'unread' : 'read']"
              @click="markAsRead(notification.id)"
            >
              <div class="notification-header">
                <div class="notification-icon" :class="getIconClass(notification.notification_type)">
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
                <div class="notification-meta">
                  <span class="notification-type">{{ getTypeName(notification.notification_type) }}</span>
                  <span class="notification-time">{{ formatTime(notification.created_at) }}</span>
                </div>
              </div>

              <div class="notification-body">
                <h3 class="notification-title">{{ notification.subject }}</h3>
                <div v-if="notification.message" class="notification-message">{{ getNotificationText(notification.message) }}</div>
              </div>

              <div class="notification-footer">
                <span :class="['status-badge', getStatusClass(notification.status_name)]">
                  {{ getStatusName(notification.status_name) }}
                </span>
              </div>
            </div>
          </div>

          <!-- Пагинация -->
          <div v-if="totalPages > 1" class="pagination">
            <button
              @click="currentPage--"
              :disabled="currentPage === 1"
              class="pagination-btn"
            >
              ← Назад
            </button>
            <span class="pagination-info">
              Страница {{ currentPage }} из {{ totalPages }}
            </span>
            <button
              @click="currentPage++"
              :disabled="currentPage === totalPages"
              class="pagination-btn"
            >
              Вперед →
            </button>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useServerNotificationStore } from '../stores/serverNotifications'
import { useNotificationStore } from '../stores/notifications'

const notificationStore = useServerNotificationStore()
const toastStore = useNotificationStore()

const isLoading = ref(false)
const currentPage = ref(1)
const activeFilter = ref('all')
const pageSize = 10

const filters = [
  { value: 'all', label: 'Все' },
  { value: 'unread', label: 'Непрочитанные' }
]

const notifications = computed(() => notificationStore.notifications)
const totalNotifications = computed(() => notificationStore.totalNotifications)
const unreadCount = computed(() => notificationStore.unreadCount)
const hasUnread = computed(() => notificationStore.hasUnreadNotifications)

const totalPages = computed(() => Math.ceil(totalNotifications.value / pageSize))

const filteredNotifications = computed(() => {
  let filtered = notifications.value

  // Фильтр "Непрочитанные" показывает уведомления в статусе pending, которые ещё не прочитаны
  if (activeFilter.value === 'unread') {
    filtered = filtered.filter(n => 
      n.status_name === 'pending' && !notificationStore.isRead(n.id)
    )
  }

  const start = (currentPage.value - 1) * pageSize
  const end = start + pageSize
  return filtered.slice(start, end)
})

const refreshNotifications = async () => {
  isLoading.value = true
  try {
    await notificationStore.fetchMyNotifications(50, 0)
  } catch (error) {
    toastStore.error('Не удалось обновить уведомления', 'Ошибка')
  } finally {
    isLoading.value = false
  }
}

const markAsRead = (notificationId) => {
  notificationStore.markAsRead(notificationId)
}

const isNotificationUnread = (notification) => {
  // Уведомление считается непрочитанным если:
  // 1. Оно в статусе pending
  // 2. Его ID нет в списке прочитанных
  return notification.status_name === 'pending' && !notificationStore.isRead(notification.id)
}

const markAllAsRead = () => {
  notificationStore.markAllAsRead()
  toastStore.success('Все уведомления отмечены как прочитанные')
}

const getIconClass = (type) => {
  const classes = {
    booking_cancelled: 'icon-cancelled',
    workspace_disabled: 'icon-warning',
    room_disabled: 'icon-warning',
    custom: 'icon-info'
  }
  return classes[type] || 'icon-default'
}

const getTypeName = (type) => {
  const names = {
    booking_cancelled: 'Отмена бронирования',
    workspace_disabled: 'Рабочее место',
    room_disabled: 'Помещение',
    custom: 'Сообщение'
  }
  return names[type] || type
}

const getStatusName = (statusName) => {
  const names = {
    pending: 'Ожидает',
    sent: 'Отправлено',
    failed: 'Ошибка',
    cancelled: 'Отменено'
  }
  return names[statusName] || statusName
}

const getStatusClass = (statusName) => {
  const classes = {
    pending: 'warning',
    sent: 'success',
    failed: 'danger',
    cancelled: 'secondary'
  }
  return classes[statusName] || 'default'
}

const formatTime = (dateString) => {
  if (!dateString) return 'Неизвестно'
  
  // Парсим дату (формат ISO без timezone: 2026-04-01T19:00:00.123456)
  // Это локальное время сервера, которое нужно отображать как есть
  const date = new Date(dateString)
  
  // Проверяем, валидна ли дата
  if (isNaN(date.getTime())) {
    console.error('Неверный формат даты:', dateString)
    return 'Неизвестно'
  }
  
  // Возвращаем точное время и дату (14:35, 1 апр. 2026)
  return date.toLocaleString('ru-RU', { 
    hour: '2-digit',
    minute: '2-digit',
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  
  // Проверяем, валидна ли дата
  if (isNaN(date.getTime())) {
    return ''
  }
  
  // Возвращаем дату с относительным временем
  const now = new Date()
  const diffMs = now - date
  const minutes = Math.floor(diffMs / 60000)
  const hours = Math.floor(diffMs / 3600000)
  const days = Math.floor(diffMs / 86400000)
  
  // Для свежих уведомлений показываем относительное время
  if (minutes < 1) return 'Только что'
  if (minutes < 60) return `${minutes} мин. назад`
  if (hours < 24) return `${hours} ч. назад`
  if (days < 7) return `${days} дн. назад`
  
  // Для старых уведомлений показываем полную дату
  return date.toLocaleDateString('ru-RU', { 
    day: 'numeric', 
    month: 'long',
    year: 'numeric'
  })
}

const truncateMessage = (message) => {
  if (!message) return ''
  // Удаляем HTML теги и обрезаем
  const text = message.replace(/<[^>]*>/g, '')
  if (text.length > 200) {
    return text.substring(0, 200) + '...'
  }
  return text
}

const getNotificationText = (message) => {
  if (!message) return ''

  try {
    // Пытаемся распарсить JSON (новый формат)
    const data = typeof message === 'string' ? JSON.parse(message) : message
    
    // Формируем текст из структурированных данных
    let text = `${data.title}\n\n`
    
    if (data.greeting) {
      text += `${data.greeting}\n`
    }
    
    if (data.message) {
      text += `${data.message}\n\n`
    }
    
    // Добавляем элементы
    if (data.items && data.items.length > 0) {
      data.items.forEach(item => {
        text += `${item.icon} ${item.label}: ${item.value}\n`
      })
      text += '\n'
    }
    
    if (data.footer) {
      text += `${data.footer}`
    }
    
    // Обрезаем до 300 символов
    if (text.length > 300) {
      return text.substring(0, 300) + '...'
    }

    return text
  } catch (e) {
    // Если не JSON, возвращаем как есть (старый формат)
    return message.length > 300 ? message.substring(0, 300) + '...' : message
  }
}

onMounted(async () => {
  await refreshNotifications()
})
</script>

<style scoped>
.notifications-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 8rem 20px 20px 20px;
  position: relative;
  overflow: hidden;
}

.background-decoration {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.floating-shapes .shape {
  position: absolute;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  animation: float 6s ease-in-out infinite;
}

.shape-1 {
  width: 80px;
  height: 80px;
  top: 20%;
  left: 10%;
}

.shape-2 {
  width: 120px;
  height: 120px;
  top: 60%;
  right: 10%;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
    opacity: 0.7;
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
    opacity: 0.3;
  }
}

.notifications-container {
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  background: rgba(255, 255, 255, 0.95);
  padding: 1.5rem 2rem;
  border-radius: 1rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.header-content h1 {
  margin: 0 0 0.5rem 0;
  font-size: var(--font-size-3xl);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.page-icon {
  width: 32px;
  height: 32px;
  color: var(--primary-start);
}

.btn-icon-sm {
  width: 18px;
  height: 18px;
  margin-right: 0.5rem;
  vertical-align: middle;
}

.subtitle {
  margin: 0;
  color: #6b7280;
  font-size: 1rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.refresh-btn,
.mark-read-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-btn {
  background: #f3f4f6;
  color: #374151;
}

.refresh-btn:hover:not(:disabled) {
  background: #e5e7eb;
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.mark-read-btn {
  background: #3b82f6;
  color: white;
}

.mark-read-btn:hover {
  background: #2563eb;
}

/* Статистика */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: rgba(255, 255, 255, 0.95);
  padding: 1.5rem;
  border-radius: 1rem;
  text-align: center;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #667eea;
}

.stat-card.unread .stat-value {
  color: #3b82f6;
}

.stat-card.pending .stat-value {
  color: #f59e0b;
}

.stat-card.sent .stat-value {
  color: #22c55e;
}

.stat-label {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #6b7280;
}

/* Контент */
.notifications-content {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 1rem;
  padding: 2rem;
  min-height: 500px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.loading-spinner {
  width: 3rem;
  height: 3rem;
  border: 3px solid #e5e7eb;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p,
.empty-state p {
  color: #6b7280;
  font-size: 1.1rem;
}

.empty-icon {
  width: 6rem;
  height: 6rem;
  color: #d1d5db;
  margin-bottom: 1rem;
}

.empty-state h2 {
  margin: 0 0 0.5rem 0;
  color: #374151;
}

/* Фильтры */
.filters {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #e5e7eb;
  background: white;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover {
  background: #f9fafb;
}

.filter-btn.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

/* Список уведомлений */
.list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.notification-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 1rem;
  padding: 1.5rem;
  transition: all 0.2s;
}

.notification-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.notification-card.unread {
  background: #eff6ff;
  border-color: #bfdbfe;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.notification-icon {
  width: 3rem;
  height: 3rem;
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

.notification-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
}

.notification-type {
  font-size: 0.85rem;
  font-weight: 500;
  color: #6b7280;
}

.notification-time {
  font-size: 0.8rem;
  color: #9ca3af;
}

.notification-body {
  margin-bottom: 1rem;
}

.notification-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  color: #1f2937;
}

.notification-message {
  color: #4b5563;
  font-size: 0.95rem;
  line-height: 1.6;
  white-space: pre-wrap;  /* Сохраняет переносы строк */
}

.notification-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-badge.warning {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.success {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.danger {
  background: #fee2e2;
  color: #991b1b;
}

.status-badge.secondary {
  background: #f3f4f6;
  color: #374151;
}

.notification-date {
  font-size: 0.85rem;
  color: #6b7280;
}

/* Пагинация */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.pagination-btn {
  padding: 0.5rem 1rem;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  background: #e5e7eb;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  font-size: 0.95rem;
  color: #6b7280;
  font-weight: 500;
}

/* Адаптивность */
@media (max-width: 768px) {
  .notifications-page {
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .header-actions {
    width: 100%;
    justify-content: stretch;
  }

  .refresh-btn,
  .mark-read-btn {
    flex: 1;
  }

  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .filters {
    overflow-x: auto;
    flex-wrap: nowrap;
  }

  .notification-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style>
