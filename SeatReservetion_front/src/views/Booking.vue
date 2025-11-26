<template>
  <div class="booking-page">
    <!-- Фоновая декорация -->
    <div class="background-decoration">
      <div class="floating-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
        <div class="shape shape-4"></div>
      </div>
    </div>

    <div class="booking-container">
      <!-- Локальный заголовок удален - используется глобальный Header -->

      <main class="booking-content">
        <!-- Раздел с бронированиями пользователя -->
        <div v-if="showMyBookings" class="my-bookings-section">
          <h2>Мои бронирования</h2>
          <div v-if="loadingMyBookings" class="loading">Загрузка ваших бронирований...</div>
          <div v-else-if="sortedMyBookings.length === 0" class="no-bookings">
            У вас пока нет бронирований
          </div>
          <div v-else class="bookings-list">
            <!-- Активные бронирования -->
            <div v-if="activeBookings.length > 0" class="booking-group">
              <h3 class="booking-group-title active-title">Активные бронирования</h3>
              <div
                v-for="booking in activeBookings"
                :key="booking.id"
                class="booking-item"
              >
                <div class="booking-info">
                  <h3>{{ booking.workspace_name }}</h3>
                  <p class="workspace-room">{{ booking.workspace_room_name }}</p>
                  <p class="workspace-address">{{ booking.workspace_room_address }}</p>
                  <div class="booking-date">
                    <strong>Дата:</strong> {{ formatDate(booking.booking_date) }}
                  </div>
                  <div class="booking-status" :class="getStatusClass(booking.status_name)">
                    <strong>Статус:</strong> {{ getStatusDisplayName(booking.status_name) }}
                  </div>
                </div>
                <div class="booking-actions" v-if="canCancelBooking(booking)">
                  <button @click="cancelBooking(booking.id)" class="cancel-btn" :disabled="cancelling === booking.id">
                    {{ cancelling === booking.id ? 'Отмена...' : 'Отменить бронирование' }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Прошедшие бронирования -->
            <div v-if="pastBookings.length > 0" class="booking-group">
              <h3 class="booking-group-title past-title">Прошедшие бронирования</h3>
              <div
                v-for="booking in pastBookings"
                :key="booking.id"
                class="booking-item"
              >
                <div class="booking-info">
                  <h3>{{ booking.workspace_name }}</h3>
                  <p class="workspace-room">{{ booking.workspace_room_name }}</p>
                  <p class="workspace-address">{{ booking.workspace_room_address }}</p>
                  <div class="booking-date">
                    <strong>Дата:</strong> {{ formatDate(booking.booking_date) }}
                  </div>
                  <div class="booking-status" :class="getStatusClass(booking.status_name)">
                    <strong>Статус:</strong> {{ getStatusDisplayName(booking.status_name) }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Отмененные бронирования -->
            <div v-if="cancelledBookings.length > 0" class="booking-group">
              <h3 class="booking-group-title cancelled-title">Отмененные бронирования</h3>
              <div
                v-for="booking in cancelledBookings"
                :key="booking.id"
                :class="['booking-item', 'cancelled']"
              >
                <div class="booking-info">
                  <h3>{{ booking.workspace_name }}</h3>
                  <p class="workspace-room">{{ booking.workspace_room_name }}</p>
                  <p class="workspace-address">{{ booking.workspace_room_address }}</p>
                  <div class="booking-date">
                    <strong>Дата:</strong> {{ formatDate(booking.booking_date) }}
                  </div>
                  <div class="booking-status" :class="getStatusClass(booking.status_name)">
                    <strong>Статус:</strong> {{ getStatusDisplayName(booking.status_name) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Раздел бронирования -->
        <div v-else class="booking-section">
          <!-- Шаг 1: Выбор помещения -->
          <div v-if="selectedDate && !selectedRoom" class="step-container">
            <div class="step-header">
              <div class="step-number active">1</div>
              <h2>
                Выберите помещение для {{ formatDateShort(selectedDate) }}
              </h2>
            </div>
            
            <div class="room-selection">
              <!-- Поиск -->
              <div class="search-section">
                <input
                  v-model="roomSearchInput"
                  type="text"
                  :placeholder="rooms.length > 0 ? 'Поиск по названию помещения...' : 'Нет доступных помещений'"
                  class="search-input"
                  @keyup.enter="selectRoomFromInput"
                  list="rooms-list"
                />
                <datalist id="rooms-list">
                  <option v-for="room in rooms" :key="room.id" :value="room.name" />
                </datalist>
              </div>
              
              <div v-if="loadingRooms" class="loading">Загрузка помещений...</div>
              <div v-else-if="filteredRooms.length === 0" class="no-rooms">
                {{ roomSearchInput ? 'Помещения не найдены' : 'Нет доступных помещений' }}
              </div>
              <div v-else class="rooms-grid">
                <div
                  v-for="room in filteredRooms"
                  :key="room.id"
                  @click="selectRoom(room)"
                  :class="['room-card', { 'selected': selectedRoom?.id === room.id }]"
                >
                  <div class="room-card-header">
                    <h3>{{ room.name }}</h3>
                    <div class="room-status" :class="getRoomStatusClass(room)">
                      {{ getRoomStatus(room) }}
                    </div>
                  </div>
                  <p class="room-address">{{ room.address }}</p>
                  <div class="room-stats">
                    <div class="room-stat">
                      <span class="stat-label">Мест:</span>
                      <span class="stat-value">{{ room.total_workspaces || 0 }}</span>
                    </div>
                    <div class="room-stat">
                      <span class="stat-label">Доступных:</span>
                      <span class="stat-value" :class="getAvailabilityClass(room)">{{ getAvailableWorkspacesCount(room) }}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Информация о бронированиях пользователя на выбранную дату -->
              <div v-if="myDateBookings.length > 0" class="my-date-bookings">
                <h3>Ваши бронирования на {{ formatDateShort(selectedDate) }}</h3>
                <div class="date-bookings-list">
                  <div
                    v-for="booking in sortedMyDateBookings"
                    :key="booking.id"
                    class="date-booking-item"
                  >
                    <div class="booking-field">
                      <span class="booking-label">Место:</span>
                      <span class="booking-value">{{ booking.workspace_name }}</span>
                    </div>
                    <div class="booking-field">
                      <span class="booking-label">Адрес:</span>
                      <span class="booking-value">{{ booking.workspace_room_name }}</span>
                    </div>
                    <div class="booking-time">
                      Время бронирования: {{ formatDateTime(booking.created_at) }}
                      <span v-if="booking.status_name === 'cancelled' && booking.updated_at">
                        <br>Время отмены: {{ formatDateTime(booking.updated_at) }}
                      </span>
                    </div>
                    <div class="booking-status-row">
                      <div class="booking-status" :class="getStatusClass(booking.status_name)">
                        {{ getStatusDisplayName(booking.status_name) }}
                      </div>
                      <button
                        v-if="canCancelBooking(booking)"
                        @click="cancelBooking(booking.id)"
                        class="cancel-booking-btn-small"
                        :disabled="cancelling === booking.id"
                      >
                        {{ cancelling === booking.id ? 'Отмена...' : 'Отменить' }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Шаг 2: Выбор рабочего места -->
          <div v-else-if="selectedDate && selectedRoom" class="step-container">
            <div class="step-header">
              <div class="step-number completed">1</div>
              <div class="step-separator"></div>
              <div class="step-number active">2</div>
              <h2>
                Выберите рабочее место в {{ selectedRoom.name }}
                <button @click="changeRoom" class="change-room-btn">Изменить помещение</button>
              </h2>
            </div>
            
            <div class="workspace-selection">
              <div v-if="loadingWorkspaces" class="loading">Загрузка рабочих мест...</div>
              <div v-else-if="workspacesForDate.length === 0" class="no-workspaces">
                В данном помещении нет рабочих мест
              </div>
              <div v-else class="workspaces-grid">
                <div
                  v-for="workspace in workspacesForDate"
                  :key="workspace.id"
                  :class="['workspace-card', workspace.status]"
                >
                  <div class="workspace-info">
                    <div class="workspace-place">
                      <span class="workspace-label">Место:</span>
                      <span class="workspace-name">{{ workspace.name }}</span>
                    </div>
                    
                    <div class="workspace-status-row">
                      <span class="workspace-label">Статус:</span>
                      <div class="workspace-status" :class="getWorkspaceStatusClass(workspace.status)">
                        {{ getWorkspaceStatusDisplay(workspace.status) }}
                      </div>
                    </div>
                  </div>
                  
                  <div v-if="workspace.currentBooking && workspace.status === 'booked'" class="workspace-booking-info">
                    <small>
                      Забронировано: {{ workspace.currentBooking.account_first_name }} {{ workspace.currentBooking.account_last_name }}
                    </small>
                  </div>
                  
                  <div class="workspace-actions">
                    <button
                      v-if="workspace.status === 'available'"
                      @click="bookWorkspace(workspace)"
                      class="book-workspace-btn"
                      :disabled="booking"
                    >
                      {{ booking ? 'Бронирование...' : 'Забронировать место' }}
                    </button>
                    
                    <button
                      v-else-if="workspace.currentBooking && canCancelWorkspaceBooking(workspace.currentBooking)"
                      @click="cancelWorkspaceBooking(workspace.currentBooking.id)"
                      class="cancel-workspace-booking-btn"
                      :disabled="cancelling === workspace.currentBooking.id"
                    >
                      {{ cancelling === workspace.currentBooking.id ? 'Отмена...' : 'Отменить бронирование' }}
                    </button>
                    
                    <div v-else-if="workspace.status === 'inactive'" class="inactive-workspace-label">
                      Недоступно для бронирования
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { workspacesAPI, bookingsAPI, roomsAPI } from '../services/api'
import { useReservationsStore } from '../stores/reservations'
import { useNotificationStore } from '../stores/notifications'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const reservationsStore = useReservationsStore()
const notificationStore = useNotificationStore()

// Состояние
const showMyBookings = ref(false)
const loadingMyBookings = ref(false)
const loadingRooms = ref(false)
const loadingWorkspaces = ref(false)
const booking = ref(false)
const cancelling = ref(null)

// Данные
const rooms = ref([])
const selectedRoom = ref(null)
const workspaces = ref([])
const workspacesForDate = ref([])
const selectedDate = ref(null)
const myBookings = ref([])

// Статистика по помещениям
const roomStats = ref({}) // { roomId: { total: number, booked: number, available: number } }
const dateBookings = ref([]) // бронирования на выбранную дату
const myDateBookings = ref([]) // бронирования пользователя на выбранную дату

// Поиск
const roomSearchInput = ref('')

// Инициализация
onMounted(async () => {
  await loadInitialData()
  
  // Восстанавливаем состояние из URL при первоначальной загрузке
  await restoreStateFromUrl(false) // false означает первоначальную загрузку
  
  // Добавляем обработчик для кнопки "назад" в браузере
  // Обработка навигации через кнопку "назад" в браузере
  const handleBrowserNavigation = async () => {
    // Небольшая задержка для корректной работы с историей браузера
    setTimeout(async () => {
      await nextTick()
      await restoreStateFromUrl(true) // true означает, что вызов из браузерной навигации
    }, 0)
  }
  window.addEventListener('popstate', handleBrowserNavigation)
  
  // Добавляем обработчик переключения режимов от глобального Header
  const handleToggleBookingMode = () => {
    showMyBookings.value = !showMyBookings.value
  }

  window.addEventListener('toggle-booking-mode', handleToggleBookingMode)

  // Очистка обработчика при размонтировании компонента
  onUnmounted(() => {
    window.removeEventListener('toggle-booking-mode', handleToggleBookingMode)
  })
})

// Наблюдатель за изменениями в URL (только для навигации внутри приложения)
let isInitialLoad = true
watch(() => route.query, async (newQuery, oldQuery) => {
  // Пропускаем первоначальную загрузку - состояние уже восстановлено
  if (isInitialLoad) {
    isInitialLoad = false
    return
  }
  
  // Восстанавливаем состояние только при изменениях внутри приложения
  await nextTick() // Ожидаем завершения DOM обновления
  await restoreStateFromUrl(true) // true означает, что вызов из наблюдателя
}, { deep: true })

// Восстановление состояния из URL
const restoreStateFromUrl = async (isFromWatcher = false) => {
  const { date, room } = route.query
  
  // Если даты нет в URL, устанавливаем текущую дату
  const newDate = date || getTodayDateString()
  const newRoomId = room ? parseInt(room) : null
  
  // Сравниваем с текущим состоянием
  const currentDate = selectedDate.value
  const currentRoomId = selectedRoom.value?.id || null
  
  if (newDate !== currentDate) {
    // Очищаем помещение при смене даты
    selectedRoom.value = null
    workspacesForDate.value = []
    
    if (newDate && isValidDate(newDate) && isAvailableDate(new Date(newDate))) {
      selectedDate.value = newDate
      // Загружаем статистику для выбранной даты
      await loadRoomStatsForDate(newDate)
      // Загружаем бронирования пользователя на выбранную дату
      await loadUserBookingsForDate(newDate)
      
      // Восстанавливаем помещение если оно есть в URL
      if (newRoomId) {
        const selectedRoomFromUrl = rooms.value.find(r => r.id === newRoomId)
        
        if (selectedRoomFromUrl) {
          selectedRoom.value = selectedRoomFromUrl
          if (getRoomStatusClass(selectedRoomFromUrl) === 'active') {
            await loadRoomWorkspaces()
          }
        }
      }
    } else {
      // Если дата невалидна, устанавливаем текущую дату
      const todayString = getTodayDateString()
      selectedDate.value = todayString
      await loadRoomStatsForDate(todayString)
      await loadUserBookingsForDate(todayString)
    }
  } else if (newRoomId !== currentRoomId) {
    // Дата не изменилась, но изменилось помещение
    if (newRoomId) {
      const selectedRoomFromUrl = rooms.value.find(r => r.id === newRoomId)
      
      if (selectedRoomFromUrl) {
        selectedRoom.value = selectedRoomFromUrl
        if (getRoomStatusClass(selectedRoomFromUrl) === 'active') {
          await loadRoomWorkspaces()
        }
      }
    } else {
      // Убираем помещение из URL, очищаем выбранное помещение
      selectedRoom.value = null
      workspacesForDate.value = []
    }
  }
  
  // Обновляем флаг после первой загрузки
  if (!isFromWatcher) {
    isInitialLoad = false
  }
}

// Загрузка начальных данных
const loadInitialData = async () => {
  try {
    await Promise.all([
      loadRooms(),
      loadMyBookings()
    ])
  } catch (error) {
    console.error('Ошибка загрузки данных:', error)
  }
}

// Загрузка помещений
const loadRooms = async () => {
  try {
    loadingRooms.value = true
    const roomsData = await roomsAPI.getRooms()
    rooms.value = roomsData
  } catch (error) {
    console.error('Ошибка загрузки помещений:', error)
  } finally {
    loadingRooms.value = false
  }
}

// Загрузка статистики по помещениям для выбранной даты
const loadRoomStatsForDate = async (date) => {
  try {
    const [roomsData, workspacesData, bookingsData] = await Promise.all([
      roomsAPI.getRooms(),
      workspacesAPI.getWorkspaces(),
      bookingsAPI.getBookingsByDate(date, true) // только активные бронирования
    ])
    
    // Обновляем кеш
    rooms.value = roomsData
    workspaces.value = workspacesData
    dateBookings.value = bookingsData
    
    // Подсчитываем статистику по помещениям
    const stats = {}
    
    roomsData.forEach(room => {
      const roomWorkspaces = workspacesData.filter(ws => ws.room_id === room.id)
      const totalWorkspaces = roomWorkspaces.length
      
      const bookedWorkspaces = roomWorkspaces.filter(ws =>
        bookingsData.some(booking => booking.workspace_id === ws.id)
      ).length
      
      stats[room.id] = {
        total: totalWorkspaces,
        booked: bookedWorkspaces,
        available: totalWorkspaces - bookedWorkspaces
      }
    })
    
    roomStats.value = stats
    
  } catch (error) {
    console.error('Ошибка загрузки статистики по помещениям:', error)
  }
}

// Загрузка рабочих мест помещения
const loadRoomWorkspaces = async () => {
  if (!selectedRoom.value) return
  
  try {
    loadingWorkspaces.value = true
    const workspacesData = await workspacesAPI.getWorkspaces()
    // Фильтруем рабочие места по выбранному помещению
    workspaces.value = workspacesData.filter(ws => ws.room_id === selectedRoom.value.id)
    updateWorkspacesForDate()
  } catch (error) {
    console.error('Ошибка загрузки рабочих мест:', error)
  } finally {
    loadingWorkspaces.value = false
  }
}

// Загрузка бронирований пользователя
const loadMyBookings = async () => {
  if (!authStore.user) return
  
  try {
    loadingMyBookings.value = true
    const bookingsData = await bookingsAPI.getBookingsByAccount(authStore.user.id, false)
    myBookings.value = bookingsData
  } catch (error) {
    console.error('Ошибка загрузки бронирований:', error)
  } finally {
    loadingMyBookings.value = false
  }
}

// Загрузка бронирований пользователя на выбранную дату
const loadUserBookingsForDate = async (date) => {
  if (!authStore.user || !date) return
  
  try {
    // Всегда загружаем свежие данные для актуальности
    const allMyBookings = await bookingsAPI.getBookingsByAccount(authStore.user.id, false)
    
    // Фильтруем бронирования по выбранной дате
    myDateBookings.value = allMyBookings.filter(booking => {
      const bookingDate = booking.booking_date
      return bookingDate === date
    })
    
    // Обновляем кеш общих бронирований
    myBookings.value = allMyBookings
    
  } catch (error) {
    console.error('Ошибка загрузки бронирований пользователя на дату:', error)
  }
}

// Проверка валидности даты
const isValidDate = (dateString) => {
  const date = new Date(dateString)
  return date instanceof Date && !isNaN(date)
}

// Проверка доступности даты (только будущие даты)
const isAvailableDate = (date) => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const checkDate = new Date(date)
  checkDate.setHours(0, 0, 0, 0)
  return checkDate >= today
}


// Выбор помещения
const selectRoom = async (room) => {
  selectedRoom.value = room
  if (getRoomStatusClass(room) === 'active') {
    await loadRoomWorkspaces()
  }
  
  // Обновляем URL без добавления в историю, так как переход уже произошел
  const query = {
    date: selectedDate.value,
    room: room.id
  }
  router.replace({ query })
}

// Обновление рабочих мест для выбранной даты
const updateWorkspacesForDate = async () => {
  if (!selectedDate.value || !selectedRoom.value || workspaces.value.length === 0) {
    workspacesForDate.value = []
    return
  }

  try {
    // Получаем только активные бронирования на выбранную дату (исключая отмененные)
    const dateBookings = await bookingsAPI.getBookingsByDate(selectedDate.value, true)
    
    // Фильтруем рабочие места по выбранному помещению перед обновлением статусов
    const currentRoomWorkspaces = workspaces.value.filter(ws => ws.room_id === selectedRoom.value.id)
    
    workspacesForDate.value = currentRoomWorkspaces.map(workspace => {
      const booking = dateBookings.find(b => b.workspace_id === workspace.id)
      
      // Определяем статус рабочего места
      let status = 'available'
      if (!workspace.is_active) {
        status = 'inactive' // Неактивное место имеет приоритет
      } else if (booking) {
        status = 'booked'
      }
      
      return {
        ...workspace,
        status: status,
        currentBooking: booking || null,
        isMyBooking: booking && authStore.user && booking.account_id === authStore.user.id
      }
    })
  } catch (error) {
    console.error('Ошибка обновления статусов рабочих мест:', error)
  }
}

// Бронирование рабочего места
const bookWorkspace = async (workspace) => {
  if (!selectedDate.value || !authStore.user) {
    return
  }

  try {
    booking.value = true
    
    const bookingData = {
      booking_date: selectedDate.value,
      account_id: authStore.user.id,
      workspace_id: workspace.id,
      status_id: 1
    }
    
    await bookingsAPI.createBooking(bookingData)
    
    notificationStore.success(
      `Отлично! Рабочее место "${workspace.name}" успешно забронировано на ${formatDate(selectedDate.value)}!`,
      'Бронирование подтверждено'
    )
    
    // Обновляем данные
    await updateWorkspacesForDate()
    await loadMyBookings()
    
    // Обновляем бронирования пользователя на выбранную дату
    if (selectedDate.value) {
      await loadUserBookingsForDate(selectedDate.value)
    }
    
    // Обновляем статистику по помещениям
    if (selectedDate.value) {
      await loadRoomStatsForDate(selectedDate.value)
    }
    
  } catch (error) {
    console.error('Ошибка бронирования:', error)
    const errorMessage = error.response?.data?.detail || error.message || 'Ошибка при бронировании рабочего места'
    notificationStore.error(errorMessage, 'Не удалось забронировать место')
  } finally {
    booking.value = false
  }
}

// Отмена бронирования
const cancelBooking = async (bookingId) => {
  try {
    cancelling.value = bookingId
    await reservationsStore.cancelReservation(bookingId)
    
    notificationStore.success('Бронирование успешно отменено!', 'Отмена бронирования')
    
    // Обновляем список бронирований
    await loadMyBookings()
    
    // Если это было на выбранную дату, обновляем статусы
    if (selectedDate.value) {
      await updateWorkspacesForDate()
      await loadRoomStatsForDate(selectedDate.value)
      await loadUserBookingsForDate(selectedDate.value)
    }
    
  } catch (error) {
    console.error('Ошибка отмены бронирования:', error)
    const errorMessage = error.response?.data?.detail || error.message || 'Ошибка при отмене бронирования'
    notificationStore.error(errorMessage, 'Ошибка отмены')
  } finally {
    cancelling.value = null
  }
}

// Проверка возможности отмены бронирования
const canCancelBooking = (booking) => {
  if (booking.status_name === 'cancelled') return false
  
  const bookingDate = new Date(booking.booking_date)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  return bookingDate >= today
}

// Проверка возможности отмены бронирования рабочего места в таблице
const canCancelWorkspaceBooking = (booking) => {
  // Проверяем, что бронирование принадлежит текущему пользователю
  if (!authStore.user || booking.account_id !== authStore.user.id) return false
  
  // Проверяем статус и дату
  return canCancelBooking(booking)
}

// Отмена бронирования рабочего места в таблице
const cancelWorkspaceBooking = async (bookingId) => {
  try {
    cancelling.value = bookingId
    await reservationsStore.cancelReservation(bookingId)
    
    notificationStore.success('Бронирование успешно отменено!', 'Отмена бронирования')
    
    // Обновляем данные
    await updateWorkspacesForDate()
    await loadMyBookings()
    
    // Обновляем бронирования пользователя на выбранную дату
    if (selectedDate.value) {
      await loadUserBookingsForDate(selectedDate.value)
    }
    
    // Обновляем статистику по помещениям
    if (selectedDate.value) {
      await loadRoomStatsForDate(selectedDate.value)
    }
    
  } catch (error) {
    console.error('Ошибка отмены бронирования:', error)
    const errorMessage = error.response?.data?.detail || error.message || 'Ошибка при отмене бронирования'
    notificationStore.error(errorMessage, 'Ошибка отмены')
  } finally {
    cancelling.value = null
  }
}

// Получение количества доступных рабочих мест в помещении
const getAvailableWorkspacesCount = (room) => {
  if (!selectedDate.value) {
    return room.total_workspaces || 0
  }
  
  // Если у нас есть статистика для выбранной даты
  const stats = roomStats.value[room.id]
  if (stats) {
    return stats.available
  }
  
  // Фолбэк к общему количеству если нет статистики
  return room.total_workspaces || 0
}

// Получение класса для отображения доступности
const getAvailabilityClass = (room) => {
  if (!selectedDate.value) {
    return 'available-count'
  }
  
  const stats = roomStats.value[room.id]
  if (!stats) {
    return 'available-count'
  }
  
  if (stats.available === 0) {
    return 'no-available-count' // нет мест
  } else if (stats.available <= 2) {
    return 'low-available-count' // мало мест
  } else {
    return 'available-count' // достаточно мест
  }
}

// Получение класса для статуса бронирования
const getStatusClass = (statusName) => {
  // Нормализуем статус к нижнему регистру
  const normalizedStatus = statusName ? statusName.toString().toLowerCase().trim() : ''
  
  switch (normalizedStatus) {
    case 'active':
    case 'confirmed':
      return 'active'
    case 'cancelled':
      return 'cancelled'
    case 'pending':
      return 'pending'
    default:
      return 'active'
  }
}

// Получение отображаемого имени статуса
const getStatusDisplayName = (statusName) => {
  // Нормализуем статус к нижнему регистру
  const normalizedStatus = statusName ? statusName.toString().toLowerCase().trim() : ''
  
  switch (normalizedStatus) {
    case 'active':
    case 'активен': return 'Активен'
    case 'confirmed':
    case 'подтверждено': return 'Подтверждено'
    case 'cancelled':
    case 'отменено': return 'Отменено'
    case 'pending':
    case 'ожидает подтверждения': return 'Ожидает подтверждения'
    default:
      // Если статус не распознан, возвращаем "Активен" как безопасное значение
      return 'Активен'
  }
}

// Получение класса для статуса рабочего места
const getWorkspaceStatusClass = (status) => {
  switch (status) {
    case 'available': return 'available'
    case 'booked': return 'booked'
    case 'inactive': return 'inactive'
    default: return 'unknown'
  }
}

// Получение отображаемого статуса рабочего места
const getWorkspaceStatusDisplay = (status) => {
  switch (status) {
    case 'available': return 'Доступно'
    case 'booked': return 'Забронировано'
    case 'inactive': return 'Неактивно'
    default: return status
  }
}

// Получение отображаемого статуса помещения
const getRoomStatus = (room) => {
  // Пробуем разные варианты получения статуса
  let statusName = null
  
  // Вариант 1: status_name из API
  if (room.status_name) {
    statusName = room.status_name.toLowerCase()
  }
  // Вариант 2: status_id = 1 означает активный (доступный)
  else if (room.status_id === 1) {
    statusName = 'available'
  }
  // Вариант 3: если есть поле is_active
  else if (room.is_active === true) {
    statusName = 'available'
  }
  
  switch (statusName) {
    case 'available': return 'Доступно'
    case 'unavailable': return 'Недоступно'
    case 'maintenance': return 'На обслуживании'
    case 'closed': return 'Закрыто'
    case 'active': return 'Доступно'
    default: return 'Неизвестно'
  }
}

// Получение класса для статуса помещения
const getRoomStatusClass = (room) => {
  // Пробуем разные варианты получения статуса
  let statusName = null
  
  // Вариант 1: status_name из API
  if (room.status_name) {
    statusName = room.status_name.toLowerCase()
  }
  // Вариант 2: status_id = 1 означает активный (доступный)
  else if (room.status_id === 1) {
    statusName = 'available'
  }
  // Вариант 3: если есть поле is_active
  else if (room.is_active === true) {
    statusName = 'available'
  }
  
  switch (statusName) {
    case 'available': return 'active'
    case 'unavailable': return 'inactive'
    case 'maintenance': return 'maintenance'
    case 'closed': return 'closed'
    case 'active': return 'active'
    default: return 'inactive'
  }
}

// Форматирование даты
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// Краткое форматирование даты
const formatDateShort = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long'
  })
}

// Форматирование даты и времени
const formatDateTime = (dateString) => {
  if (!dateString) return 'Неизвестно'
  const date = new Date(dateString)
  return date.toLocaleString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Фильтрация помещений по поисковому запросу
const filteredRooms = computed(() => {
  if (!roomSearchInput.value) {
    return rooms.value
  }
  return rooms.value.filter(room =>
    room.name?.toLowerCase().includes(roomSearchInput.value.toLowerCase())
  )
})

// Сортированные бронирования пользователя на выбранную дату
const sortedMyDateBookings = computed(() => {
  return [...myDateBookings.value].sort((a, b) => {
    // Приоритеты статусов: 1) active (confirmed, pending), 2) cancelled
    const isActiveA = a.status_name === 'confirmed' || a.status_name === 'pending'
    const isActiveB = b.status_name === 'confirmed' || b.status_name === 'pending'
    
    // Активные бронирования идут первыми
    if (isActiveA && !isActiveB) return -1
    if (!isActiveA && isActiveB) return 1
    
    // Внутри одной группы сортируем по времени создания (новые сверху)
    return new Date(b.created_at || b.updated_at) - new Date(a.created_at || a.updated_at)
  })
})

// Сортированные все бронирования пользователя
const sortedMyBookings = computed(() => {
  return [...myBookings.value].sort((a, b) => {
    // Получаем дату бронирования для определения прошедших
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const bookingDateA = new Date(a.booking_date)
    const bookingDateB = new Date(b.booking_date)
    
    // Определяем типы бронирований
    const isActiveA = (a.status_name === 'confirmed' || a.status_name === 'pending') && bookingDateA >= today
    const isActiveB = (b.status_name === 'confirmed' || b.status_name === 'pending') && bookingDateB >= today
    
    const isPastA = bookingDateA < today
    const isPastB = bookingDateB < today
    
    const isCancelledA = a.status_name === 'cancelled'
    const isCancelledB = b.status_name === 'cancelled'
    
    // Группировка: 1) активные, 2) прошедшие, 3) отмененные
    // Активные бронирования
    if (isActiveA && !isActiveB) return -1
    if (!isActiveA && isActiveB) return 1
    
    // Прошедшие бронирования (не отмененные)
    if (isPastA && !isPastB && !isCancelledA) return -1
    if (!isPastA && isPastB && !isCancelledB) return 1
    
    // Отмененные бронирования
    if (isCancelledA && !isCancelledB) return -1
    if (!isCancelledA && isCancelledB) return 1
    
    // Внутри одной группы сортируем по дате бронирования (новые сверху)
    const dateCompare = new Date(b.booking_date) - new Date(a.booking_date)
    if (dateCompare !== 0) return dateCompare
    
    // Если даты равны, сортируем по времени создания (новые сверху)
    return new Date(b.created_at || b.updated_at) - new Date(a.created_at || a.updated_at)
  })
})

// Фильтрация бронирований по группам
const activeBookings = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return sortedMyBookings.value.filter(booking => {
    const bookingDate = new Date(booking.booking_date)
    // Упрощенное условие - любой неотмененный статус на будущую дату
    return booking.status_name !== 'cancelled' && bookingDate >= today
  })
})

const pastBookings = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return sortedMyBookings.value.filter(booking => {
    const bookingDate = new Date(booking.booking_date)
    return bookingDate < today && booking.status_name !== 'cancelled'
  })
})

const cancelledBookings = computed(() => {
  return sortedMyBookings.value.filter(booking => booking.status_name === 'cancelled')
})

// Изменение помещения
const changeRoom = () => {
  selectedRoom.value = null
  workspacesForDate.value = []
  // Заменяем URL без добавления в историю (пользователь хочет изменить помещение, не возвращаться)
  router.replace({ query: { date: selectedDate.value } })
}

// Получение строки текущей даты в формате YYYY-MM-DD
const getTodayDateString = () => {
  const today = new Date()
  return today.toISOString().split('T')[0]
}

// Выбор помещения из ввода
const selectRoomFromInput = () => {
  if (!roomSearchInput.value.trim()) return
  
  const foundRoom = rooms.value.find(room =>
    room.name?.toLowerCase() === roomSearchInput.value.toLowerCase().trim()
  )
  
  if (foundRoom) {
    selectRoom(foundRoom)
    roomSearchInput.value = '' // Очищаем поле после выбора
  }
}
</script>

<style scoped>
/* Фоновые стили */
.booking-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.booking-page::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none;
}

.booking-page .floating-shapes {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none;
}

.booking-page .shape {
  position: absolute;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  animation: float 6s ease-in-out infinite;
}

.booking-page .shape-1 {
  width: 80px;
  height: 80px;
  top: 20%;
  left: 10%;
  animation-delay: 0s;
}

.booking-page .shape-2 {
  width: 120px;
  height: 120px;
  top: 60%;
  right: 10%;
  animation-delay: 2s;
}

.booking-page .shape-3 {
  width: 60px;
  height: 60px;
  bottom: 20%;
  left: 20%;
  animation-delay: 4s;
}

.booking-page .shape-4 {
  width: 100px;
  height: 100px;
  top: 30%;
  right: 30%;
  animation-delay: 1s;
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

.booking-container {
  min-height: 100vh;
  padding: 8rem 20px 20px 20px;
  position: relative;
  z-index: 10;
}

.booking-content {
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  z-index: 10;
}

.my-bookings-section {
  max-width: 1200px;
  margin: 0 auto;
}

.my-bookings-section h2 {
  color: white;
  margin: 0 0 1.5rem 0;
  font-size: 1.8rem;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.loading, .no-bookings {
  text-align: center;
  color: rgba(255, 255, 255, 0.9);
  padding: 2rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.bookings-list {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.booking-group {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.booking-group-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.3rem;
  font-weight: 600;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
}

.active-title {
  color: #10b981;
  border-bottom-color: rgba(16, 185, 129, 0.3);
}

.past-title {
  color: #6b7280;
  border-bottom-color: rgba(107, 114, 128, 0.3);
}

.cancelled-title {
  color: #ef4444;
  border-bottom-color: rgba(239, 68, 68, 0.3);
}

.booking-item {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.booking-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.booking-item.cancelled {
  opacity: 0.6;
  background-color: rgba(248, 249, 250, 0.8);
}

.booking-info h3 {
  margin: 0 0 0.5rem 0;
  color: #1f2937;
  font-size: 1.3rem;
  font-weight: 600;
}

.workspace-room, .workspace-address {
  color: #6b7280;
  margin: 0.25rem 0;
  font-size: 0.95rem;
}

.booking-date, .booking-status {
  margin: 0.5rem 0;
  color: #374151;
  font-weight: 500;
}

.booking-status.confirmed {
  color: #10b981;
  background: rgba(16, 185, 129, 0.1);
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  display: inline-block;
}

.booking-status.cancelled {
  color: #6b7280;
  background: rgba(107, 114, 128, 0.1);
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  display: inline-block;
}

.booking-status.pending {
  color: #f59e0b;
  background: rgba(245, 158, 11, 0.1);
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  display: inline-block;
}

.cancel-btn {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.cancel-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #f87171 0%, #ef4444 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(239, 68, 68, 0.4);
}

.cancel-btn:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

.booking-section {
  max-width: 1200px;
  margin: 0 auto;
}

/* Шаги бронирования */
.step-container {
  background: white;
  border-radius: 20px;
  padding: 2.5rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.step-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 2px solid rgba(229, 231, 235, 0.3);
}

.step-header h2 {
  margin: 0;
  color: #1f2937;
  font-size: 1.5rem;
  font-weight: 600;
  flex: 1;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(156, 163, 175, 0.3);
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1.1rem;
}

.step-number.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.step-number.completed {
  background: #10b981;
  color: white;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

.step-separator {
  width: 60px;
  height: 2px;
  background: rgba(156, 163, 175, 0.3);
}

.change-room-btn {
  padding: 0.5rem 1rem;
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.85rem;
  font-weight: 500;
}

.change-room-btn:hover {
  background: rgba(102, 126, 234, 0.2);
  transform: translateY(-1px);
}

.room-selection {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.my-date-bookings {
  background: rgba(59, 130, 246, 0.1);
  border: 2px solid rgba(59, 130, 246, 0.3);
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  backdrop-filter: blur(10px);
}

.my-date-bookings h3 {
  margin: 0 0 1rem 0;
  color: #1e40af;
  font-size: 1.1rem;
  font-weight: 600;
}

.date-bookings-list {
  max-height: 250px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.date-booking-item {
  max-height: 150px;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  padding: 1rem;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.booking-field {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.booking-label {
  color: #6b7280;
  font-size: 0.9rem;
  font-weight: 500;
  min-width: 50px;
}

.booking-value {
  color: #1f2937;
  font-size: 0.9rem;
  font-weight: 600;
  flex: 1;
}

.booking-status {
  padding: 0.25rem 0.75rem;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
  align-self: flex-start;
}

.booking-status-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  justify-content: space-between;
}

.booking-status.confirmed {
  background: rgba(16, 185, 129, 0.15);
  color: #059669;
  border: 1px solid rgba(16, 185, 129, 0.4);
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.1);
}

.booking-status.active {
  background: rgba(16, 185, 129, 0.15);
  color: #059669;
  border: 1px solid rgba(16, 185, 129, 0.4);
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.1);
}

.booking-status.cancelled {
  background: rgba(107, 114, 128, 0.15);
  color: #6b7280;
  border: 1px solid rgba(107, 114, 128, 0.4);
  box-shadow: 0 2px 4px rgba(107, 114, 128, 0.1);
}

.booking-status.pending {
  background: rgba(245, 158, 11, 0.15);
  color: #d97706;
  border: 1px solid rgba(245, 158, 11, 0.4);
  box-shadow: 0 2px 4px rgba(245, 158, 11, 0.1);
}

.cancel-booking-btn-small {
  padding: 0.25rem 0.75rem;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
  box-shadow: 0 2px 6px rgba(239, 68, 68, 0.3);
}

.cancel-booking-btn-small:hover:not(:disabled) {
  background: linear-gradient(135deg, #f87171 0%, #ef4444 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(239, 68, 68, 0.4);
}

.cancel-booking-btn-small:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
  transform: none;
}

.search-section {
  margin-bottom: 1rem;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid rgba(229, 231, 235, 0.8);
  border-radius: 10px;
  font-size: 0.9rem;
  background: rgba(249, 250, 251, 0.8);
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.05);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.loading, .no-rooms {
  text-align: center;
  color: #6b7280;
  padding: 2rem;
  background: rgba(249, 250, 251, 0.8);
  border-radius: 12px;
}

.rooms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.room-card {
  padding: 1.5rem;
  border: 2px solid rgba(229, 231, 235, 0.8);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
}

.room-card:hover {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.05);
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(102, 126, 234, 0.2);
}

.room-card.selected {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.1);
  box-shadow: 0 12px 30px rgba(102, 126, 234, 0.3);
}

.room-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.room-card-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.2rem;
  font-weight: 600;
  flex: 1;
}

.room-status {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  backdrop-filter: blur(10px);
}

.room-status.active {
  background: rgba(16, 185, 129, 0.2);
  color: #065f46;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.room-status.inactive {
  background: rgba(239, 68, 68, 0.2);
  color: #991b1b;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.room-address {
  color: #6b7280;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.room-stats {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.room-stat {
  display: flex;
  flex-direction: column;
  text-align: center;
}

.stat-label {
  font-size: 0.8rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1f2937;
}

.stat-value.available-count {
  color: #10b981;
}

.stat-value.no-available-count {
  color: #ef4444;
}

.stat-value.low-available-count {
  color: #f59e0b;
}

/* Шаг 3: Выбор рабочего места */
.workspace-selection {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.booking-time {
  color: #9ca3af;
  font-size: 0.8rem;
  line-height: 1.4;
}

.workspaces-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
}

.workspace-card {
  padding: 1.5rem;
  border-radius: 16px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  border: 2px solid transparent;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.workspace-card.available {
  background: rgba(16, 185, 129, 0.05);
  border-color: rgba(16, 185, 129, 0.2);
}

.workspace-card.available:hover {
  background: rgba(16, 185, 129, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(16, 185, 129, 0.2);
}

.workspace-card.booked {
  background: rgba(239, 68, 68, 0.05);
  border-color: rgba(239, 68, 68, 0.2);
}

.workspace-card.booked:hover {
  background: rgba(239, 68, 68, 0.1);
}


.workspace-card.inactive {
  background: rgba(107, 114, 128, 0.05);
  border-color: rgba(107, 114, 128, 0.2);
  opacity: 0.7;
}

.workspace-card.inactive:hover {
  background: rgba(107, 114, 128, 0.1);
  opacity: 0.8;
}

.workspace-info {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.workspace-place {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.workspace-label {
  color: #6b7280;
  font-size: 0.85rem;
  font-weight: 500;
}

.workspace-name {
  color: #1f2937;
  font-size: 1.2rem;
  font-weight: 600;
  line-height: 1.3;
}

.workspace-status-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  justify-content: flex-start;
}

.workspace-status {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  backdrop-filter: blur(10px);
}

.workspace-status.available {
  background: rgba(16, 185, 129, 0.2);
  color: #065f46;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.workspace-status.booked {
  background: rgba(239, 68, 68, 0.2);
  color: #991b1b;
  border: 1px solid rgba(239, 68, 68, 0.3);
}


.workspace-status.inactive {
  background: rgba(107, 114, 128, 0.2);
  color: #6b7280;
  border: 1px solid rgba(107, 114, 128, 0.3);
}

.workspace-booking-info {
  padding: 0.75rem;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(239, 68, 68, 0.2);
  word-break: break-word;
}

.workspace-booking-info small {
  color: #991b1b;
  font-size: 0.8rem;
  line-height: 1.4;
  white-space: normal;
  word-break: break-word;
  hyphens: auto;
  display: block;
}

.workspace-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: auto;
}

.book-workspace-btn {
  width: 100%;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.book-workspace-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
}

.book-workspace-btn:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

.cancel-workspace-booking-btn {
  width: 100%;
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.85rem;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.cancel-workspace-booking-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #f87171 0%, #ef4444 100%);
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
}

.cancel-workspace-booking-btn:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

.inactive-workspace-label {
  width: 100%;
  padding: 0.75rem 1.5rem;
  background: rgba(107, 114, 128, 0.15);
  color: #6b7280;
  border: 1px solid rgba(107, 114, 128, 0.3);
  border-radius: 8px;
  text-align: center;
  font-size: 0.85rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Адаптивность */
@media (max-width: 768px) {
  .booking-container {
    padding: 10px;
  }
    
  .booking-content {
    padding: 0;
  }
  
  .step-container {
    padding: 1.5rem;
  }
  
  .step-header {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .step-header h2 {
    font-size: 1.2rem;
  }
                
  .rooms-grid {
    grid-template-columns: 1fr;
  }
  
  .workspaces-grid {
    grid-template-columns: 1fr;
  }
  
  .booking-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .my-date-bookings {
    padding: 1rem;
  }
  
  .date-bookings-list {
    gap: 0.5rem;
  }
  
  .date-booking-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
    padding: 0.75rem;
  }
  
  .booking-room {
    font-size: 0.85rem;
  }
  
  .booking-status {
    font-size: 0.75rem;
    padding: 0.2rem 0.6rem;
  }
  
  .booking-time {
    font-size: 0.75rem;
  }
}
</style>

