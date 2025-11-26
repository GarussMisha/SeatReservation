// API сервис для взаимодействия с backend
import axios from 'axios'

/**
 * СОДЕРЖАНИЕ
 *
 * - authAPI: Методы аутентификации (login, register), получение текущего пользователя,
 *            выход из системы, статистика аккаунтов, обновление аккаунта.
 * - accountsAPI: CRUD-операции с аккаунтами (getAccounts, getAccount, createAccount,
 *                updateAccount, deleteAccount), статистика.
 * - workspacesAPI: CRUD-операции с рабочими местами (getWorkspaces, getWorkspace и т.д.),
 *                  получение по помещению, статистика, массовое обновление.
 * - bookingsAPI: CRUD-операции с бронированиями, фильтры (по workspace, account, date),
 *                статистика, отмена бронирования.
 * - roomsAPI: CRUD-операции с помещениями, поиск, рабочие места помещения,
 *             статистика, массовое обновление.
 * - adminAPI: Административные методы для пользователей, venues/seats (workspaces),
 *             статистика.
 * - statusesAPI: Получение всех статусов.
 * - utilsAPI: Проверка соединения с API (/health).
 */
 
// Создаем экземпляр axios с базовой конфигурацией
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Добавляем перехватчик для автоматического добавления токена
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('seatreservation_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Добавляем перехватчик для обработки ошибок авторизации
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Не редиректим на /login при ошибке самого логина
      if (!error.config.url.includes('/login')) {
        localStorage.removeItem('seatreservation_token')
        localStorage.removeItem('seatreservation_user')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  // Вход в систему
  async login(credentials) {
    try {
      const loginData = {
        login: credentials.login || credentials.email,
        password: credentials.password
      }
      const response = await api.post('/api/v1/accounts/auth/login', loginData)
      return response.data
    } catch (error) {
      console.error('Ошибка входа:', error)
      throw error
    }
  },

  // Регистрация аккаунта (для создания нового пользователя)
  async register(accountData) {
    try {
      // Структура данных должна соответствовать AccountCreate схеме бэкенда
      const data = {
        login: accountData.login,
        password: accountData.password,
        first_name: accountData.first_name || '',
        last_name: accountData.last_name || '',
        middle_name: accountData.middle_name || '',
        email: accountData.email || '',
        phone: accountData.phone || '',
        is_admin: accountData.is_admin || false,
        status_id: accountData.status_id || 1
      }
      const response = await api.post('/api/v1/accounts/', data)
      return response.data
    } catch (error) {
      console.error('Ошибка регистрации:', error)
      throw error
    }
  },

  // Получение данных текущего пользователя
  async getCurrentUser() {
    try {
      const response = await api.get('/api/v1/accounts/me')
      return response.data
    } catch (error) {
      console.error('Ошибка получения данных пользователя:', error)
      throw error
    }
  },

  // Выход из системы (очистка токена)
  logout() {
    localStorage.removeItem('seatreservation_token')
    localStorage.removeItem('seatreservation_user')
  },

  // Получение статистики аккаунтов
  async getAccountsStats() {
    try {
      const response = await api.get('/api/v1/accounts/stats/overview')
      return response.data
    } catch (error) {
      console.error('Ошибка получения статистики аккаунтов:', error)
      throw error
    }
  },

  // Обновление аккаунта
  async updateAccount(accountId, accountData) {
    try {
      const response = await api.put(`/api/v1/accounts/${accountId}`, accountData)
      return response.data
    } catch (error) {
      console.error('Ошибка обновления аккаунта:', error)
      throw error
    }
  }
}

// Accounts API
export const accountsAPI = {
  // Получение всех аккаунтов
  async getAccounts(skip = 0, limit = 100) {
    try {
      const response = await api.get(`/api/v1/accounts/?skip=${skip}&limit=${limit}`)
      return response.data
    } catch (error) {
      console.error('Get accounts error:', error)
      throw error
    }
  },

  // Получение аккаунта по ID
  async getAccount(accountId) {
    try {
      const response = await api.get(`/api/v1/accounts/${accountId}`)
      return response.data
    } catch (error) {
      console.error('Get account error:', error)
      throw error
    }
  },

  // Создание аккаунта
  async createAccount(accountData) {
    try {
      const response = await api.post('/api/v1/accounts/', accountData)
      return response.data
    } catch (error) {
      console.error('Create account error:', error)
      throw error
    }
  },

  // Обновление аккаунта
  async updateAccount(accountId, accountData) {
    try {
      const response = await api.put(`/api/v1/accounts/${accountId}`, accountData)
      return response.data
    } catch (error) {
      console.error('Update account error:', error)
      throw error
    }
  },

  // Удаление аккаунта
  async deleteAccount(accountId) {
    try {
      const response = await api.delete(`/api/v1/accounts/${accountId}`)
      return response.data
    } catch (error) {
      console.error('Delete account error:', error)
      throw error
    }
  },

  // Получение статистики аккаунтов
  async getAccountsStats() {
    try {
      const response = await api.get('/api/v1/accounts/stats/overview')
      return response.data
    } catch (error) {
      console.error('Get accounts stats error:', error)
      throw error
    }
  }
}

// Workspaces API
export const workspacesAPI = {
  // Получение всех рабочих мест
  async getWorkspaces(skip = 0, limit = 100) {
    try {
      const response = await api.get(`/api/v1/workspaces/?skip=${skip}&limit=${limit}`)
      return response.data
    } catch (error) {
      console.error('Get workspaces error:', error)
      throw error
    }
  },

  // Получение рабочего места по ID
  async getWorkspace(workspaceId) {
    try {
      const response = await api.get(`/api/v1/workspaces/${workspaceId}`)
      return response.data
    } catch (error) {
      console.error('Get workspace error:', error)
      throw error
    }
  },

  // Создание рабочего места
  async createWorkspace(workspaceData) {
    try {
      const response = await api.post('/api/v1/workspaces/', workspaceData)
      return response.data
    } catch (error) {
      console.error('Create workspace error:', error)
      throw error
    }
  },

  // Обновление рабочего места
  async updateWorkspace(workspaceId, workspaceData) {
    try {
      const response = await api.put(`/api/v1/workspaces/${workspaceId}`, workspaceData)
      return response.data
    } catch (error) {
      console.error('Update workspace error:', error)
      throw error
    }
  },

  // Удаление рабочего места
  async deleteWorkspace(workspaceId) {
    try {
      const response = await api.delete(`/api/v1/workspaces/${workspaceId}`)
      return response.data
    } catch (error) {
      console.error('Delete workspace error:', error)
      throw error
    }
  },

  // Получение рабочих мест помещения
  async getWorkspacesByRoom(roomId) {
    try {
      const response = await api.get(`/api/v1/workspaces/room/${roomId}`)
      return response.data
    } catch (error) {
      console.error('Get workspaces by room error:', error)
      throw error
    }
  },

  // Получение статистики рабочих мест
  async getWorkspacesStats() {
    try {
      const response = await api.get('/api/v1/workspaces/stats/overview')
      return response.data
    } catch (error) {
      console.error('Get workspaces stats error:', error)
      throw error
    }
  },

  // Массовое обновление рабочих мест
  async bulkUpdateWorkspaces(workspaceIds, updateData) {
    try {
      const response = await api.put('/api/v1/workspaces/bulk/update', {
        workspace_ids: workspaceIds,
        ...updateData
      })
      return response.data
    } catch (error) {
      console.error('Bulk update workspaces error:', error)
      throw error
    }
  }
}

// Bookings API
export const bookingsAPI = {
  // Получение всех бронирований
  async getBookings(skip = 0, limit = 100) {
    try {
      const response = await api.get(`/api/v1/bookings/?skip=${skip}&limit=${limit}`)
      return response.data
    } catch (error) {
      console.error('Get bookings error:', error)
      throw error
    }
  },

  // Получение бронирования по ID
  async getBooking(bookingId) {
    try {
      const response = await api.get(`/api/v1/bookings/${bookingId}`)
      return response.data
    } catch (error) {
      console.error('Get booking error:', error)
      throw error
    }
  },

  // Создание бронирования
  async createBooking(bookingData) {
    try {
      const response = await api.post('/api/v1/bookings/', bookingData)
      return response.data
    } catch (error) {
      console.error('Create booking error:', error)
      throw error
    }
  },

  // Обновление бронирования
  async updateBooking(bookingId, bookingData) {
    try {
      const response = await api.put(`/api/v1/bookings/${bookingId}`, bookingData)
      return response.data
    } catch (error) {
      console.error('Update booking error:', error)
      throw error
    }
  },

  // Удаление бронирования
  async deleteBooking(bookingId) {
    try {
      const response = await api.delete(`/api/v1/bookings/${bookingId}`)
      return response.data
    } catch (error) {
      console.error('Delete booking error:', error)
      throw error
    }
  },

  // Получение бронирований рабочего места
  async getBookingsByWorkspace(workspaceId, dateFrom = null, dateTo = null) {
    try {
      let url = `/api/v1/bookings/workspace/${workspaceId}`
      const params = new URLSearchParams()
      if (dateFrom) params.append('date_from', dateFrom)
      if (dateTo) params.append('date_to', dateTo)
      if (params.toString()) url += `?${params.toString()}`
      
      const response = await api.get(url)
      return response.data
    } catch (error) {
      console.error('Get bookings by workspace error:', error)
      throw error
    }
  },

  // Получение бронирований пользователя
  async getBookingsByAccount(accountId, includePast = false) {
    try {
      const response = await api.get(`/api/v1/bookings/account/${accountId}?include_past=${includePast}`)
      return response.data
    } catch (error) {
      console.error('Get bookings by account error:', error)
      throw error
    }
  },

  // Получение бронирований на дату
  async getBookingsByDate(bookingDate, excludeCancelled = true) {
    try {
      const response = await api.get(`/api/v1/bookings/date/${bookingDate}?exclude_cancelled=${excludeCancelled}`)
      return response.data
    } catch (error) {
      console.error('Get bookings by date error:', error)
      throw error
    }
  },

  // Получение статистики бронирований
  async getBookingsStats() {
    try {
      const response = await api.get('/api/v1/bookings/stats/overview')
      return response.data
    } catch (error) {
      console.error('Get bookings stats error:', error)
      throw error
    }
  },

  // Отмена бронирования
  async cancelBooking(bookingId) {
    try {
      const response = await api.post(`/api/v1/bookings/${bookingId}/cancel`)
      return response.data
    } catch (error) {
      console.error('Cancel booking error:', error)
      throw error
    }
  }
}

// Rooms API
export const roomsAPI = {
  // Получение всех помещений
  async getRooms(skip = 0, limit = 100) {
    try {
      const response = await api.get(`/api/v1/rooms/?skip=${skip}&limit=${limit}`)
      return response.data
    } catch (error) {
      console.error('Get rooms error:', error)
      throw error
    }
  },

  // Получение помещения по ID
  async getRoom(roomId) {
    try {
      const response = await api.get(`/api/v1/rooms/${roomId}`)
      return response.data
    } catch (error) {
      console.error('Get room error:', error)
      throw error
    }
  },

  // Создание помещения
  async createRoom(roomData) {
    try {
      const response = await api.post('/api/v1/rooms/', roomData)
      return response.data
    } catch (error) {
      console.error('Create room error:', error)
      throw error
    }
  },

  // Обновление помещения
  async updateRoom(roomId, roomData) {
    try {
      const response = await api.put(`/api/v1/rooms/${roomId}`, roomData)
      return response.data
    } catch (error) {
      console.error('Update room error:', error)
      throw error
    }
  },

  // Удаление помещения
  async deleteRoom(roomId) {
    try {
      const response = await api.delete(`/api/v1/rooms/${roomId}`)
      return response.data
    } catch (error) {
      console.error('Delete room error:', error)
      throw error
    }
  },

  // Поиск помещений
  async searchRooms(searchParams = {}) {
    try {
      const params = new URLSearchParams()
      Object.keys(searchParams).forEach(key => {
        if (searchParams[key] !== null && searchParams[key] !== undefined) {
          params.append(key, searchParams[key])
        }
      })
      
      const response = await api.get(`/api/v1/rooms/search/?${params.toString()}`)
      return response.data
    } catch (error) {
      console.error('Search rooms error:', error)
      throw error
    }
  },

  // Получение рабочих мест помещения
  async getRoomWorkspaces(roomId) {
    try {
      const response = await api.get(`/api/v1/rooms/${roomId}/workspaces`)
      return response.data
    } catch (error) {
      console.error('Get room workspaces error:', error)
      throw error
    }
  },

  // Получение статистики помещений
  async getRoomsStats() {
    try {
      const response = await api.get('/api/v1/rooms/stats/overview')
      return response.data
    } catch (error) {
      console.error('Get rooms stats error:', error)
      throw error
    }
  },

  // Массовое обновление помещений
  async bulkUpdateRooms(roomIds, updateData) {
    try {
      const response = await api.put('/api/v1/rooms/bulk/update', {
        room_ids: roomIds,
        ...updateData
      })
      return response.data
    } catch (error) {
      console.error('Bulk update rooms error:', error)
      throw error
    }
  },
}

// Admin API
export const adminAPI = {
  // Пользователи/Аккаунты
  // Получение списка пользователей (админ)
  async getUsers() {
    try {
      const response = await api.get('/api/v1/accounts/')
      return response.data
    } catch (error) {
      console.error('Get admin users error:', error)
      throw error
    }
  },

  // Удаление пользователя по ID (админ)
  async deleteUser(userId) {
    try {
      const response = await api.delete(`/api/v1/accounts/${userId}`)
      return response.data
    } catch (error) {
      console.error('Delete user error:', error)
      throw error
    }
  },

  // Рабочие места (venues)
  // Получение списка venues (рабочих мест, админ)
  async getVenues() {
    try {
      const response = await api.get('/api/v1/workspaces/')
      return response.data
    } catch (error) {
      console.error('Get admin venues error:', error)
      throw error
    }
  },

  // Создание venue (рабочего места, админ)
  async createVenue(venueData) {
    try {
      const response = await api.post('/api/v1/workspaces/', venueData)
      return response.data
    } catch (error) {
      console.error('Create venue error:', error)
      throw error
    }
  },

  // Обновление venue (рабочего места) по ID (админ)
  async updateVenue(venueId, venueData) {
    try {
      const response = await api.put(`/api/v1/workspaces/${venueId}`, venueData)
      return response.data
    } catch (error) {
      console.error('Update venue error:', error)
      throw error
    }
  },

  // Удаление venue (рабочего места) по ID (админ)
  async deleteVenue(venueId) {
    try {
      const response = await api.delete(`/api/v1/workspaces/${venueId}`)
      return response.data
    } catch (error) {
      console.error('Delete venue error:', error)
      throw error
    }
  },

  // Места (workspaces)
  // Получение списка seats (мест/workspaces, админ)
  async getSeats() {
    try {
      const response = await api.get('/api/v1/workspaces/')
      return response.data
    } catch (error) {
      console.error('Get admin seats error:', error)
      throw error
    }
  },

  // Создание seat (места/workspace, админ)
  async createSeat(seatData) {
    try {
      const response = await api.post('/api/v1/workspaces/', seatData)
      return response.data
    } catch (error) {
      console.error('Create seat error:', error)
      throw error
    }
  },

  // Обновление seat (места/workspace) по ID (админ)
  async updateSeat(seatId, seatData) {
    try {
      const response = await api.put(`/api/v1/workspaces/${seatId}`, seatData)
      return response.data
    } catch (error) {
      console.error('Update seat error:', error)
      throw error
    }
  },

  // Удаление seat (места/workspace) по ID (админ)
  async deleteSeat(seatId) {
    try {
      const response = await api.delete(`/api/v1/workspaces/${seatId}`)
      return response.data
    } catch (error) {
      console.error('Delete seat error:', error)
      throw error
    }
  },

  // Статистика
  // Получение общей статистики (аккаунты, workspaces, bookings)
  async getStats() {
    try {
      const [accountsStats, workspacesStats, bookingsStats] = await Promise.all([
        api.get('/api/v1/accounts/stats/overview'),
        api.get('/api/v1/workspaces/stats/overview'),
        api.get('/api/v1/bookings/stats/overview')
      ])
      
      return {
        accounts: accountsStats.data,
        workspaces: workspacesStats.data,
        bookings: bookingsStats.data
      }
    } catch (error) {
      console.error('Get admin stats error:', error)
      throw error
    }
  }
}

// Statuses API
export const statusesAPI = {
  // Получение всех статусов
  async getStatuses() {
    try {
      const response = await api.get('/api/v1/statuses/')
      return response.data
    } catch (error) {
      console.error('Get statuses error:', error)
      throw error
    }
  },
}

// Utils API
export const utilsAPI = {
  // Проверка состояния подключения к API
  async checkConnection() {
    try {
      const response = await api.get('/health')
      return response.data
    } catch (error) {
      console.error('API connection check failed:', error)
      throw error
    }
  }
}

export default api