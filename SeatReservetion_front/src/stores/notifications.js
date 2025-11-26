import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useNotificationStore = defineStore('notifications', () => {
  const notifications = ref([])

  const addNotification = (notification) => {
    const id = Date.now() + Math.random()
    const newNotification = {
      id,
      type: notification.type || 'info',
      title: notification.title,
      message: notification.message,
      duration: notification.duration || 5000,
      autoRemove: notification.autoRemove !== false,
      timestamp: Date.now()
    }
    
    notifications.value.push(newNotification)
    
    // Автоматическое удаление если включено
    if (newNotification.autoRemove) {
      setTimeout(() => {
        removeNotification(id)
      }, newNotification.duration)
    }
    
    return id
  }

  const removeNotification = (id) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  const clearAllNotifications = () => {
    notifications.value = []
  }

  // Удобные методы для разных типов уведомлений
  const success = (message, title = 'Успешно', options = {}) => {
    return addNotification({
      type: 'success',
      title,
      message,
      ...options
    })
  }

  const error = (message, title = 'Ошибка', options = {}) => {
    return addNotification({
      type: 'error',
      title,
      message,
      autoRemove: options.autoRemove !== false,
      duration: options.duration || 8000,
      ...options
    })
  }

  const warning = (message, title = 'Предупреждение', options = {}) => {
    return addNotification({
      type: 'warning',
      title,
      message,
      ...options
    })
  }

  const info = (message, title = 'Информация', options = {}) => {
    return addNotification({
      type: 'info',
      title,
      message,
      ...options
    })
  }

  return {
    notifications,
    addNotification,
    removeNotification,
    clearAllNotifications,
    success,
    error,
    warning,
    info
  }
})