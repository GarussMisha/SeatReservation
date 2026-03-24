// API сервис для работы с уведомлениями
import api from './api'

/**
 * Notifications API
 * Методы для работы с системой уведомлений пользователей
 */
export const notificationsAPI = {
  /**
   * Получить мои уведомления (для текущего пользователя)
   * @param {number} limit - Количество записей (по умолчанию 50)
   * @param {number} skip - Пропуск записей (по умолчанию 0)
   * @returns {Promise}
   */
  async getMyNotifications(limit = 50, skip = 0) {
    try {
      const response = await api.get(`/api/v1/notifications/my?limit=${limit}&skip=${skip}`)
      return response.data
    } catch (error) {
      console.error('Ошибка получения уведомлений:', error)
      throw error
    }
  },

  /**
   * Получить все уведомления (только для администраторов)
   * @param {Object} params - Параметры фильтрации
   * @param {string} params.notification_type - Тип уведомления
   * @param {number} params.status_id - ID статуса
   * @param {number} params.user_id - ID пользователя
   * @param {number} params.limit - Лимит записей
   * @param {number} params.skip - Пропуск записей
   * @returns {Promise}
   */
  async getAllNotifications(params = {}) {
    try {
      const response = await api.get('/api/v1/notifications/', { params })
      return response.data
    } catch (error) {
      console.error('Ошибка получения всех уведомлений:', error)
      throw error
    }
  },

  /**
   * Получить уведомление по ID (только для администраторов)
   * @param {number} notificationId - ID уведомления
   * @returns {Promise}
   */
  async getNotification(notificationId) {
    try {
      const response = await api.get(`/api/v1/notifications/${notificationId}`)
      return response.data
    } catch (error) {
      console.error('Ошибка получения уведомления:', error)
      throw error
    }
  },

  /**
   * Запланировать рассылку уведомлений (только для администраторов)
   * @param {Object} data - Данные рассылки
   * @param {number[]} data.user_ids - Список ID пользователей
   * @param {string} data.subject - Тема сообщения
   * @param {string} data.message - Текст сообщения
   * @param {string} data.scheduled_at - Время отправки (ISO 8601)
   * @returns {Promise}
   */
  async scheduleNotification(data) {
    try {
      const response = await api.post('/api/v1/notifications/schedule', data)
      return response.data
    } catch (error) {
      console.error('Ошибка планирования рассылки:', error)
      throw error
    }
  },

  /**
   * Массовая отправка уведомлений (только для администраторов)
   * @param {Object} data - Данные рассылки
   * @param {number[]} data.user_ids - Список ID пользователей
   * @param {string} data.subject - Тема сообщения
   * @param {string} data.message - Текст сообщения
   * @param {boolean} data.send_now - Отправить немедленно
   * @param {string} data.scheduled_at - Время отправки (если не немедленно)
   * @returns {Promise}
   */
  async bulkSendNotification(data) {
    try {
      const response = await api.post('/api/v1/notifications/bulk-send', data)
      return response.data
    } catch (error) {
      console.error('Ошибка массовой отправки:', error)
      throw error
    }
  },

  /**
   * Отменить уведомление (только для администраторов)
   * @param {number} notificationId - ID уведомления
   * @returns {Promise}
   */
  async cancelNotification(notificationId) {
    try {
      const response = await api.delete(`/api/v1/notifications/${notificationId}`)
      return response.data
    } catch (error) {
      console.error('Ошибка отмены уведомления:', error)
      throw error
    }
  },

  /**
   * Повторная отправка уведомления (только для администраторов)
   * @param {number} notificationId - ID уведомления
   * @returns {Promise}
   */
  async resendNotification(notificationId) {
    try {
      const response = await api.post(`/api/v1/notifications/${notificationId}/resend`)
      return response.data
    } catch (error) {
      console.error('Ошибка повторной отправки:', error)
      throw error
    }
  },

  /**
   * Получить статистику уведомлений (только для администраторов)
   * @returns {Promise}
   */
  async getNotificationsStats() {
    try {
      const response = await api.get('/api/v1/notifications/stats/overview')
      return response.data
    } catch (error) {
      console.error('Ошибка получения статистики:', error)
      throw error
    }
  },

  /**
   * Отправить ожидающие уведомления (только для администраторов)
   * @returns {Promise}
   */
  async sendPendingNotifications() {
    try {
      const response = await api.post('/api/v1/notifications/send-pending')
      return response.data
    } catch (error) {
      console.error('Ошибка отправки ожидающих уведомлений:', error)
      throw error
    }
  }
}

export default notificationsAPI
