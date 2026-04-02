<template>
  <div class="notification-settings-page">
    <!-- Фоновая декорация -->
    <div class="background-decoration">
      <div class="floating-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
        <div class="shape shape-4"></div>
      </div>
    </div>

    <div class="settings-container">
      <!-- Заголовок -->
      <div class="page-header">
        <div class="header-content">
          <h1>
            <svg class="page-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
            Настройки уведомлений
          </h1>
          <p class="subtitle">Управляйте способами получения уведомлений</p>
        </div>
      </div>

      <!-- Основной контент -->
      <main class="settings-content">
        <!-- Загрузка -->
        <div v-if="isLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Загрузка настроек...</p>
        </div>

        <!-- Ошибка -->
        <div v-else-if="error" class="error-state">
          <svg class="error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <h2>Ошибка загрузки</h2>
          <p>{{ error }}</p>
          <button @click="loadSettings" class="retry-btn">Попробовать снова</button>
        </div>

        <!-- Форма настроек -->
        <div v-else class="settings-form">
          <div class="settings-card">
            <div class="card-header">
              <svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
              <h2>Способы получения уведомлений</h2>
            </div>

            <div class="card-content">
              <div class="setting-item">
                <div class="setting-info">
                  <div class="setting-label">
                    <svg class="setting-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                    </svg>
                    Email уведомления
                  </div>
                  <p class="setting-description">
                    Получать уведомления на электронную почту {{ user?.email }}
                  </p>
                </div>
                <label class="toggle-switch">
                  <input type="checkbox" v-model="settings.email_enabled" />
                  <span class="toggle-slider"></span>
                </label>
              </div>

              <div class="setting-item">
                <div class="setting-info">
                  <div class="setting-label">
                    <svg class="setting-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
                    </svg>
                    Уведомления на сайте
                  </div>
                  <p class="setting-description">
                    Показывать уведомления в браузере (колокольчик в шапке)
                  </p>
                </div>
                <label class="toggle-switch">
                  <input type="checkbox" v-model="settings.site_enabled" />
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>

            <div class="card-footer">
              <button @click="saveSettings" class="save-btn" :disabled="isSaving">
                <svg v-if="!isSaving" class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"/>
                </svg>
                <svg v-else class="btn-icon btn-icon-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                </svg>
                {{ isSaving ? 'Сохранение...' : 'Сохранить изменения' }}
              </button>
            </div>
          </div>

          <!-- Информация -->
          <div class="info-card">
            <div class="info-header">
              <svg class="info-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <h3>Как это работает?</h3>
            </div>
            <div class="info-content">
              <p><strong>Email уведомления</strong> — важные уведомления дублируются на вашу электронную почту. Например, отмена бронирования или изменение статуса рабочего места.</p>
              <p><strong>Уведомления на сайте</strong> — уведомления отображаются в браузере (иконка колокольчика в шапке сайта). Вы увидите их, когда зайдёте на сайт.</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useNotificationSettingsStore } from '../stores/notificationSettings'
import { useAuthStore } from '../stores/auth'
import { useNotificationStore } from '../stores/notifications'

const settingsStore = useNotificationSettingsStore()
const authStore = useAuthStore()
const toastStore = useNotificationStore()

const settings = ref({
  email_enabled: true,
  site_enabled: true
})

const isLoading = computed(() => settingsStore.isLoading)
const error = computed(() => settingsStore.error)
const user = computed(() => authStore.user)

const isSaving = ref(false)

const loadSettings = async () => {
  try {
    const data = await settingsStore.fetchMySettings()
    settings.value = {
      email_enabled: data.email_enabled,
      site_enabled: data.site_enabled
    }
  } catch (err) {
    toastStore.error('Не удалось загрузить настройки уведомлений', 'Ошибка')
  }
}

const saveSettings = async () => {
  isSaving.value = true
  
  try {
    await settingsStore.updateMySettings(settings.value)
    toastStore.success('Настройки уведомлений сохранены', 'Успешно')
  } catch (err) {
    toastStore.error('Не удалось сохранить настройки уведомлений', 'Ошибка')
  } finally {
    isSaving.value = false
  }
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.notification-settings-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 8rem 20px 20px 20px;
  position: relative;
  overflow: hidden;
}

.background-decoration {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.floating-shapes .shape {
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
}

.shape-2 {
  width: 120px;
  height: 120px;
  top: 60%;
  right: 10%;
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

.settings-container {
  max-width: 800px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.page-header {
  margin-bottom: 2rem;
  background: rgba(255, 255, 255, 0.95);
  padding: 1.5rem 2rem;
  border-radius: 1rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.header-content h1 {
  margin: 0 0 0.5rem 0;
  font-size: var(--font-size-3xl);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.page-icon {
  width: 32px;
  height: 32px;
  color: var(--primary-start);
}

.subtitle {
  margin: 0;
  color: #6b7280;
  font-size: 1rem;
}

/* Контент */
.settings-content {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.loading-spinner {
  width: 3rem;
  height: 3rem;
  border: 3px solid #e5e7eb;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p,
.error-state p {
  color: #6b7280;
  font-size: 1.1rem;
}

.error-icon {
  width: 4rem;
  height: 4rem;
  color: #ef4444;
  margin-bottom: 1rem;
}

.error-state h2 {
  margin: 0 0 0.5rem 0;
  color: #374151;
  font-size: 1.5rem;
}

.retry-btn {
  margin-top: 1.5rem;
  padding: 0.75rem 2rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.retry-btn:hover {
  background: #5568d3;
}

/* Форма настроек */
.settings-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.settings-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 1rem;
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem 2rem;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.card-icon {
  width: 28px;
  height: 28px;
  color: #667eea;
}

.card-header h2 {
  margin: 0;
  font-size: 1.25rem;
  color: #1f2937;
}

.card-content {
  padding: 2rem;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1.5rem 0;
  border-bottom: 1px solid #e5e7eb;
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-info {
  flex: 1;
  padding-right: 2rem;
}

.setting-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.setting-icon {
  width: 24px;
  height: 24px;
  color: #667eea;
}

.setting-description {
  margin: 0;
  color: #6b7280;
  font-size: 0.95rem;
  line-height: 1.5;
}

/* Toggle Switch */
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 34px;
  flex-shrink: 0;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #d1d5db;
  transition: 0.3s;
  border-radius: 34px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 26px;
  width: 26px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: #667eea;
}

input:checked + .toggle-slider:before {
  transform: translateX(26px);
}

/* Footer */
.card-footer {
  padding: 1.5rem 2rem;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
}

.save-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.save-btn:hover:not(:disabled) {
  background: #5568d3;
  transform: translateY(-1px);
}

.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon {
  width: 20px;
  height: 20px;
}

.btn-icon-spin {
  animation: spin 1s linear infinite;
}

/* Info Card */
.info-card {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 1rem;
  padding: 1.5rem;
}

.info-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.info-icon {
  width: 24px;
  height: 24px;
  color: #3b82f6;
}

.info-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #1e40af;
}

.info-content p {
  margin: 0 0 1rem 0;
  color: #1e3a8a;
  line-height: 1.6;
}

.info-content p:last-child {
  margin-bottom: 0;
}

/* Адаптивность */
@media (max-width: 768px) {
  .notification-settings-page {
    padding: 1rem;
  }

  .page-header {
    padding: 1rem;
  }

  .header-content h1 {
    font-size: var(--font-size-xl);
  }

  .settings-content {
    padding: 1rem;
  }

  .card-header {
    padding: 1rem;
  }

  .card-content {
    padding: 1rem;
  }

  .setting-item {
    flex-direction: column;
    gap: 1rem;
  }

  .setting-info {
    padding-right: 0;
  }

  .card-footer {
    padding: 1rem;
  }

  .save-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
