import { defineStore } from 'pinia'
import { ref } from 'vue'
import { notificationSettingsAPI } from '../services/api'

/**
 * Store для управления настройками уведомлений
 */
export const useNotificationSettingsStore = defineStore('notificationSettings', () => {
  // Состояние
  const userSettings = ref(null)
  const smtpSettings = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  // Методы

  /**
   * Загрузить мои настройки уведомлений
   */
  const fetchMySettings = async () => {
    isLoading.value = true
    error.value = null

    try {
      const data = await notificationSettingsAPI.getMySettings()
      userSettings.value = data
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Ошибка загрузки настроек'
      console.error('Ошибка загрузки настроек уведомлений:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Обновить мои настройки уведомлений
   * @param {Object} data - Данные для обновления
   */
  const updateMySettings = async (data) => {
    isLoading.value = true
    error.value = null

    try {
      const result = await notificationSettingsAPI.updateMySettings(data)
      userSettings.value = result
      return result
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Ошибка обновления настроек'
      console.error('Ошибка обновления настроек уведомлений:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Загрузить настройки SMTP (админ)
   */
  const fetchSmtpSettings = async () => {
    isLoading.value = true
    error.value = null

    try {
      const data = await notificationSettingsAPI.getNotificationSettings()
      smtpSettings.value = data
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Ошибка загрузки настроек SMTP'
      console.error('Ошибка загрузки настроек SMTP:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Обновить настройки SMTP (админ)
   * @param {Object} data - Данные для обновления
   */
  const updateSmtpSettings = async (data) => {
    isLoading.value = true
    error.value = null

    try {
      const result = await notificationSettingsAPI.updateNotificationSettings(data)
      smtpSettings.value = result
      return result
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Ошибка обновления настроек SMTP'
      console.error('Ошибка обновления настроек SMTP:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Протестировать SMTP настройки (админ)
   * @param {string} testEmail - Email для тестового письма
   */
  const testSmtpSettings = async (testEmail) => {
    isLoading.value = true
    error.value = null

    try {
      const result = await notificationSettingsAPI.testNotificationSettings(testEmail)
      return result
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Ошибка тестирования SMTP'
      console.error('Ошибка тестирования SMTP:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Очистить ошибку
   */
  const clearError = () => {
    error.value = null
  }

  /**
   * Очистить настройки
   */
  const clearSettings = () => {
    userSettings.value = null
    smtpSettings.value = null
    error.value = null
  }

  return {
    // Состояние
    userSettings,
    smtpSettings,
    isLoading,
    error,

    // Методы
    fetchMySettings,
    updateMySettings,
    fetchSmtpSettings,
    updateSmtpSettings,
    testSmtpSettings,
    clearError,
    clearSettings
  }
})
