import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { notificationsAPI } from '../services/api'

/**
 * Store для работы с серверными уведомлениями
 * Отличается от notificationStore тем, что работает с уведомлениями из БД
 * а не с локальными toast-уведомлениями
 */
export const useServerNotificationStore = defineStore('serverNotifications', () => {
  // Состояние
  const notifications = ref([])
  const totalNotifications = ref(0)
  const isLoading = ref(false)
  const error = ref(null)
  const unreadCount = ref(0)

  // Computed - вычисляемые свойства
  const hasUnreadNotifications = computed(() => unreadCount.value > 0)

  const groupedNotifications = computed(() => {
    const grouped = {
      pending: [],
      sent: [],
      failed: [],
      cancelled: []
    }

    notifications.value.forEach(notification => {
      const statusName = notification.status_name?.toLowerCase()
      if (grouped[statusName]) {
        grouped[statusName].push(notification)
      }
    })

    return grouped
  })

  // Методы

  /**
   * Получить мои уведомления
   */
  const fetchMyNotifications = async (limit = 50, skip = 0) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await notificationsAPI.getMyNotifications(limit, skip)
      notifications.value = response.notifications || []
      totalNotifications.value = response.total || 0

      // Подсчитываем непрочитанные (pending)
      unreadCount.value = notifications.value.filter(
        n => n.status_name === 'pending'
      ).length

      return response
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Ошибка загрузки уведомлений'
      console.error('Ошибка загрузки уведомлений:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Получить все уведомления (админ)
   */
  const fetchAllNotifications = async (params = {}) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await notificationsAPI.getAllNotifications(params)
      notifications.value = response.notifications || []
      totalNotifications.value = response.total || 0

      return response
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Ошибка загрузки уведомлений'
      console.error('Ошибка загрузки уведомлений:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Запланировать рассылку (админ)
   */
  const scheduleNotification = async (data) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await notificationsAPI.scheduleNotification(data)
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Ошибка планирования рассылки'
      console.error('Ошибка планирования рассылки:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Отменить уведомление (админ)
   */
  const cancelNotification = async (notificationId) => {
    error.value = null

    try {
      await notificationsAPI.cancelNotification(notificationId)
      // Удаляем из локального состояния
      const index = notifications.value.findIndex(n => n.id === notificationId)
      if (index !== -1) {
        notifications.value.splice(index, 1)
        totalNotifications.value--
      }
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Ошибка отмены уведомления'
      console.error('Ошибка отмены уведомления:', err)
      throw err
    }
  }

  /**
   * Повторно отправить уведомление (админ)
   */
  const resendNotification = async (notificationId) => {
    error.value = null

    try {
      const response = await notificationsAPI.resendNotification(notificationId)

      // Обновляем статус в локальном состоянии
      const index = notifications.value.findIndex(n => n.id === notificationId)
      if (index !== -1) {
        notifications.value[index].status_name = 'pending'
      }

      return response
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Ошибка повторной отправки'
      console.error('Ошибка повторной отправки:', err)
      throw err
    }
  }

  /**
   * Получить статистику уведомлений (админ)
   */
  const fetchStats = async () => {
    try {
      const response = await notificationsAPI.getNotificationsStats()
      return response
    } catch (err) {
      console.error('Ошибка получения статистики:', err)
      throw err
    }
  }

  /**
   * Отправить ожидающие уведомления (админ)
   */
  const sendPendingNotifications = async () => {
    try {
      const response = await notificationsAPI.sendPendingNotifications()
      // После отправки обновляем список
      await fetchMyNotifications()
      return response
    } catch (err) {
      console.error('Ошибка отправки уведомлений:', err)
      throw err
    }
  }

  /**
   * Очистить ошибки
   */
  const clearError = () => {
    error.value = null
  }

  /**
   * Очистить все уведомления
   */
  const clearNotifications = () => {
    notifications.value = []
    totalNotifications.value = 0
    unreadCount.value = 0
    error.value = null
  }

  /**
   * Обновить счетчик непрочитанных
   */
  const updateUnreadCount = () => {
    unreadCount.value = notifications.value.filter(
      n => n.status_name === 'pending'
    ).length
  }

  return {
    // Состояние
    notifications,
    totalNotifications,
    isLoading,
    error,
    unreadCount,

    // Computed
    hasUnreadNotifications,
    groupedNotifications,

    // Методы
    fetchMyNotifications,
    fetchAllNotifications,
    scheduleNotification,
    cancelNotification,
    resendNotification,
    fetchStats,
    sendPendingNotifications,
    clearError,
    clearNotifications,
    updateUnreadCount
  }
})
