import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  // Состояние
  const user = ref(null)
  const token = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  // Computed - вычисляемые свойства для проверки аутентификации
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userName = computed(() => {
    if (!user.value) return ''
    const firstName = user.value.first_name || ''
    const lastName = user.value.last_name || ''
    const login = user.value.login || ''
    return `${firstName} ${lastName}`.trim() || login
  })
  const userEmail = computed(() => user.value?.email || '')
  const userRole = computed(() => user.value?.is_admin ? 'admin' : 'user')
  const isAdmin = computed(() => user.value?.is_admin || false)

  // Методы
  const login = async (email, password) => {
    isLoading.value = true
    error.value = null

    try {
      // Вызываем API с правильными полями (email -> login)
      const response = await authAPI.login({ login: email, password })
      
      // Сохраняем токен
      token.value = response.access_token
      localStorage.setItem('seatreservation_token', response.access_token)
      
      // Сохраняем данные пользователя из ответа API
      user.value = response.user
      localStorage.setItem('seatreservation_user', JSON.stringify(response.user))
      
      return { success: true, user: response.user, token: response.access_token }
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Ошибка авторизации'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const register = async (userData) => {
    isLoading.value = true
    error.value = null

    try {
      // Валидация данных для новой структуры API
      if (!userData.login || !userData.password || !userData.first_name) {
        throw new Error('Логин, пароль и имя обязательны для заполнения')
      }
      
      if (userData.password.length < 6) {
        throw new Error('Пароль должен содержать минимум 6 символов')
      }
      
      // Создаем аккаунт через API
      const newUser = await authAPI.register(userData)
      
      return { success: true, user: newUser }
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Ошибка регистрации'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const logout = () => {
    user.value = null
    token.value = null
    error.value = null
    
    // Удаляем из localStorage
    localStorage.removeItem('seatreservation_token')
    localStorage.removeItem('seatreservation_user')
  }

  const checkAuth = async () => {
    const storedToken = localStorage.getItem('seatreservation_token')
    
    if (!storedToken) {
      return false
    }
    
    try {
      token.value = storedToken
      // Проверяем токен, получая данные пользователя
      const userData = await authAPI.getCurrentUser()
      user.value = userData
      localStorage.setItem('seatreservation_user', JSON.stringify(userData))
      return true
    } catch (err) {
      // Токен недействителен, удаляем
      logout()
      return false
    }
  }

  const clearError = () => {
    error.value = null
  }

  const refreshUserData = async () => {
    if (!token.value) return false
    
    try {
      const userData = await authAPI.getCurrentUser()
      user.value = userData
      localStorage.setItem('seatreservation_user', JSON.stringify(userData))
      return true
    } catch (err) {
      console.error('Не удалось обновить данные пользователя:', err)
      // Если не удалось получить данные пользователя, вероятно токен недействителен
      logout()
      return false
    }
  }

  return {
    // Состояние
    user,
    token,
    isLoading,
    error,
    
    // Computed
    isAuthenticated,
    userName,
    userEmail,
    userRole,
    isAdmin,
    
    // Методы
    login,
    register,
    logout,
    checkAuth,
    clearError,
    refreshUserData
  }
})