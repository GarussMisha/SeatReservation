<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-card">
        <!-- Лого и заголовок -->
        <div class="login-header">
          <div class="logo">
            <svg class="w-12 h-12 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
            </svg>
          </div>
          <h1 class="login-title">Вход в систему</h1>
        </div>

        <!-- Форма входа -->
        <form @submit.prevent="handleLogin" class="login-form">
          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>

          <div class="form-group">
            <label for="login" class="form-label">
              Логин или Email
            </label>
            <input
              type="text"
              id="login"
              v-model="login"
              class="form-input"
              :class="{ 'error': loginError }"
              placeholder="Введите логин или email адрес"
              required
            />
            <p v-if="loginError" class="field-error">{{ loginError }}</p>
          </div>

          <div class="form-group">
            <label for="password" class="form-label">
              Пароль
            </label>
            <div class="password-container">
              <input
                :type="showPassword ? 'text' : 'password'"
                id="password"
                v-model="password"
                class="form-input password-input"
                :class="{ 'error': passwordError }"
                placeholder="Введите пароль"
                @input="clearFieldError('password')"
                required
              />
              <button
                type="button"
                @click="togglePassword"
                class="password-toggle"
              >
                <svg v-if="showPassword" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"/>
                </svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
              </button>
            </div>
            <p v-if="passwordError" class="field-error">{{ passwordError }}</p>
          </div>

          <div class="form-options">
            <a href="#" class="forgot-password" @click.prevent="showForgotPasswordModal">Забыли пароль?</a>
          </div>

          <!-- Модальное окно для восстановления пароля -->
          <div v-if="showModal" class="modal-overlay" @click="closeModal">
            <div class="modal-content" @click.stop>
              <div class="modal-header">
                <h3>Восстановление пароля</h3>
                <button @click="closeModal" class="close-button">&times;</button>
              </div>
              <div class="modal-body">
                <p>Жаль, что вы забыли пароль)</p>
                <p>Обратитесь к администратору системы для восстановления доступа.</p>
              </div>
              <div class="modal-footer">
                <button @click="closeModal" class="modal-button">Понятно</button>
              </div>
            </div>
          </div>

          <button 
            type="submit" 
            class="login-button"
            :disabled="isLoading"
          >
            <div v-if="isLoading" class="loading-spinner"></div>
            <span v-else>Войти в систему</span>
          </button>
        </form>

        <!-- Дополнительная информация -->
        <div class="login-footer">
          <p class="version-info">
            SeatReservation v1.0
          </p>
        </div>
      </div>
    </div>

    <!-- Фоновая декорация -->
    <div class="background-decoration">
      <div class="floating-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
        <div class="shape shape-4"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// Реактивные данные
const login = ref('')
const password = ref('')
const showPassword = ref(false)
const showModal = ref(false)
const errorMessage = ref('')
const loginError = ref('')
const passwordError = ref('')

// Computed properties для auth store
const isLoading = computed(() => authStore.isLoading)
const error = computed(() => authStore.error)

// Переключение видимости пароля
const togglePassword = () => {
  showPassword.value = !showPassword.value
}

// Валидация полей
const validateForm = () => {
  let isValid = true
  
  // Валидация логина/email
  if (!login.value) {
    loginError.value = 'Логин или email обязателен для заполнения'
    isValid = false
  } else {
    // Если содержит @, проверяем как email
    if (login.value.includes('@')) {
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(login.value)) {
        loginError.value = 'Введите корректный email адрес'
        isValid = false
      } else {
        loginError.value = ''
      }
    } else {
      // Иначе считаем это логином (минимум 3 символа)
      if (login.value.length < 3) {
        loginError.value = 'Логин должен содержать минимум 3 символа'
        isValid = false
      } else {
        loginError.value = ''
      }
    }
  }
  
  // Валидация пароля
  if (!password.value) {
    passwordError.value = 'Пароль обязателен для заполнения'
    isValid = false
  } else if (password.value.length < 6) {
    passwordError.value = 'Пароль должен содержать минимум 6 символов'
    isValid = false
  } else {
    passwordError.value = ''
  }
  
  return isValid
}

// Обработка входа
const handleLogin = async () => {
  errorMessage.value = ''
  authStore.clearError()
  
  if (!validateForm()) {
    return
  }
  
  try {
    await authStore.login(login.value, password.value)
    // Явный редирект на дашборд после успешного входа
    router.push('/dashboard')
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || error.message || 'Ошибка авторизации. Проверьте введенные данные.'
  }
}

// Модальное окно для восстановления пароля
const showForgotPasswordModal = () => {
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

// Очистка ошибок при изменении полей
const clearFieldError = (field) => {
  if (field === 'login') {
    loginError.value = ''
  } else if (field === 'password') {
    passwordError.value = ''
  }
}

// Инициализация
onMounted(async () => {
  // Проверяем, не авторизован ли уже пользователь
  await authStore.checkAuth()
  if (authStore.isAuthenticated) {
    router.push('/dashboard')
  }
})
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.login-container {
  width: 100%;
  max-width: 400px;
  z-index: 10;
  position: relative;
}

.login-card {
  background: white;
  border-radius: 20px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  padding: 40px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.logo {
  margin: 0 auto 20px;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.login-title {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 8px;
}

.login-subtitle {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.login-form {
  margin-bottom: 30px;
}

.error-message {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  font-size: 14px;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: flex;
  align-items: center;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 14px;
  transition: all 0.2s;
  background: #f9fafb;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-input.error {
  border-color: #dc2626;
  background: #fef2f2;
}

.password-container {
  position: relative;
}

.password-input {
  padding-right: 45px;
}

.password-toggle {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: color 0.2s;
}

.password-toggle:hover {
  color: #374151;
}

.field-error {
  color: #dc2626;
  font-size: 12px;
  margin-top: 4px;
  margin-left: 4px;
}

.form-options {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 25px;
}

.forgot-password {
  font-size: 14px;
  color: #667eea;
  text-decoration: none;
  transition: color 0.2s;
}

.forgot-password:hover {
  color: #4f46e5;
  text-decoration: underline;
}

.login-button {
  width: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 14px 20px;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
}

.login-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 10px 25px -5px rgba(102, 126, 234, 0.4);
}

.login-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.login-footer {
  text-align: center;
  border-top: 1px solid #e5e7eb;
  padding-top: 20px;
  margin-top: 20px;
}


.version-info {
  font-size: 11px;
  color: #9ca3af;
  margin: 0;
}

.background-decoration {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none;
}

.floating-shapes {
  position: relative;
  width: 100%;
  height: 100%;
}

.shape {
  position: absolute;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  animation: float 6s ease-in-out infinite;
}

.shape-1 {
  width: 80px;
  height: 80px;
  top: 20%;
  left: 10%;
  animation-delay: 0s;
}

.shape-2 {
  width: 120px;
  height: 120px;
  top: 60%;
  right: 10%;
  animation-delay: 2s;
}

.shape-3 {
  width: 60px;
  height: 60px;
  bottom: 20%;
  left: 20%;
  animation-delay: 4s;
}

.shape-4 {
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

.login-page,
.login-page * {
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;

  border-radius: 20px;
  padding: 40px;
  backdrop-filter: blur(10px);
}

.modal-content {
  background: white;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  animation: slideIn 0.3s ease;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  color: #6b7280;
  cursor: pointer;
  padding: 4px;
  line-height: 1;
  transition: color 0.2s;
}

.close-button:hover {
  color: #374151;
}

.modal-body {
  padding: 24px;
  text-align: center;
}

.modal-body p {
  margin: 0 0 12px 0;
  color: #4b5563;
  line-height: 1.5;
}

.modal-body p:last-child {
  margin-bottom: 0;
  font-size: 14px;
  color: #6b7280;
}

.modal-footer {
  padding: 0 24px 24px 24px;
  text-align: center;
}

.modal-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.modal-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@media (max-width: 480px) {
  .login-page {
    padding: 10px;
  }
  
  .login-card {
    padding: 30px 20px;
  }
  
  .login-title {
    font-size: 24px;
  }
  
  .form-options {
    justify-content: center;
  }

  .modal-content {
    width: 95%;
  }
  
  .modal-header,
  .modal-body,
  .modal-footer {
    padding-left: 16px;
    padding-right: 16px;
  }
}
</style>