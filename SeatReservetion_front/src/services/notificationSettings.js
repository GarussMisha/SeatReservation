// API сервис для работы с настройками уведомлений
import api from './api'

/**
 * Notification Settings API
 * Методы для управления настройками уведомлений
 */
export const notificationSettingsAPI = {
  /**
   * Получить мои настройки уведомлений
   * @returns {Promise}
   */
  async getMySettings() {
    try {
      const response = await api.get('/notification-settings/my/settings')
      return response.data
    } catch (error) {
      console.error('Ошибка получения настроек уведомлений:', error)
      throw error
    }
  },

  /**
   * Обновить мои настройки уведомлений
   * @param {Object} data - Данные для обновления
   * @param {boolean} data.email_enabled - Включены ли email уведомления
   * @param {boolean} data.site_enabled - Включены ли уведомления на сайте
   * @returns {Promise}
   */
  async updateMySettings(data) {
    try {
      const response = await api.put('/notification-settings/my/settings', data)
      return response.data
    } catch (error) {
      console.error('Ошибка обновления настроек уведомлений:', error)
      throw error
    }
  },

  /**
   * Получить глобальные настройки SMTP (админ)
   * @returns {Promise}
   */
  async getNotificationSettings() {
    try {
      const response = await api.get('/notification-settings/admin/notification-settings')
      return response.data
    } catch (error) {
      console.error('Ошибка получения настроек SMTP:', error)
      throw error
    }
  },

  /**
   * Обновить настройки SMTP (админ)
   * @param {Object} data - Данные для обновления
   * @returns {Promise}
   */
  async updateNotificationSettings(data) {
    try {
      const response = await api.put('/notification-settings/admin/notification-settings', data)
      return response.data
    } catch (error) {
      console.error('Ошибка обновления настроек SMTP:', error)
      throw error
    }
  },

  /**
   * Протестировать SMTP настройки (админ)
   * @param {string} testEmail - Email для тестового письма
   * @returns {Promise}
   */
  async testNotificationSettings(testEmail) {
    try {
      const response = await api.post('/notification-settings/admin/notification-settings/test', {
        test_email: testEmail
      })
      return response.data
    } catch (error) {
      console.error('Ошибка тестирования SMTP:', error)
      throw error
    }
  }
}

export default notificationSettingsAPI
