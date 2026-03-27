/**
 * BookingToolbar - верхняя панель для выбора помещения и даты
 * Используется на Dashboard для быстрого переключения между помещениями и датами
 */
<template>
  <div class="booking-toolbar">
    <div class="toolbar-section">
      <label class="toolbar-label">
        <span class="label-icon">🏢</span>
        Помещение
      </label>
      <div class="room-selector">
        <select
          v-model="selectedRoomId"
          class="room-select"
          @change="handleRoomChange"
        >
          <option value="" disabled>Выберите помещение</option>
          <option
            v-for="room in rooms"
            :key="room.id"
            :value="room.id"
          >
            {{ room.name }} ({{ room.address }})
          </option>
        </select>
      </div>
    </div>

    <div class="toolbar-section">
      <label class="toolbar-label">
        <span class="label-icon">📅</span>
        Дата
      </label>
      <div class="date-selector">
        <button
          @click="previousMonth"
          class="nav-btn"
          title="Предыдущий месяц"
        >
          ‹
        </button>
        
        <div class="calendar-wrapper">
          <button @click="toggleCalendar" class="date-display">
            {{ formattedDate }}
            <span class="calendar-icon">📅</span>
          </button>
          
          <transition name="calendar-slide">
            <div v-if="showCalendar" class="mini-calendar">
              <div class="calendar-header">
                <button @click="previousMonth" class="calendar-nav">‹</button>
                <span class="calendar-month-year">{{ currentMonthYear }}</span>
                <button @click="nextMonth" class="calendar-nav">›</button>
              </div>
              
              <div class="calendar-grid">
                <div
                  v-for="day in calendarDays"
                  :key="day.date"
                  :class="[
                    'calendar-day',
                    day.isToday ? 'today' : '',
                    day.isPast ? 'past' : '',
                    day.isSelected ? 'selected' : '',
                    day.hasBooking ? 'has-booking' : ''
                  ]"
                  @click="selectDate(day.date)"
                >
                  <span class="day-number">{{ day.day }}</span>
                  <div v-if="day.hasBooking" class="booking-dot"></div>
                </div>
              </div>
            </div>
          </transition>
        </div>
        
        <button
          @click="nextMonth"
          class="nav-btn"
          title="Следующий месяц"
        >
          ›
        </button>
      </div>
    </div>

    <div class="toolbar-section info-section">
      <div v-if="selectedRoom && selectedDate" class="room-info-display">
        <span class="info-label">Выбрано:</span>
        <span class="info-value">{{ selectedRoom.name }}</span>
        <span class="info-separator">•</span>
        <span class="info-value">{{ formattedDate }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { roomsAPI } from '@/services/api'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({ roomId: null, date: null })
  },
  myBookings: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue', 'room-change', 'date-change'])

// Состояние
const rooms = ref([])
const selectedRoomId = ref(null)
const currentDate = ref(new Date())
const showCalendar = ref(false)

// Вычисляемые свойства
const selectedRoom = computed(() => {
  return rooms.value.find(r => r.id === selectedRoomId.value) || null
})

const selectedDate = computed(() => {
  if (!currentDate.value) return null
  return formatDateForAPI(currentDate.value)
})

const formattedDate = computed(() => {
  if (!currentDate.value) return ''
  return currentDate.value.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
})

const currentMonthYear = computed(() => {
  return currentDate.value.toLocaleDateString('ru-RU', {
    month: 'long',
    year: 'numeric'
  })
})

// Дни календаря для отображения
const calendarDays = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  const days = []
  
  // Добавляем пустые ячейки до первого дня месяца
  const startDayOfWeek = firstDay.getDay()
  for (let i = 0; i < startDayOfWeek; i++) {
    days.push({ date: null, day: '' })
  }
  
  // Добавляем дни месяца
  for (let day = 1; day <= lastDay.getDate(); day++) {
    const date = new Date(year, month, day)
    const dateStr = formatDateForAPI(date)
    
    const isToday = date.getTime() === today.getTime()
    const isPast = date < today
    const isSelected = props.modelValue.date === dateStr
    const hasBooking = props.myBookings.some(
      booking => booking.booking_date === dateStr && booking.status_name !== 'cancelled'
    )
    
    days.push({
      date: dateStr,
      day,
      isToday,
      isPast,
      isSelected,
      hasBooking
    })
  }
  
  return days
})

// Методы
const handleRoomChange = () => {
  emit('update:modelValue', {
    roomId: selectedRoomId.value,
    date: selectedDate.value
  })
  emit('room-change', selectedRoom.value)
}

const selectDate = (date) => {
  if (!date) return
  
  currentDate.value = new Date(date)
  showCalendar.value = false
  
  emit('update:modelValue', {
    roomId: selectedRoomId.value,
    date: date
  })
  emit('date-change', date)
}

const toggleCalendar = () => {
  showCalendar.value = !showCalendar.value
}

const previousMonth = () => {
  currentDate.value = new Date(
    currentDate.value.getFullYear(),
    currentDate.value.getMonth() - 1,
    1
  )
}

const nextMonth = () => {
  currentDate.value = new Date(
    currentDate.value.getFullYear(),
    currentDate.value.getMonth() + 1,
    1
  )
}

const formatDateForAPI = (date) => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const closeCalendarOnClickOutside = (event) => {
  if (showCalendar.value && !event.target.closest('.calendar-wrapper')) {
    showCalendar.value = false
  }
}

// Загрузка помещений
const loadRooms = async () => {
  try {
    const roomsData = await roomsAPI.getRooms()
    rooms.value = roomsData
    
    // Выбираем первое помещение по умолчанию
    if (rooms.value.length > 0 && !selectedRoomId.value) {
      selectedRoomId.value = rooms.value[0].id
      handleRoomChange()
    }
  } catch (error) {
    console.error('Ошибка загрузки помещений:', error)
  }
}

// Watchers
watch(() => props.modelValue, (newValue) => {
  if (newValue.roomId && newValue.roomId !== selectedRoomId.value) {
    selectedRoomId.value = newValue.roomId
  }
  if (newValue.date) {
    currentDate.value = new Date(newValue.date)
  }
}, { deep: true })

// Lifecycle
onMounted(() => {
  loadRooms()
  document.addEventListener('click', closeCalendarOnClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', closeCalendarOnClickOutside)
})
</script>

<style scoped>
.booking-toolbar {
  display: flex;
  align-items: flex-start;
  gap: 2rem;
  padding: 1.5rem 2rem;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(102, 126, 234, 0.15);
  margin-bottom: 2rem;
}

.toolbar-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.toolbar-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: #667eea;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.label-icon {
  font-size: 1.1rem;
}

.room-selector {
  min-width: 300px;
}

.room-select {
  width: 100%;
  padding: 0.875rem 1.25rem;
  background: white;
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 500;
  color: #333;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%23667eea' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 1rem center;
  background-repeat: no-repeat;
  background-size: 1.25rem 1.25rem;
  padding-right: 3rem;
}

.room-select:hover {
  border-color: rgba(102, 126, 234, 0.4);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
  transform: translateY(-1px);
}

.room-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.date-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav-btn {
  padding: 0.75rem 1.25rem;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 12px;
  cursor: pointer;
  font-size: 1.25rem;
  font-weight: 600;
  color: #667eea;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.nav-btn:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
  border-color: rgba(102, 126, 234, 0.4);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
  transform: translateY(-1px);
}

.calendar-wrapper {
  position: relative;
}

.date-display {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 1.25rem;
  background: white;
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 12px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 500;
  color: #333;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.date-display:hover {
  border-color: rgba(102, 126, 234, 0.4);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
  transform: translateY(-1px);
}

.calendar-icon {
  font-size: 1.1rem;
}

.mini-calendar {
  position: absolute;
  top: calc(100% + 0.5rem);
  left: 0;
  z-index: 1000;
  padding: 1rem;
  background: white;
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
  min-width: 280px;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.calendar-nav {
  padding: 0.25rem 0.5rem;
  background: none;
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 4px;
  cursor: pointer;
  font-size: 1.1rem;
  color: #667eea;
  transition: all 0.2s;
}

.calendar-nav:hover {
  background: rgba(102, 126, 234, 0.1);
}

.calendar-month-year {
  font-size: 0.95rem;
  font-weight: 600;
  color: #333;
  text-transform: capitalize;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.25rem;
}

.calendar-day {
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  color: #333;
  transition: all 0.2s;
  position: relative;
}

.calendar-day:hover:not(.past):not(:empty) {
  background: rgba(102, 126, 234, 0.1);
}

.calendar-day.today {
  background: rgba(102, 126, 234, 0.2);
  font-weight: 600;
  color: #667eea;
}

.calendar-day.past {
  color: #ccc;
  cursor: not-allowed;
}

.calendar-day.selected {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
}

.calendar-day.has-booking::after {
  content: '';
  position: absolute;
  bottom: 2px;
  width: 4px;
  height: 4px;
  background: #28a745;
  border-radius: 50%;
}

.calendar-day.selected.has-booking::after {
  background: white;
}

.day-number {
  display: flex;
  align-items: center;
  justify-content: center;
}

.booking-dot {
  position: absolute;
  bottom: 2px;
  width: 4px;
  height: 4px;
  background: #28a745;
  border-radius: 50%;
}

.calendar-slide-enter-active,
.calendar-slide-leave-active {
  transition: all 0.2s ease;
}

.calendar-slide-enter-from,
.calendar-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.info-section {
  margin-left: auto;
}

.room-info-display {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 8px;
  font-size: 0.9rem;
}

.info-label {
  color: #666;
  font-weight: 500;
}

.info-value {
  color: #333;
  font-weight: 600;
}

.info-separator {
  color: #ccc;
}
</style>
