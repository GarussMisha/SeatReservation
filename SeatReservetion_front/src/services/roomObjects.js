// API сервис для работы с объектами помещения
import api from './api'

/**
 * Room Objects API
 * Методы для управления объектами на плане помещения
 */
export const roomObjectsAPI = {
  /**
   * Получить все объекты помещения
   */
  async getRoomObjects(roomId, skip = 0, limit = 100) {
    try {
      const response = await api.get(`/api/v1/rooms/${roomId}/objects?skip=${skip}&limit=${limit}`)
      return response.data
    } catch (error) {
      console.error('Ошибка получения объектов помещения:', error)
      throw error
    }
  },

  /**
   * Получить объект по ID
   */
  async getRoomObject(objectId) {
    try {
      const response = await api.get(`/api/v1/rooms/objects/${objectId}`)
      return response.data
    } catch (error) {
      console.error('Ошибка получения объекта:', error)
      throw error
    }
  },

  /**
   * Создать объект помещения
   */
  async createRoomObject(roomId, objectData) {
    try {
      const response = await api.post(`/api/v1/rooms/${roomId}/objects`, objectData)
      return response.data
    } catch (error) {
      console.error('Ошибка создания объекта:', error)
      throw error
    }
  },

  /**
   * Обновить объект помещения
   */
  async updateRoomObject(objectId, updateData) {
    try {
      const response = await api.put(`/api/v1/rooms/objects/${objectId}`, updateData)
      return response.data
    } catch (error) {
      console.error('Ошибка обновления объекта:', error)
      throw error
    }
  },

  /**
   * Удалить объект помещения
   */
  async deleteRoomObject(objectId) {
    try {
      await api.delete(`/api/v1/rooms/objects/${objectId}`)
    } catch (error) {
      console.error('Ошибка удаления объекта:', error)
      throw error
    }
  },

  /**
   * Создать стену
   */
  async createWall(wallData) {
    try {
      const response = await api.post('/api/v1/rooms/walls', wallData)
      return response.data
    } catch (error) {
      console.error('Ошибка создания стены:', error)
      throw error
    }
  },

  /**
   * Создать дверь
   */
  async createDoor(doorData) {
    try {
      const response = await api.post('/api/v1/rooms/doors', doorData)
      return response.data
    } catch (error) {
      console.error('Ошибка создания двери:', error)
      throw error
    }
  },

  /**
   * Создать окно
   */
  async createWindow(windowData) {
    try {
      const response = await api.post('/api/v1/rooms/windows', windowData)
      return response.data
    } catch (error) {
      console.error('Ошибка создания окна:', error)
      throw error
    }
  },

  /**
   * Создать рабочее место на плане
   */
  async createWorkspaceOnPlan(workspaceData) {
    try {
      const response = await api.post('/api/v1/rooms/workspaces-on-plan', workspaceData)
      return response.data
    } catch (error) {
      console.error('Ошибка создания рабочего места:', error)
      throw error
    }
  },

  /**
   * Обновить рабочее место на плане
   */
  async updateWorkspaceOnPlan(wpId, updateData) {
    try {
      const response = await api.put(`/api/v1/rooms/workspaces-on-plan/${wpId}`, updateData)
      return response.data
    } catch (error) {
      console.error('Ошибка обновления рабочего места:', error)
      throw error
    }
  },

  /**
   * Сохранить весь план помещения
   */
  async saveRoomPlan(roomId, objects, fieldWidth, fieldHeight) {
    try {
      const response = await api.post(`/api/v1/rooms/${roomId}/plan`, {
        objects,
        fieldWidth,
        fieldHeight
      })
      return response.data
    } catch (error) {
      console.error('Ошибка сохранения плана:', error)
      throw error
    }
  },

  /**
   * Получить весь план помещения
   */
  async getRoomPlan(roomId) {
    try {
      const response = await api.get(`/api/v1/rooms/${roomId}/plan`)
      return response.data
    } catch (error) {
      console.error('Ошибка получения плана:', error)
      throw error
    }
  },

  /**
   * Очистить весь план помещения (удалить все объекты)
   */
  async clearRoomPlan(roomId) {
    try {
      const response = await api.delete(`/api/v1/rooms/${roomId}/plan`)
      return response.data
    } catch (error) {
      console.error('Ошибка очистки плана:', error)
      throw error
    }
  },

  /**
   * Обновить название рабочего места
   */
  async updateWorkspaceName(roomId, workspaceOnPlanId, newName) {
    try {
      const response = await api.put(`/api/v1/rooms/${roomId}/workspaces-on-plan/${workspaceOnPlanId}/name`, {
        name: newName
      })
      return response.data
    } catch (error) {
      console.error('Ошибка обновления названия рабочего места:', error)
      throw error
    }
  },

  /**
   * Получить рабочие места с координатами
   */
  async getWorkspacesWithLocations(roomId, bookingDate = null) {
    try {
      const params = new URLSearchParams()
      if (bookingDate) {
        params.append('booking_date', bookingDate)
      }
      const url = `/api/v1/rooms/${roomId}/workspaces/with-locations${params.toString() ? '?' + params.toString() : ''}`
      const response = await api.get(url)
      return response.data
    } catch (error) {
      console.error('Ошибка получения рабочих мест с координатами:', error)
      throw error
    }
  }
}

export default roomObjectsAPI
