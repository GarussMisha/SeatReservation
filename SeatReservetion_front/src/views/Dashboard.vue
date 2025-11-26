<template>
<div class="dashboard-page">
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
    <!-- Заголовок перемещен в глобальный компонент Header -->
    <main class="dashboard-content">
      <div class="welcome-section">
        <h2>Система бронирования рабочих мест</h2>
        <p>Выбирайте день на который вы хотите забронировать место</p>
      </div>

      <!-- Главная секция с кнопками и таблицей бронирований -->
      <div class="main-section">
        <!-- Правая колонка - Календарь бронирований -->
        <div class="right-column">
          <div class="calendar-section">
            <!-- Заголовок календаря -->
            <div class="calendar-header">
              <h3>Календарь бронирований</h3>
              <span class="booking-count">{{ filteredBookings.length }} бронирований</span>
            </div>

            <!-- Управление календарем и фильтрами -->
            <div class="calendar-controls">
              <!-- Навигация по месяцам -->
              <div class="calendar-navigation">
                <button @click="previousMonth" class="nav-btn">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M15 18l-6-6 6-6"/>
                  </svg>
                </button>
                
                <div class="current-month">
                  {{ months[currentMonth] }} {{ currentYear }}
                </div>
                
                <button @click="nextMonth" class="nav-btn">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M9 18l6-6-6-6"/>
                  </svg>
                </button>
                
                <button @click="goToToday" class="today-btn">Сегодня</button>
              </div>

              <!-- Фильтры -->
              <div class="calendar-filters">
                <button
                  v-for="filter in filters"
                  :key="filter.key"
                  @click="activeFilter = filter.key"
                  :class="['filter-btn', { active: activeFilter === filter.key }]"
                >
                  {{ filter.label }}
                </button>
              </div>
            </div>
            
            <!-- Календарная сетка -->
            <div class="calendar-container">
              <div class="calendar-grid">
                <!-- Заголовки дней недели -->
                <div class="weekdays">
                  <div v-for="day in weekDays" :key="day" class="weekday">
                    {{ day }}
                  </div>
                </div>
                
                <!-- Дни месяца -->
                <div class="calendar-days">
                  <div
                    v-for="(day, index) in calendarDays"
                    :key="index"
                    :class="[
                      'calendar-day',
                      {
                        'other-month': !day.isCurrentMonth,
                        'today': day.isToday,
                        'current-week': day.isCurrentWeek,
                        'has-bookings': getFilteredBookingsForDate(day.date).length > 0,
                        'has-inactive-bookings': hasInactiveBookingsForDay(day) && !hasActiveBookingsForDay(day),
                        'has-active-bookings': hasActiveBookingsForDay(day),
                        'clickable-day': true
                      }
                    ]"
                    @click="goToBookingDate(day.date)"
                  >
                    <div class="day-number">{{ day.date.getDate() }}</div>
                    
                    <div v-if="getFilteredBookingsForDate(day.date).length > 0" class="bookings-indicators">
                      <div
                        :class="[
                          'booking-indicator',
                          hasActiveBookings(getFilteredBookingsForDate(day.date)) ? 'has-active' : 'no-active'
                        ]"
                        @mouseenter="expandDay(day)"
                        @mouseleave="collapseDay"
                      >
                        <span class="booking-text">
                          {{ getBookingIndicatorText(getFilteredBookingsForDate(day.date)) }}
                        </span>
                        <span v-if="getPriorityBookingForDisplay(day.date)" class="booking-details">
                          {{ getPriorityBookingForDisplay(day.date).workspace_name }}
                          <span v-if="getPriorityBookingForDisplay(day.date).workspace_room_name" class="room-name">
                            - {{ getPriorityBookingForDisplay(day.date).workspace_room_name }}
                          </span>
                        </span>
                        <span v-if="getFilteredBookingsForDate(day.date).length > 1" class="booking-ellipsis">...</span>
                      </div>
                    </div>
                    
                    <!-- Расширенная информация о бронированиях -->
                    <div
                      v-if="expandedDay && isSameDay(expandedDay.date, day.date)"
                      class="expanded-bookings"
                      @mouseenter="expandDay(day)"
                      @mouseleave="collapseDay"
                    >
                      <div class="expanded-content">
                        <div
                          v-for="(booking, index) in getLimitedBookingsForExpandedDay(day, 2)"
                          :key="booking.id"
                          :class="[
                            'expanded-booking',
                            isActiveBooking(booking) ? 'active' : 'inactive'
                          ]"
                        >
                          <div class="booking-workspace">
                            {{ booking.workspace_name }}
                            <span v-if="booking.workspace_room_name" class="workspace-room">
                              - {{ booking.workspace_room_name }}
                            </span>
                          </div>
                          <div class="booking-status">
                            <span v-if="isActiveBooking(booking)">
                              {{ getStatusDisplayName(booking.status_name) }}
                            </span>
                            <span v-else>
                              Прошедшее
                            </span>
                          </div>
                        </div>
                        
                        <!-- Индикатор дополнительных бронирований -->
                        <div
                          v-if="getFilteredBookingsForDate(day.date).length > 2"
                          class="more-bookings-indicator"
                        >
                          ... и еще {{ getFilteredBookingsForDate(day.date).length - 2 }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>     
            <div class="booking-hint">
              <p>
                <span class="hint-icon">📅</span>
                Чтобы создать бронирование, выберите день на календаре
              </p>
              <div class="features-list">
                <div class="feature-card clickable" @click="goToProfile">
                  <div class="feature-action">Открыть профиль</div>
                </div>

                <div
                  v-if="authStore.isAdmin"
                  class="feature-card clickable admin-card"
                  @click="goToAdmin"
                >
                  <div class="feature-action">Открыть Админ панель</div>
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
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import { bookingsAPI } from '../services/api'

const authStore = useAuthStore()
const router = useRouter()

// Состояние
const userBookings = ref([])
const stats = ref({
  totalBookings: 0,
  todayBookings: 0,
  upcomingBookings: 0
})
const loading = ref(false)
const activeFilter = ref('all') // Фильтр: all, active, completed (по умолчанию все)
const currentDate = ref(new Date()) // Текущая дата для календаря

// Состояние для расширенного дня
const expandedDay = ref(null)
let collapseTimeout = null // Таймер для отложенного скрытия

// Фильтры
const filters = [
  { key: 'all', label: 'Все' },
  { key: 'active', label: 'Активные (Запланированные)' },
  { key: 'completed', label: 'Неактивные (Завершонные)' }
]

// Месяцы и дни недели для календаря
const months = [
  'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
  'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
]

const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

// Инициализация
onMounted(async () => {
  if (authStore.user) {
    await loadUserData()
  }
})

// Очистка таймера при размонтировании компонента
onUnmounted(() => {
  if (collapseTimeout) {
    clearTimeout(collapseTimeout)
    collapseTimeout = null
  }
})

// Сортированные бронирования
const sortedUserBookings = computed(() => {
  return [...userBookings.value].sort((a, b) => {
    // По умолчанию: сначала предстоящие, потом прошедшие, затем по дате создания
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    
    const dateA = new Date(a.booking_date)
    const dateB = new Date(b.booking_date)
    const todayA = new Date(dateA.getFullYear(), dateA.getMonth(), dateA.getDate())
    const todayB = new Date(dateB.getFullYear(), dateB.getMonth(), dateB.getDate())
    
    const isUpcomingA = todayA >= today
    const isUpcomingB = todayB >= today
    
    if (isUpcomingA && !isUpcomingB) return -1
    if (!isUpcomingA && isUpcomingB) return 1
    
    // Если оба предстоящих или оба прошедшие, сортируем по дате создания (новые сверху)
    return new Date(b.created_at || b.updated_at || b.booking_date) - new Date(a.created_at || a.updated_at || a.booking_date)
  })
})

// Отфильтрованные бронирования для календаря
const calendarBookings = computed(() => {
  const bookings = [...userBookings.value]
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  
  let filteredBookings = []
  
  switch (activeFilter.value) {
    case 'active':
      // Показываем только активные (не отмененные и не прошедшие)
      filteredBookings = bookings.filter(booking => {
        const bookingDate = new Date(booking.booking_date)
        const bookingDateOnly = new Date(bookingDate.getFullYear(), bookingDate.getMonth(), bookingDate.getDate())
        return bookingDateOnly >= today && booking.status_name !== 'cancelled'
      })
      // Сортируем активные по дате
      filteredBookings.sort((a, b) => new Date(a.booking_date) - new Date(b.booking_date))
      break
      
    case 'completed':
      // Показываем только завершенные (отмененные или прошедшие)
      filteredBookings = bookings.filter(booking => {
        const bookingDate = new Date(booking.booking_date)
        const bookingDateOnly = new Date(bookingDate.getFullYear(), bookingDate.getMonth(), bookingDate.getDate())
        return bookingDateOnly < today || booking.status_name === 'cancelled'
      })
      // Сортируем завершенные по дате (новые сверху)
      filteredBookings.sort((a, b) => new Date(b.booking_date) - new Date(a.booking_date))
      break
      
    default: // 'all'
      // Для режима "Все": показываем все бронирования
      filteredBookings = bookings
      // Сортируем все бронирования: сначала активные, потом завершенные
      filteredBookings.sort((a, b) => {
        const aIsActive = isActiveBooking(a)
        const bIsActive = isActiveBooking(b)
        
        if (aIsActive && !bIsActive) return -1
        if (!aIsActive && bIsActive) return 1
        
        // Если оба активных или оба неактивных, сортируем по дате (новые сверху)
        return new Date(b.booking_date) - new Date(a.booking_date)
      })
      break
  }
  
  return filteredBookings
})

// Отфильтрованные бронирования для общей фильтрации
const filteredBookings = computed(() => {
  const bookings = sortedUserBookings.value
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  
  switch (activeFilter.value) {
    case 'active':
      return bookings.filter(booking => {
        const bookingDate = new Date(booking.booking_date)
        const bookingDateOnly = new Date(bookingDate.getFullYear(), bookingDate.getMonth(), bookingDate.getDate())
        return bookingDateOnly >= today && booking.status_name !== 'cancelled'
      })
    
    case 'completed':
      return bookings.filter(booking => {
        const bookingDate = new Date(booking.booking_date)
        const bookingDateOnly = new Date(bookingDate.getFullYear(), bookingDate.getMonth(), bookingDate.getDate())
        return bookingDateOnly < today || booking.status_name === 'cancelled'
      })
    
    default:
      return bookings
  }
})

// Календарная логика
const currentMonth = computed(() => currentDate.value.getMonth())
const currentYear = computed(() => currentDate.value.getFullYear())

// Получение дней месяца для календаря
const calendarDays = computed(() => {
  const year = currentYear.value
  const month = currentMonth.value
  
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const startDate = new Date(firstDay)
  
  // Начинаем с понедельника
  startDate.setDate(startDate.getDate() - (firstDay.getDay() || 7) + 1)
  
  const days = []
  const current = new Date(startDate)
  
  // Генерируем 42 дня (6 недель)
  for (let i = 0; i < 42; i++) {
    const isCurrentWeek = isCurrentWeekDay(current)
    days.push({
      date: new Date(current),
      isCurrentMonth: current.getMonth() === month,
      isToday: isSameDay(current, new Date()),
      isCurrentWeek,
      bookings: getFilteredBookingsForDate(current)
    })
    current.setDate(current.getDate() + 1)
  }
  
  return days
})

// Проверка, является ли день частью текущей недели
const isCurrentWeekDay = (date) => {
  const today = new Date()
  const todayStart = new Date(today.getFullYear(), today.getMonth(), today.getDate())
  const dayOfWeek = todayStart.getDay() || 7 // Понедельник = 1, Воскресенье = 7
  
  const weekStart = new Date(todayStart)
  weekStart.setDate(todayStart.getDate() - dayOfWeek + 1)
  
  const weekEnd = new Date(weekStart)
  weekEnd.setDate(weekStart.getDate() + 6)
  
  return date >= weekStart && date <= weekEnd
}
// Получение приоритетной брони из отфильтрованных бронирований
const getPriorityBookingForDisplay = (date) => {
  const filteredBookingsForDate = getFilteredBookingsForDate(date)
  
  if (filteredBookingsForDate.length === 0) {
    return null
  }
  
  // Сортируем бронирования по приоритету
  const sortedBookings = [...filteredBookingsForDate].sort((a, b) => {
    const aIsActive = isActiveBooking(a)
    const bIsActive = isActiveBooking(b)
    
    // 1. Активные брони имеют наивысший приоритет
    if (aIsActive && !bIsActive) return -1
    if (!aIsActive && bIsActive) return 1
    
    // 2. Если обе активные или обе неактивные, сортируем по времени создания (новые сверху)
    return new Date(b.created_at || b.updated_at || b.booking_date) - new Date(a.created_at || a.updated_at || a.booking_date)
  })
  
  // Возвращаем первую (приоритетную) бронь
  return sortedBookings[0]
}

// Проверка совпадения дат
const isSameDay = (date1, date2) => {
  return date1.getDate() === date2.getDate() &&
         date1.getMonth() === date2.getMonth() &&
         date1.getFullYear() === date2.getFullYear()
}

// Определение активности бронирования
const isActiveBooking = (booking) => {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const bookingDate = new Date(booking.booking_date)
  const bookingDateOnly = new Date(bookingDate.getFullYear(), bookingDate.getMonth(), bookingDate.getDate())
  
  // Активное, если не отменено и дата сегодня или в будущем
  return booking.status_name !== 'cancelled' && bookingDateOnly >= today
}

// Проверка есть ли активные бронирования в списке
const hasActiveBookings = (bookings) => {
  return bookings.some(booking => isActiveBooking(booking))
}

// Проверка активных бронирований в конкретном дне (для CSS классов)
const hasActiveBookingsForDay = (day) => {
  return getFilteredBookingsForDate(day.date).some(booking => isActiveBooking(booking))
}

// Проверка неактивных бронирований в конкретном дне (для CSS классов)
const hasInactiveBookingsForDay = (day) => {
  return getFilteredBookingsForDate(day.date).some(booking => !isActiveBooking(booking))
}

// Получение отфильтрованных бронирований для конкретной даты
const getFilteredBookingsForDate = (date) => {
  const filteredBookings = calendarBookings.value.filter(booking => {
    const bookingDate = new Date(booking.booking_date)
    return isSameDay(bookingDate, date)
  })
  
  return filteredBookings
}

// Получение текста для индикатора бронирования в зависимости от типа бронирований
const getBookingIndicatorText = (bookings) => {
  const activeBookings = bookings.filter(booking => isActiveBooking(booking))
  const inactiveBookings = bookings.filter(booking => !isActiveBooking(booking))
  
  if (activeBookings.length > 0 && inactiveBookings.length > 0) {
    return `${activeBookings.length}акт./${inactiveBookings.length}прош.`
  } else if (activeBookings.length > 0) {
    return activeBookings.length === 1 ? 'Бронь' : `${activeBookings.length} бронирования`
  } else if (inactiveBookings.length > 0) {
    return inactiveBookings.length === 1 ? 'Прошедшее' : `${inactiveBookings.length} прошедших`
  } else {
    return 'Бронь'
  }
}

// Методы для управления расширенным днем
const expandDay = (day) => {
  // Очищаем таймер отложенного скрытия
  if (collapseTimeout) {
    clearTimeout(collapseTimeout)
    collapseTimeout = null
  }
  
  // Получаем отфильтрованные бронирования для этой даты
  day.allBookings = getFilteredBookingsForDate(day.date)
  expandedDay.value = day
}

const collapseDay = () => {
  // Запускаем таймер для отложенного скрытия (300мс)
  collapseTimeout = setTimeout(() => {
    expandedDay.value = null
    collapseTimeout = null
  }, 300)
}

// Получение отсортированных бронирований для расширенного дня
const getSortedBookingsForExpandedDay = (day) => {
  const bookings = day.allBookings || day.bookings
  return [...bookings].sort((a, b) => {
    // Сначала активные (не отмененные и в будущем)
    const aIsActive = isActiveBooking(a)
    const bIsActive = isActiveBooking(b)
    
    if (aIsActive && !bIsActive) return -1
    if (!aIsActive && bIsActive) return 1
    
    // Если оба активных или оба неактивных, сортируем по времени создания (новые сверху)
    return new Date(b.created_at || b.updated_at || b.booking_date) - new Date(a.created_at || a.updated_at || a.booking_date)
  })
}

// Получение ограниченного списка бронирований для отображения
const getLimitedBookingsForExpandedDay = (day, limit = 2) => {
  const sortedBookings = getSortedBookingsForExpandedDay(day)
  return sortedBookings.slice(0, limit)
}

// Форматирование даты для tooltip
const formatTooltipDate = (date) => {
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

// Навигация по календарю
const previousMonth = () => {
  currentDate.value = new Date(currentYear.value, currentMonth.value - 1, 1)
}

const nextMonth = () => {
  currentDate.value = new Date(currentYear.value, currentMonth.value + 1, 1)
}

const goToToday = () => {
  currentDate.value = new Date()
}

// Загрузка данных пользователя
const loadUserData = async () => {
  try {
    loading.value = true
    await Promise.all([
      loadUserBookings(),
      loadBookingStats()
    ])
  } catch (error) {
    console.error('Ошибка загрузки данных пользователя:', error)
  } finally {
    loading.value = false
  }
}

// Загрузка бронирований пользователя
const loadUserBookings = async () => {
  try {
    // Загружаем все бронирования, включая прошедшие, для корректного отображения в календаре
    const bookings = await bookingsAPI.getBookingsByAccount(authStore.user.id, true)
    userBookings.value = bookings
  } catch (error) {
    console.error('Ошибка загрузки бронирований:', error)
  }
}

// Загрузка статистики
const loadBookingStats = async () => {
  try {
    const bookingsStats = await bookingsAPI.getBookingsStats()
    stats.value = {
      totalBookings: bookingsStats.total_bookings || 0,
      todayBookings: bookingsStats.today_bookings || 0,
      upcomingBookings: bookingsStats.upcoming_bookings || 0
    }
  } catch (error) {
    console.error('Ошибка загрузки статистики:', error)
  }
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

// Форматирование даты создания
const formatCreatedDate = (dateString) => {
  if (!dateString) return 'Неизвестно'
  
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) {
    return 'Сегодня'
  } else if (diffDays === 1) {
    return 'Вчера'
  } else if (diffDays < 7) {
    return `${diffDays} дн. назад`
  } else {
    return date.toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'short'
    })
  }
}

// Получение отображаемого имени статуса
const getStatusDisplayName = (statusName) => {
  switch (statusName?.toLowerCase()) {
    case 'confirmed': return 'Подтверждено'
    case 'cancelled': return 'Отменено'
    case 'pending': return 'Ожидает подтверждения'
    default: return statusName || 'Неизвестно'
  }
}

// Получение CSS класса для строки таблицы
const getBookingRowClass = (booking) => {
  const date = new Date(booking.booking_date)
  const today = new Date()
  const todayStart = new Date(today.getFullYear(), today.getMonth(), today.getDate())
  
  if (booking.status_name === 'cancelled') {
    return 'cancelled-booking'
  } else if (date >= todayStart) {
    return 'upcoming-booking'
  } else {
    return 'past-booking'
  }
}

// Получение строки текущей даты в формате YYYY-MM-DD
const getTodayDateString = () => {
  const today = new Date()
  return today.toISOString().split('T')[0]
}

// Обработчики событий
const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

const goToBooking = () => {
  const todayString = getTodayDateString()
  router.push(`/booking?date=${todayString}`)
}

const goToProfile = () => {
  router.push('/profile')
}

const goToBookingDate = (date) => {
  // Форматируем дату в формат YYYY-MM-DD для передачи в URL
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const formattedDate = `${year}-${month}-${day}`
  
  // Переходим на страницу выбора помещения с предустановленной датой
  router.replace(`/booking?date=${formattedDate}`)
}

const goToAdmin = () => {
  router.push('/admin')
}
</script>

<style scoped>
.dashboard-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.dashboard-container {
  min-height: 100vh;
  padding: 8rem 20px 20px 20px;
  position: relative;
  z-index: 10;
}

.dashboard-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.welcome-section {
  text-align: center;
  margin-bottom: 1rem;
}

.welcome-section h2 {
  color: white;
  margin-bottom: 0.5rem;
  font-size: 2rem;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.welcome-section p {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.1rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* Главная секция с разделением на колонки */
.main-section {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  min-height: 600px;
}

.left-column {
  display: flex;
  flex-direction: column;
}

.right-column {
  background: white;
  border-radius: 16px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  overflow: hidden;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* Список функций в один столбец */
.features-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.feature-card {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.feature-card.clickable {
  cursor: pointer;
}

.feature-card.clickable:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  background-color: rgba(255, 255, 255, 0.95);
}

.feature-card.admin-card {
  border-left: 4px solid #ff6b35;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 245, 243, 0.9) 100%);
}

.feature-card.admin-card:hover {
  background: linear-gradient(135deg, rgba(248, 249, 250, 0.95) 0%, rgba(255, 232, 224, 0.95) 100%);
}

.feature-card h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.2rem;
  font-weight: 600;
}

.feature-card p {
  margin: 0;
  color: #6b7280;
  line-height: 1.5;
  font-size: 0.95rem;
}

.feature-action {
  margin-top: auto;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.feature-card.clickable .feature-action:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 25px -5px rgba(102, 126, 234, 0.4);
}

.admin-card .feature-action {
  background: linear-gradient(135deg, #ff6b35 0%, #e55a2b 100%);
}

.admin-card.clickable .feature-action:hover {
  box-shadow: 0 10px 25px -5px rgba(255, 107, 53, 0.4);
}

/* Фоновая декорация */
.dashboard-page::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none;
}

.dashboard-page .floating-shapes {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none;
}

.dashboard-page .shape {
  position: absolute;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  animation: float 6s ease-in-out infinite;
}

.dashboard-page .shape-1 {
  width: 80px;
  height: 80px;
  top: 20%;
  left: 10%;
  animation-delay: 0s;
}

.dashboard-page .shape-2 {
  width: 120px;
  height: 120px;
  top: 60%;
  right: 10%;
  animation-delay: 2s;
}

.dashboard-page .shape-3 {
  width: 60px;
  height: 60px;
  bottom: 20%;
  left: 20%;
  animation-delay: 4s;
}

.dashboard-page .shape-4 {
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

/* Секция календаря */
.calendar-section {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.calendar-header {
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.calendar-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.3rem;
  font-weight: 600;
}

.booking-count {
  color: #666;
  font-size: 0.9rem;
  font-weight: 500;
}

.calendar-controls {
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.calendar-navigation {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nav-btn {
  padding: 0.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.current-month {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  min-width: 150px;
  text-align: center;
}

.today-btn {
  padding: 0.5rem 1rem;
  background: #f8f9fa;
  color: #667eea;
  border: 2px solid #667eea;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.85rem;
  font-weight: 500;
}

.today-btn:hover {
  background: #667eea;
  color: white;
  transform: translateY(-1px);
}

.calendar-filters {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 0.5rem 1rem;
  background: #f8f9fa;
  color: #666;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.8rem;
  font-weight: 500;
}

.filter-btn:hover {
  border-color: #667eea;
  color: #667eea;
  background: rgba(102, 126, 234, 0.05);
}

.filter-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* Календарная сетка */
.calendar-container {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
}

.calendar-grid {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  margin-bottom: 0.25rem;
}

.weekday {
  text-align: center;
  font-weight: 600;
  color: #667eea;
  font-size: 0.75rem;
  padding: 0.25rem;
}

.calendar-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
}

.calendar-day {
  min-height: 90px;
  border: 2px solid #e0e0e0;
  border-radius: 4px;
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  position: relative;
  transition: all 0.3s ease;
  background: #fafafa;
}

.calendar-day.current-week {
  background: white;
  border: 2px solid #667eea;
  min-height: 125px;
}

.calendar-day.clickable-day {
  cursor: pointer;
}

.calendar-day.current-week:hover {
  transform: scale(1.02);
  box-shadow: 0 10px 25px rgba(102, 126, 234, 0.2);
  z-index: 15;
}

.calendar-day.clickable-day:hover {
  border-color: #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
  transform: translateY(-1px);
  z-index: 10;
}

.calendar-day.other-month.clickable-day:hover {
  border-color: #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.05);
  transform: translateY(-1px);
  background: #fafafa;
}

.calendar-day.other-month {
  opacity: 0.2;
  background: #f9f9f9;
}

.calendar-day.today {
  border: 5px solid #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  min-height: 125px;
}

.calendar-day.has-active-bookings {
  border-color: #10b981;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%);
}

.calendar-day.current-week.has-active-bookings {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(16, 185, 129, 0.1) 100%);
}

.calendar-day.has-inactive-bookings {
  border-color: #9ca3af;
  background: linear-gradient(135deg, rgba(156, 163, 175, 0.1) 0%, rgba(156, 163, 175, 0.05) 100%);
}

.calendar-day.current-week.has-inactive-bookings {
  background: linear-gradient(135deg, rgba(156, 163, 175, 0.15) 0%, rgba(156, 163, 175, 0.1) 100%);
}

.day-number {
  font-weight: 600;
  font-size: 0.7rem;
  color: #333;
  margin-bottom: 0.1rem;
}

.calendar-day.current-week .day-number {
  font-size: 0.8rem;
}

.calendar-day.other-month .day-number {
  color: #9ca3af;
}

.calendar-day.today .day-number {
  color: #667eea;
}

.bookings-indicators {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  justify-content: flex-end;
}

.calendar-day.current-week .bookings-indicators {
  gap: 3px;
}

.booking-info {
  padding: 2px 4px;
  border-radius: 3px;
  font-size: 0.65rem;
  line-height: 1.2;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid transparent;
}

.calendar-day.current-week .booking-info {
  padding: 3px 6px;
  font-size: 0.7rem;
  background: rgba(16, 185, 129, 0.15);
  border-color: #10b981;
  color: #065f46;
}

.booking-info.active {
  background: rgba(16, 185, 129, 0.15);
  border-color: #10b981;
  color: #065f46;
}

.booking-info.inactive {
  background: rgba(107, 114, 128, 0.15);
  border-color: #6b7280;
  color: #4b5563;
}

.booking-name {
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.calendar-day:not(.current-week) .booking-name {
  font-size: 0.6rem;
}

.booking-room {
  font-size: 0.55rem;
  opacity: 0.8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: 1px;
}

.calendar-day.current-week .booking-room {
  font-size: 0.6rem;
}

.booking-count {
  font-size: 0.6rem;
  color: #666;
  text-align: center;
  font-weight: 500;
  background: rgba(102, 126, 234, 0.1);
  padding: 1px 3px;
  border-radius: 2px;
}

.calendar-day.current-week .booking-count {
  font-size: 0.65rem;
  padding: 2px 4px;
}

.booking-indicator {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid #10b981;
  border-radius: 4px;
  padding: 3px 6px;
  font-size: 0.65rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  min-height: 20px;
  justify-content: center;
}

.calendar-day.current-week .booking-indicator {
  padding: 4px 8px;
  font-size: 0.7rem;
  min-height: 24px;
}

.booking-indicator.has-active {
  background: rgba(16, 185, 129, 0.15);
  border-color: #10b981;
  color: #065f46;
}

.booking-indicator.no-active {
  background: rgba(107, 114, 128, 0.15);
  border-color: #6b7280;
  color: #4b5563;
}

.booking-indicator:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 20;
}

.booking-text {
  font-weight: 600;
  margin-bottom: 1px;
}

.booking-details {
  font-size: 0.85em;
  opacity: 0.9;
  font-weight: 500;
  margin-top: 1px;
}

.room-name {
  font-weight: normal;
  opacity: 0.8;
}

.booking-ellipsis {
  font-size: 1.2em;
  font-weight: bold;
  line-height: 1;
}

.expanded-bookings {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 20;
  margin-top: 2px;
  padding: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.expanded-content {
  max-height: 150px;
  overflow-y: auto;
}

.expanded-booking {
  padding: 4px 0;
  border-bottom: 1px solid #f5f5f5;
  font-size: 0.7rem;
}

.expanded-booking:last-child {
  border-bottom: none;
}

.expanded-booking.active {
  color: #065f46;
}

.expanded-booking.inactive {
  color: #4b5563;
}

.expanded-booking .booking-workspace {
  font-weight: 600;
  margin-bottom: 1px;
}

.expanded-booking .workspace-room {
  font-weight: normal;
  opacity: 0.8;
}

.expanded-booking .booking-status {
  font-size: 0.65rem;
  opacity: 0.7;
  font-style: italic;
}

.more-bookings-indicator {
  padding: 4px 0;
  text-align: center;
  font-size: 0.7rem;
  color: #666;
  font-style: italic;
  border-top: 1px solid #f0f0f0;
  margin-top: 2px;
  padding-top: 6px;
}

.booking-hint {
  padding: 1rem 3rem;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  border-top: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 0 0 16px 16px;
  text-align: center;
}

.booking-hint p {
  margin: 0;
  color: #667eea;
  font-size: 1rem;
  font-weight: 500;
  line-height: 1.4;
}

.hint-icon {
  font-size: 1.2rem;
  margin-right: 0.5rem;
  display: inline-block;
}

.booking-hint .features-list {
  flex-direction: row;
  gap: 0.75rem;
  margin-top: 1.5rem;
  justify-content: center;
}

.booking-hint .feature-card {
  padding: 0.75rem;
  min-height: 60px;
  width: 200px;
  flex-shrink: 0;
  font-size: 0.85rem;
}

.booking-hint .feature-action {
  padding: 0.4rem 0.75rem;
  font-size: 0.75rem;
}

.booking-hint .feature-card.admin-card {
  width: 220px;
}

@media (max-width: 768px) {
  .booking-hint {
    padding: 1.5rem 1rem;
  }
  
  .booking-hint p {
    font-size: 0.95rem;
  }
}

.create-booking-btn {
  padding: 0.75rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.create-booking-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
  background: linear-gradient(135deg, #7c8cf0 0%, #8a5fb8 100%);
}

@media (max-width: 1200px) {
  .main-section {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .right-column {
    order: -1;
  }
  
  .features-list {
    flex-direction: row;
    overflow-x: auto;
    padding-bottom: 1rem;
  }
  
  .feature-card {
    min-width: 280px;
    flex-shrink: 0;
  }
  
  .calendar-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .calendar-navigation {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 10px;
  }
    
  .welcome-section h2 {
    font-size: 1.5rem;
  }
  
  .features-list {
    flex-direction: column;
  }
  
  .feature-card {
    min-width: unset;
  }
  
  .calendar-header {
    padding: 1rem;
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }
  
  .calendar-controls {
    padding: 1rem;
  }
  
  .calendar-navigation {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .current-month {
    font-size: 1rem;
  }
  
  .calendar-filters {
    justify-content: center;
  }
  
  .filter-btn {
    padding: 0.4rem 0.8rem;
    font-size: 0.75rem;
  }
  
  .calendar-container {
    padding: 1rem;
  }
  
  .calendar-day {
    padding: 0.25rem;
    min-height: 35px;
  }
  
  .calendar-day.current-week {
    min-height: 40px;
  }
  
  .day-number {
    font-size: 0.7rem;
  }
  
  .calendar-day.current-week .day-number {
    font-size: 0.75rem;
  }
  
  .bookings-indicators {
    gap: 1px;
  }
  
  .calendar-day.current-week .bookings-indicators {
    gap: 2px;
  }
  
  .booking-info {
    padding: 1px 3px;
    font-size: 0.6rem;
  }
  
  .calendar-day.current-week .booking-info {
    padding: 2px 4px;
    font-size: 0.65rem;
  }
  
  .booking-name {
    font-size: 0.55rem;
  }
  
  .calendar-day.current-week .booking-name {
    font-size: 0.6rem;
  }
  
  .booking-room {
    font-size: 0.5rem;
  }
  
  .calendar-day.current-week .booking-room {
    font-size: 0.55rem;
  }
  
  .booking-count {
    font-size: 0.55rem;
    padding: 1px 2px;
  }
  
  .calendar-day.current-week .booking-count {
    font-size: 0.6rem;
    padding: 1px 3px;
  }
  
  .expanded-bookings {
    max-height: 150px;
    padding: 6px;
  }
  
  .expanded-booking {
    font-size: 0.65rem;
  }
  
  .expanded-booking .booking-workspace {
    font-size: 0.7rem;
  }
  
  .expanded-booking .booking-status {
    font-size: 0.6rem;
  }
  
  .more-bookings-indicator {
    font-size: 0.65rem;
    padding: 3px 0;
    padding-top: 5px;
  }
}
</style>