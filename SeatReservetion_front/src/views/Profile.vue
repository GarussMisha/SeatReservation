<template>
<div class="profile-page">
  <!-- Фоновая декорация -->
  <div class="background-decoration">
    <div class="floating-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
      <div class="shape shape-4"></div>
    </div>
  </div>

  <div class="profile-container">
    <!-- Заголовок перемещен в глобальный компонент Header -->

    <main class="profile-content">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Загрузка данных профиля...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <svg class="error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
        </svg>
        <h3>Ошибка загрузки</h3>
        <p>{{ error }}</p>
        <button @click="loadProfileData" class="retry-btn">Повторить</button>
      </div>

      <div v-else class="profile-sections">
        <!-- Информация о пользователе -->
        <section class="profile-section user-info">
          <div class="section-header">
            <h2>
              <svg class="section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
              Личная информация
            </h2>
          </div>
          
          <div class="user-avatar">
            <div class="avatar-circle">
              {{ getInitials() }}
            </div>
            <div class="avatar-status">
              <span :class="['status-badge', user?.status_name?.toLowerCase() || 'active']">
                {{ getStatusDisplayName() }}
              </span>
            </div>
          </div>

          <div class="info-grid">
                      <div class="info-item">
                        <label>Имя *</label>
                        <div class="info-value">{{ user?.first_name || 'Не указано' }}</div>
                      </div>
                      
                      <div class="info-item">
                        <label>Фамилия *</label>
                        <div class="info-value">{{ user?.last_name || 'Не указано' }}</div>
                      </div>
                      
                      <div class="info-item">
                        <label>Отчество</label>
                        <div class="info-value">{{ user?.middle_name || 'Не указано' }}</div>
                      </div>
                      
                      <div class="info-item">
                        <label>Логин *</label>
                        <div class="info-value">{{ user?.login || 'Не указано' }}</div>
                      </div>
                      
                      <div class="info-item">
                        <label>Email</label>
                        <div class="info-value">
                          <a v-if="user?.email" :href="`mailto:${user.email}`" class="email-link">
                            {{ user.email }}
                          </a>
                          <span v-else>Не указан</span>
                        </div>
                      </div>
                      
                      <div class="info-item">
                        <label>Телефон</label>
                        <div class="info-value">
                          <a v-if="user?.phone" :href="`tel:${user.phone}`" class="phone-link">
                            {{ user.phone }}
                          </a>
                          <span v-else>Не указан</span>
                        </div>
                      </div>
                      
                      <div class="info-item">
                        <label>Дата рождения</label>
                        <div class="info-value">
                          {{ formatBirthDate() || 'Не указана' }}
                        </div>
                      </div>
                      
                      <div class="info-item">
                        <label>Роль</label>
                        <div class="info-value">
                          <span :class="['role-badge', user?.is_admin ? 'admin' : 'user']">
                            {{ user?.is_admin ? 'Администратор' : 'Пользователь' }}
                          </span>
                        </div>
                      </div>
                    </div>
        </section>

        <!-- Статистика -->
        <section class="profile-section statistics">
          <div class="section-header">
            <h2>
              <svg class="section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
              </svg>
              Статистика использования
            </h2>
          </div>

          <div class="stats-grid">
            <div class="stat-card">
              <svg class="stat-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
              </svg>
              <div class="stat-content">
                <div class="stat-number">{{ user?.booking_count || 0 }}</div>
                <div class="stat-label">Всего бронирований</div>
              </div>
            </div>

            <div class="stat-card">
              <svg class="stat-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
              </svg>
              <div class="stat-content">
                <div class="stat-number">{{ getUpcomingBookingsCount() }}</div>
                <div class="stat-label">Предстоящих</div>
              </div>
            </div>

            <div class="stat-card">
              <svg class="stat-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <div class="stat-content">
                <div class="stat-number">{{ getCompletedBookingsCount() }}</div>
                <div class="stat-label">Завершенных</div>
              </div>
            </div>

            <div class="stat-card">
              <svg class="stat-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <div class="stat-content">
                <div class="stat-number">{{ getAccountAge() }}</div>
                <div class="stat-label">Дней в системе</div>
              </div>
            </div>
          </div>
        </section>

        <!-- Информация об аккаунте -->
        <section class="profile-section account-info">
          <div class="section-header">
            <h2>
              <svg class="section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
              </svg>
              Информация об аккаунте
            </h2>
          </div>
          
          <div class="info-grid">
            <div class="info-item">
              <label>ID пользователя</label>
              <div class="info-value">{{ user?.id || 'Неизвестно' }}</div>
            </div>
            
            <div class="info-item">
              <label>Дата регистрации</label>
              <div class="info-value">{{ formatDate() }}</div>
            </div>
            
            <div class="info-item">
              <label>Последнее бронирование</label>
              <div class="info-value">
                {{ formatLastBookingDate() || 'Нет бронирований' }}
              </div>
            </div>
            
            <div class="info-item">
              <label>Статус аккаунта</label>
              <div class="info-value">
                <span :class="['status-badge', user?.status_name?.toLowerCase() || 'active']">
                  {{ getStatusDisplayName() }}
                </span>
              </div>
            </div>
          </div>
        </section>

      </div>
    </main>
  </div>
</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import { authAPI, bookingsAPI } from '../services/api'

const authStore = useAuthStore()
const router = useRouter()

// Состояние
const user = ref(null)
const userBookings = ref([])
const loading = ref(false)
const error = ref(null)

// Загрузка данных профиля
const loadProfileData = async () => {
  loading.value = true
  error.value = null
  
  try {
    const userData = await authAPI.getCurrentUser()
    user.value = userData
    
    // Загружаем бронирования пользователя для статистики
    if (authStore.user) {
      await loadUserBookings()
    }
  } catch (err) {
    console.error('Ошибка загрузки профиля:', err)
    error.value = err.response?.data?.detail || 'Не удалось загрузить данные профиля'
  } finally {
    loading.value = false
  }
}

// Загрузка бронирований пользователя
const loadUserBookings = async () => {
  try {
    const bookings = await bookingsAPI.getBookingsByAccount(authStore.user.id, false)
    userBookings.value = bookings
  } catch (err) {
    console.error('Ошибка загрузки бронирований:', err)
    // Не блокируем профиль, если не удалось загрузить бронирования
  }
}

// Вспомогательные методы
const getInitials = () => {
  if (!user.value) return 'U'
  const firstName = user.value.first_name || ''
  const lastName = user.value.last_name || ''
  return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase() || 'U'
}

const getStatusDisplayName = () => {
  if (!user.value?.status_name) return 'Активен'
  
  const statusMap = {
    'active': 'Активен',
    'inactive': 'Неактивен',
    'pending': 'Ожидает подтверждения',
    'confirmed': 'Подтвержден',
    'cancelled': 'Отменен'
  }
  
  return statusMap[user.value.status_name.toLowerCase()] || user.value.status_name
}

const formatDate = () => {
  if (!user.value?.created_at) return 'Неизвестно'
  
  const date = new Date(user.value.created_at)
  return date.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatBirthDate = () => {
  if (!user.value?.birth_date) return null
  
  const date = new Date(user.value.birth_date)
  return date.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const formatLastBookingDate = () => {
  if (!user.value?.last_booking_date) return null
  
  const date = new Date(user.value.last_booking_date)
  return date.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getUpcomingBookingsCount = () => {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  
  return userBookings.value.filter(booking => {
    const bookingDate = new Date(booking.booking_date)
    const bookingDateOnly = new Date(bookingDate.getFullYear(), bookingDate.getMonth(), bookingDate.getDate())
    
    // Предстоящее бронирование: не отменено и дата в будущем или сегодня
    return booking.status_name !== 'cancelled' && bookingDateOnly >= today
  }).length
}

const getCompletedBookingsCount = () => {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  
  return userBookings.value.filter(booking => {
    const bookingDate = new Date(booking.booking_date)
    const bookingDateOnly = new Date(bookingDate.getFullYear(), bookingDate.getMonth(), bookingDate.getDate())
    
    // Завершенное бронирование: отменено или дата в прошлом
    return bookingDateOnly < today || booking.status_name === 'cancelled'
  }).length
}

const getAccountAge = () => {
  if (!user.value?.created_at) return 0
  
  const createdDate = new Date(user.value.created_at)
  const now = new Date()
  const diffTime = Math.abs(now - createdDate)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  return diffDays
}


// Навигация
const goToDashboard = () => {
  router.push('/dashboard')
}

const goToAdmin = () => {
  router.push('/admin')
}

const refreshProfileData = async () => {
  await loadProfileData()
}

// Инициализация
onMounted(() => {
  if (authStore.user) {
    user.value = authStore.user
  }
  loadProfileData()
})
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.profile-container {
  min-height: 100vh;
  padding: 0 20px 20px 20px;
  position: relative;
  z-index: 10;
  margin-top: 0;
}

.profile-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  padding-top: 8rem;
}

.loading-state, .error-state {
  background: white;
  padding: 3rem 2rem;
  border-radius: 16px;
  text-align: center;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-state h3 {
  color: #e74c3c;
  margin-bottom: 0.5rem;
}

.retry-btn {
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

/* Секции профиля */
.profile-sections {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.profile-section {
  background: white;
  border-radius: 16px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  overflow: hidden;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.section-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #eee;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
}

.section-header h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.section-icon,
.error-icon {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}

.stat-icon-svg {
  width: 32px;
  height: 32px;
  color: var(--primary-start);
  opacity: 0.8;
}

.icon {
  font-size: 1.2rem;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-avatar {
  padding: 2rem;
  text-align: center;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
}

.avatar-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 auto 1rem;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
}

.avatar-status {
  margin-top: 1rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  padding: 2rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-item label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-size: 1rem;
  color: #333;
  font-weight: 500;
}

.email-link, .phone-link {
  color: #667eea;
  text-decoration: none;
  transition: color 0.3s ease;
}

.email-link:hover, .phone-link:hover {
  color: #764ba2;
  text-decoration: underline;
}

/* Бейджи */
.status-badge, .role-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.active {
  background: #d4edda;
  color: #155724;
}

.status-badge.inactive {
  background: #f8d7da;
  color: #721c24;
}

.status-badge.pending {
  background: #fff3cd;
  color: #856404;
}

.status-badge.confirmed {
  background: #d1ecf1;
  color: #0c5460;
}

.status-badge.cancelled {
  background: #f8d7da;
  color: #721c24;
}

.role-badge.admin {
  background: linear-gradient(135deg, #ff6b35 0%, #e55a2b 100%);
  color: white;
}

.role-badge.user {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

/* Статистика */
.statistics {
  padding: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  padding: 2rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  border-radius: 12px;
  border: 1px solid rgba(102, 126, 234, 0.1);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
}

.stat-icon {
  font-size: 2rem;
  opacity: 0.8;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: #333;
  line-height: 1;
}

.stat-label {
  font-size: 0.85rem;
  color: #666;
  margin-top: 0.25rem;
}

.actions {
  padding: 0;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  padding: 2rem;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  font-weight: 500;
  color: #333;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.action-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: #667eea;
}

.action-btn.primary:hover {
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.action-btn.admin {
  background: linear-gradient(135deg, #ff6b35 0%, #e55a2b 100%);
  color: white;
  border-color: #ff6b35;
}

.action-btn.admin:hover {
  box-shadow: 0 8px 25px rgba(255, 107, 53, 0.4);
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  background: white;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-input::placeholder {
  color: #9ca3af;
}

.form-input.error {
  border-color: #e74c3c;
  box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.1);
}

.error-message {
  color: #e74c3c;
  font-size: 0.75rem;
  margin-top: 0.25rem;
  display: block;
}

.action-icon {
  font-size: 1.1rem;
}

/* Фоновая декорация */
.profile-page::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none;
}

.profile-page .floating-shapes {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none;
}

.profile-page .shape {
  position: absolute;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  animation: float 6s ease-in-out infinite;
}

.profile-page .shape-1 {
  width: 80px;
  height: 80px;
  top: 20%;
  left: 10%;
  animation-delay: 0s;
}

.profile-page .shape-2 {
  width: 120px;
  height: 120px;
  top: 60%;
  right: 10%;
  animation-delay: 2s;
}

.profile-page .shape-3 {
  width: 60px;
  height: 60px;
  bottom: 20%;
  left: 20%;
  animation-delay: 4s;
}

.profile-page .shape-4 {
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

/* Адаптивность */
@media (max-width: 768px) {
  .profile-container {
    padding: 0 10px 10px 10px;
  }
  
  .profile-content {
    padding-top: 6rem;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
    padding: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 0.75rem;
    padding: 1rem;
  }
  
  .stat-card {
    padding: 1rem;
  }
  
  .actions-grid {
    grid-template-columns: 1fr;
    gap: 0.75rem;
    padding: 1rem;
  }
  
  .user-avatar {
    padding: 1.5rem;
  }
  
  .avatar-circle {
    width: 60px;
    height: 60px;
    font-size: 1.2rem;
  }
}
</style>