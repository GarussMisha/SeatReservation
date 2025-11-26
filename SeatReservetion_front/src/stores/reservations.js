import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { bookingsAPI } from '../services/api'

export const useReservationsStore = defineStore('reservations', () => {
  // Состояние
  const reservations = ref([])
  const currentReservation = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  // Computed
  const upcomingReservations = computed(() => {
    const now = new Date()
    return reservations.value
      .filter(r => new Date(r.end_time) > now)
      .sort((a, b) => new Date(a.start_time) - new Date(b.start_time))
  })

  const pastReservations = computed(() => {
    const now = new Date()
    return reservations.value
      .filter(r => new Date(r.end_time) <= now)
      .sort((a, b) => new Date(b.start_time) - new Date(a.start_time))
  })

  const totalReservations = computed(() => reservations.value.length)

  // Методы
  const fetchReservations = async () => {
    isLoading.value = true
    error.value = null

    try {
      const data = await bookingsAPI.getBookings()
      reservations.value = data
      return data
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Ошибка загрузки бронирований'
      error.value = errorMessage
      throw new Error(errorMessage)
    } finally {
      isLoading.value = false
    }
  }

  const createReservation = async (reservationData) => {
    isLoading.value = true
    error.value = null

    try {
      const newReservation = await bookingsAPI.createBooking(reservationData)
      reservations.value.push(newReservation)
      return newReservation
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Ошибка создания бронирования'
      error.value = errorMessage
      throw new Error(errorMessage)
    } finally {
      isLoading.value = false
    }
  }

  const cancelReservation = async (reservationId) => {
    isLoading.value = true
    error.value = null

    try {
      await bookingsAPI.cancelBooking(reservationId)
      // Обновляем статус бронирования в локальном состоянии
      const index = reservations.value.findIndex(r => r.id === reservationId)
      if (index !== -1) {
        reservations.value[index] = { ...reservations.value[index], status_name: 'cancelled', status_description: 'Отменено' }
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Ошибка отмены бронирования'
      error.value = errorMessage
      throw new Error(errorMessage)
    } finally {
      isLoading.value = false
    }
  }

  const updateReservation = async (reservationId, reservationData) => {
    isLoading.value = true
    error.value = null

    try {
      const updatedReservation = await bookingsAPI.updateBooking(reservationId, reservationData)
      const index = reservations.value.findIndex(r => r.id === reservationId)
      if (index !== -1) {
        reservations.value[index] = updatedReservation
      }
      return updatedReservation
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Ошибка обновления бронирования'
      error.value = errorMessage
      throw new Error(errorMessage)
    } finally {
      isLoading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  const clearReservations = () => {
    reservations.value = []
    currentReservation.value = null
    error.value = null
  }

  return {
    // Состояние
    reservations,
    currentReservation,
    isLoading,
    error,
    
    // Computed
    upcomingReservations,
    pastReservations,
    totalReservations,
    
    // Методы
    fetchReservations,
    createReservation,
    cancelReservation,
    updateReservation,
    clearError,
    clearReservations
  }
})