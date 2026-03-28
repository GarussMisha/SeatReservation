/**
 * Dashboard - главная страница бронирования
 * Новый интерфейс с визуальным планом помещения
 */
<template>
  <div class="dashboard-page">
    <Header
      title="Бронирование рабочих мест"
      :userGreeting="`Добро пожаловать, ${authStore.userName || 'Пользователь'}`"
      showLogout
      @logout="handleLogout"
    />

    <div class="dashboard-content-wrapper">
      <!-- Фоновая декорация -->
      <div class="background-decoration">
        <div class="floating-shapes">
          <div class="shape shape-1"></div>
          <div class="shape shape-2"></div>
          <div class="shape shape-3"></div>
          <div class="shape shape-4"></div>
        </div>
      </div>

      <div class="dashboard-container">
        <main class="dashboard-main">
          <!-- Верхняя панель с выбором помещения и даты -->
          <BookingToolbar
            v-model="selection"
            :my-bookings="myBookings"
            @room-change="handleRoomChange"
            @date-change="handleDateChange"
          />

        <!-- Основная область с планом помещения -->
        <div class="plan-section">
          <div v-if="!selectedRoom" class="no-selection">
            <div class="empty-state">
              <svg class="empty-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
              </svg>
              <h3>Выберите помещение</h3>
              <p>Используйте панель сверху для выбора помещения и даты</p>
            </div>
          </div>

          <div v-else class="plan-container">
            <div class="plan-header">
              <div class="plan-title">
                <h2>{{ selectedRoom.name }}</h2>
                <span class="plan-address">{{ selectedRoom.address }}</span>
                <!-- Предупреждение если помещение не активно -->
                <span v-if="selectedRoom.status_id === 2" class="room-inactive-warning">
                  <svg class="warning-icon-inline" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                  </svg>
                  Помещение не активно. Бронирование недоступно.
                </span>
              </div>
              <div class="plan-stats">
                <div class="stat-item">
                  <span class="stat-label">Всего мест:</span>
                  <span class="stat-value">{{ totalWorkspaces }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Доступно:</span>
                  <span class="stat-value available">{{ availableWorkspaces }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Занято:</span>
                  <span class="stat-value booked">{{ bookedWorkspaces }}</span>
                </div>
              </div>
            </div>

            <RoomPlanCanvas
              ref="roomPlan"
              :room-id="selectedRoom.id"
              :selected-date="selectedDate"
              :field-width="selectedRoom.field_width || 50"
              :field-height="selectedRoom.field_height || 50"
              :disabled="selectedRoom.status_id === 2"
              @workspace-click="handleWorkspaceClick"
              @workspace-hover="handleWorkspaceHover"
              @workspaces-loaded="updateWorkspacesStats"
            />
          </div>
        </div>

        <!-- Секция с бронированиями пользователя -->
        <div class="my-bookings-section">
          <h3>Мои бронирования</h3>

          <div v-if="loadingMyBookings" class="loading">
            Загрузка бронирований...
          </div>

          <div v-else-if="sortedMyBookings.length === 0" class="no-bookings">
            <svg class="no-bookings-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
            <p>У вас пока нет бронирований</p>
          </div>

          <div v-else>
            <div class="bookings-list" :class="{ 'bookings-list-scrollable': sortedMyBookings.length > 2 && !showAllBookings }">
              <div
                v-for="(booking, index) in displayedBookings"
                :key="booking.id"
                :class="['booking-item', booking.status_name]"
              >
                <div class="booking-info">
                  <h4>{{ booking.workspace_name }}</h4>
                  <p class="booking-room">{{ booking.workspace_room_name }}</p>
                  <p class="booking-date">
                    <strong>Дата:</strong> {{ formatDate(booking.booking_date) }}
                  </p>
                  <p class="booking-status" :class="getStatusClass(booking.status_name)">
                    <strong>Статус:</strong> {{ getStatusDisplayName(booking.status_name) }}
                  </p>
                </div>
                <div class="booking-actions" v-if="canCancelBooking(booking)">
                  <button
                    @click="confirmCancelBooking(booking)"
                    class="cancel-btn"
                    :disabled="cancelling === booking.id"
                  >
                    {{ cancelling === booking.id ? 'Отмена...' : 'Отменить' }}
                  </button>
                </div>
              </div>
            </div>
            
            <!-- Кнопка показать все/скрыть -->
            <div v-if="sortedMyBookings.length > 2" class="show-all-toggle">
              <button @click="showAllBookings = !showAllBookings" class="toggle-btn">
                {{ showAllBookings ? 'Скрыть' : `Показать все (${sortedMyBookings.length})` }}
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>

    <!-- Модальное окно подтверждения -->
    <BookingConfirmModal
      :show="showModal"
      :mode="modalMode"
      :workspace-name="selectedWorkspace?.name"
      :workspace-id="selectedWorkspace?.id"
      :booking-id="selectedBooking?.id"
      :date="selectedDate"
      :room-name="selectedRoom?.name"
      :is-loading="isProcessing"
      @close="closeModal"
      @confirm="handleModalConfirm"
      @cancel="handleModalCancel"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { bookingsAPI, roomsAPI } from '@/services/api'
import { useNotificationStore } from '@/stores/notifications'
import Header from '@/components/Header.vue'
import BookingToolbar from '@/components/dashboard/BookingToolbar.vue'
import RoomPlanCanvas from '@/components/dashboard/RoomPlanCanvas.vue'
import BookingConfirmModal from '@/components/dashboard/BookingConfirmModal.vue'

const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

// Состояние выбора
const selection = ref({ roomId: null, date: null })
const selectedRoom = ref(null)
const selectedDate = ref(null)

// Метод logout
const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

// Данные
const rooms = ref([])
const myBookings = ref([])
const loadingMyBookings = ref(false)
const showAllBookings = ref(false)  // Показывать все брони или только первые 2
const cancelling = ref(null)

// Модальное окно
const showModal = ref(false)
const modalMode = ref('book') // 'book' или 'cancel'
const selectedWorkspace = ref(null)
const selectedBooking = ref(null)
const isProcessing = ref(false)

// Ссылка на компонент плана
const roomPlan = ref(null)

// Вычисляемые свойства
const totalWorkspaces = computed(() => {
  return workspacesStats.value.total
})

const availableWorkspaces = computed(() => {
  return workspacesStats.value.available
})

const bookedWorkspaces = computed(() => {
  return workspacesStats.value.booked
})

// Статистика рабочих мест
const workspacesStats = ref({
  total: 0,
  available: 0,
  booked: 0
})

const updateWorkspacesStats = (workspaces) => {
  workspacesStats.value = {
    total: workspaces.length,
    available: workspaces.filter(ws => ws.status === 'available').length,
    booked: workspaces.filter(ws => ws.status === 'booked' || ws.status === 'myBooking').length
  }
}

const sortedMyBookings = computed(() => {
  // Брони уже отсортированы в loadMyBookings
  return myBookings.value
})

// Отображаем только первые 2 брони если не нажата кнопка "показать все"
const displayedBookings = computed(() => {
  if (showAllBookings.value) {
    return sortedMyBookings.value
  }
  return sortedMyBookings.value.slice(0, 2)  // Только первые 2
})

// Обработчики
const handleRoomChange = (room) => {
  selectedRoom.value = room
}

const handleDateChange = (date) => {
  selectedDate.value = date
}

const handleWorkspaceClick = (workspace) => {
  if (workspace.status === 'available') {
    selectedWorkspace.value = workspace
    modalMode.value = 'book'
    showModal.value = true
  } else if (workspace.status === 'myBooking' && workspace.currentBooking) {
    selectedBooking.value = workspace.currentBooking
    selectedWorkspace.value = workspace
    modalMode.value = 'cancel'
    showModal.value = true
  }
}

const handleWorkspaceHover = (workspace) => {
  // Можно добавить дополнительную логику при наведении
}

const confirmCancelBooking = (booking) => {
  selectedBooking.value = booking
  selectedWorkspace.value = { name: booking.workspace_name }
  modalMode.value = 'cancel'
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  selectedWorkspace.value = null
  selectedBooking.value = null
}

const handleModalConfirm = async ({ workspaceId, bookingId, date }) => {
  try {
    // Устанавливаем флаг обработки ДО создания брони
    isProcessing.value = true

    if (modalMode.value === 'book') {
      // Бронирование
      const bookingData = {
        booking_date: date,
        account_id: authStore.user.id,
        workspace_id: workspaceId,
        status_id: 13  // 13 = confirmed (подтверждено/активно)
      }

      console.log('=== Создание бронирования ===')
      console.log('bookingData:', bookingData)
      await bookingsAPI.createBooking(bookingData)
      console.log('Бронирование создано')
      notificationStore.success(
        `Рабочее место забронировано на ${formatDate(date)}`,
        'Бронирование подтверждено'
      )
    } else if (modalMode.value === 'cancel' && bookingId) {
      // Отмена
      console.log('=== Отмена бронирования ===')
      console.log('bookingId:', bookingId)
      await bookingsAPI.cancelBooking(bookingId)
      console.log('Бронирование отменено на backend')
      notificationStore.success('Бронирование отменено', 'Отмена бронирования')
    }

    closeModal()
    await loadMyBookings()
    
    // Обновляем план помещения
    console.log('=== Обновление плана помещения ===')
    if (roomPlan.value?.refreshPlan) {
      console.log('Вызов refreshPlan()...')
      await roomPlan.value.refreshPlan()
      console.log('План обновлён')
    } else {
      console.warn('roomPlan.value или refreshPlan не доступен')
    }
  } catch (error) {
    console.error('Ошибка:', error)
    const errorMessage = error.response?.data?.detail || error.message
    notificationStore.error(errorMessage, 'Ошибка')
  } finally {
    isProcessing.value = false
  }
}

const handleModalCancel = () => {
  closeModal()
}

// Загрузка бронирований
const loadMyBookings = async () => {
  if (!authStore.user) return

  try {
    loadingMyBookings.value = true
    const bookings = await bookingsAPI.getBookingsByAccount(authStore.user.id, false)
    // Сортируем: сначала активные (confirmed), потом отменённые
    // Внутри групп сортируем по дате (новые сверху)
    myBookings.value = bookings.sort((a, b) => {
      // Сначала сортируем по статусу (активные сверху)
      const isActiveA = a.status_name === 'confirmed'
      const isActiveB = b.status_name === 'confirmed'
      
      if (isActiveA && !isActiveB) return -1  // Активные выше
      if (!isActiveA && isActiveB) return 1   // Активные выше
      
      // Если статусы одинаковые, сортируем по дате (новые сверху)
      const dateA = new Date(a.booking_date)
      const dateB = new Date(b.booking_date)
      return dateB - dateA
    })
  } catch (error) {
    console.error('Ошибка загрузки бронирований:', error)
  } finally {
    loadingMyBookings.value = false
  }
}

// Проверка возможности отмены
const canCancelBooking = (booking) => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const bookingDate = new Date(booking.booking_date)
  bookingDate.setHours(0, 0, 0, 0)

  return booking.status_name !== 'cancelled' && bookingDate >= today
}

// Форматирование даты
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

// Класс статуса
const getStatusClass = (statusName) => {
  const classes = {
    pending: 'pending',
    confirmed: 'confirmed',
    cancelled: 'cancelled',
    completed: 'completed'
  }
  return classes[statusName] || ''
}

// Отображаемое имя статуса
const getStatusDisplayName = (statusName) => {
  const names = {
    pending: 'Ожидает подтверждения',
    confirmed: 'Подтверждено',
    cancelled: 'Отменено',
    completed: 'Завершено'
  }
  return names[statusName] || statusName
}

// Watchers
watch(() => selection.value, (newVal) => {
  if (newVal.roomId) {
    const room = rooms.value.find(r => r.id === newVal.roomId)
    if (room) {
      selectedRoom.value = room
    }
  }
  if (newVal.date) {
    selectedDate.value = newVal.date
  }
}, { deep: true })

// Lifecycle
onMounted(async () => {
  await loadMyBookings()

  // Загружаем помещения
  try {
    rooms.value = await roomsAPI.getRooms()
    
    // Выбираем первое помещение по умолчанию
    if (rooms.value.length > 0) {
      selection.value = {
        roomId: rooms.value[0].id,
        date: new Date().toISOString().split('T')[0]
      }
    }
  } catch (error) {
    console.error('Ошибка загрузки помещений:', error)
  }
})
</script>

<style scoped>
.dashboard-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  padding-top: 100px;
}

.dashboard-content-wrapper {
  flex: 1;
  position: relative;
  z-index: 10;
  min-height: calc(100vh - 180px);
}

.background-decoration {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 0;
}

.floating-shapes {
  position: absolute;
  width: 100%;
  height: 100%;
}

.shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  filter: blur(60px);
}

.shape-1 {
  width: 400px;
  height: 400px;
  top: -100px;
  right: -100px;
  background: rgba(102, 126, 234, 0.2);
}

.shape-2 {
  width: 300px;
  height: 300px;
  bottom: -50px;
  left: -50px;
  background: rgba(118, 75, 162, 0.2);
}

.shape-3 {
  width: 200px;
  height: 200px;
  top: 50%;
  left: 50%;
  background: rgba(102, 126, 234, 0.15);
}

.shape-4 {
  width: 250px;
  height: 250px;
  bottom: 20%;
  right: 10%;
  background: rgba(118, 75, 162, 0.1);
}

.dashboard-container {
  max-width: 1600px;
  margin: 0 auto;
  padding: 2rem;
}

.dashboard-main {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  padding: 2rem;
  min-height: calc(100vh - 260px);
}

.plan-section {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(102, 126, 234, 0.15);
  overflow: hidden;
  min-height: 600px;
}

.no-selection {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 600px;
}

.empty-state {
  text-align: center;
  color: #666;
}

.empty-icon-svg {
  width: 80px;
  height: 80px;
  display: block;
  margin-bottom: 1rem;
  opacity: 0.5;
  color: var(--text-muted);
}

.no-bookings-icon-svg {
  width: 60px;
  height: 60px;
  display: block;
  margin: 0 auto 1rem;
  opacity: 0.5;
  color: var(--text-muted);
}

.warning-icon-inline {
  width: 18px;
  height: 18px;
  vertical-align: middle;
  margin-right: 6px;
}

.empty-state h3 {
  margin: 0 0 0.5rem;
  font-size: 1.5rem;
  color: #333;
}

.empty-state p {
  margin: 0;
  font-size: 1rem;
  color: #999;
}

.plan-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #f0f0f0;
}

.plan-title h2 {
  margin: 0 0 0.25rem;
  font-size: 1.5rem;
  color: #1f2937;
}

.plan-address {
  font-size: 0.9rem;
  color: #666;
}

.room-inactive-warning {
  margin-top: 0.5rem;
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(251, 146, 60, 0.1) 100%);
  border-left: 4px solid #f59e0b;
  border-radius: 8px;
  font-size: 0.9rem;
  color: #92400e;
  font-weight: 500;
}

.plan-stats {
  display: flex;
  gap: 2rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.stat-label {
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #333;
}

.stat-value.available {
  color: #22c55e;
}

.stat-value.booked {
  color: #3b82f6;
}

.my-bookings-section {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  margin-top: 2rem;
  box-shadow: 0 4px 24px rgba(102, 126, 234, 0.15);
}

.my-bookings-section h3 {
  margin: 0 0 1.5rem;
  font-size: 1.25rem;
  color: #1f2937;
}

.loading {
  text-align: center;
  color: #666;
  padding: 2rem;
}

.no-bookings {
  text-align: center;
  color: #999;
  padding: 3rem 1rem;
}

.no-bookings-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.no-bookings p {
  margin: 0;
  font-size: 1rem;
}

.bookings-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.bookings-list.bookings-list-scrollable {
  max-height: 420px;  /* Высота для 2 бронирований без прокрутки */
  overflow-y: auto;
  padding-right: 0.5rem;
}

.show-all-toggle {
  margin-top: 1rem;
  text-align: center;
}

.toggle-btn {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border: 2px solid rgba(102, 126, 234, 0.3);
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  color: #667eea;
  transition: all 0.3s;
}

.toggle-btn:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
  border-color: rgba(102, 126, 234, 0.5);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.booking-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.03) 0%, rgba(118, 75, 162, 0.03) 100%);
  border-radius: 12px;
  border: 1px solid rgba(102, 126, 234, 0.1);
  transition: all 0.3s;
}

.booking-item:hover {
  border-color: rgba(102, 126, 234, 0.3);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
}

.booking-item.cancelled {
  opacity: 0.6;
}

.booking-info h4 {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
  color: #1f2937;
}

.booking-room {
  margin: 0 0 0.5rem;
  font-size: 0.9rem;
  color: #666;
}

.booking-date,
.booking-status {
  margin: 0.25rem 0;
  font-size: 0.85rem;
  color: #666;
}

.booking-status {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 500;
}

.booking-status.pending {
  background: rgba(245, 158, 11, 0.1);
  color: #d97706;
}

.booking-status.confirmed {
  background: rgba(40, 167, 69, 0.1);
  color: #16a34a;
}

.booking-status.cancelled {
  background: rgba(220, 53, 69, 0.1);
  color: #dc2626;
}

.booking-status.completed {
  background: rgba(107, 114, 128, 0.1);
  color: #6b7280;
}

.cancel-btn {
  padding: 0.625rem 1.25rem;
  background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s;
}

.cancel-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #e74a3b 0%, #d32f2f 100%);
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
  transform: translateY(-2px);
}

.cancel-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
