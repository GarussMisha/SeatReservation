<template>
  <div class="notification-settings-section">
    <div class="section-header">
      <div class="section-title">
        <svg class="section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
        </svg>
        <h3>Настройки уведомлений</h3>
      </div>
    </div>

    <div class="section-content">
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
        <p>{{ error }}</p>
        <button @click="loadSettings" class="retry-btn">Попробовать снова</button>
      </div>

      <!-- Переключатели -->
      <div v-else class="settings-list">
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-label">
              <svg class="setting-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
              <span>Email уведомления</span>
            </div>
            <p class="setting-description">
              Получать уведомления на электронную почту {{ user?.email }}
            </p>
          </div>
          <label class="toggle-switch">
            <input type="checkbox" v-model="localSettings.email_enabled" @change="handleToggle" />
            <span class="toggle-slider"></span>
          </label>
        </div>

        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-label">
              <svg class="setting-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
              </svg>
              <span>Уведомления в личном кабинете</span>
            </div>
            <p class="setting-description">
              Показывать уведомления в браузере (колокольчик в шапке)
            </p>
          </div>
          <label class="toggle-switch">
            <input type="checkbox" v-model="localSettings.site_enabled" @change="handleToggle" />
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useNotificationSettingsStore } from '../../stores/notificationSettings'
import { useAuthStore } from '../../stores/auth'
import { useNotificationStore } from '../../stores/notifications'

const settingsStore = useNotificationSettingsStore()
const authStore = useAuthStore()
const toastStore = useNotificationStore()

const user = computed(() => authStore.user)
const isLoading = computed(() => settingsStore.isLoading)
const error = computed(() => settingsStore.error)

const localSettings = ref({
  email_enabled: true,
  site_enabled: true
})

const loadSettings = async () => {
  try {
    const data = await settingsStore.fetchMySettings()
    localSettings.value = {
      email_enabled: data.email_enabled,
      site_enabled: data.site_enabled
    }
  } catch (err) {
    toastStore.error('Не удалось загрузить настройки уведомлений', 'Ошибка')
  }
}

const handleToggle = async () => {
  try {
    await settingsStore.updateMySettings(localSettings.value)
    toastStore.success('Настройки уведомлений сохранены', 'Успешно')
  } catch (err) {
    toastStore.error('Не удалось сохранить настройки уведомлений', 'Ошибка')
  }
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.notification-settings-section {
  background: white;
  border-radius: 1rem;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.section-header {
  padding: 1.5rem 2rem;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.section-icon {
  width: 24px;
  height: 24px;
  color: #667eea;
}

.section-title h3 {
  margin: 0;
  font-size: 1.25rem;
  color: #1f2937;
  font-weight: 600;
}

.section-content {
  padding: 2rem;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
}

.loading-spinner {
  width: 2.5rem;
  height: 2.5rem;
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
  font-size: 0.95rem;
  margin: 0 0 1rem 0;
}

.error-icon {
  width: 3rem;
  height: 3rem;
  color: #ef4444;
  margin-bottom: 1rem;
}

.retry-btn {
  padding: 0.5rem 1.5rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.retry-btn:hover {
  background: #5568d3;
}

.settings-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1rem 0;
  border-bottom: 1px solid #f3f4f6;
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
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.setting-icon {
  width: 20px;
  height: 20px;
  color: #667eea;
}

.setting-description {
  margin: 0;
  color: #6b7280;
  font-size: 0.9rem;
  line-height: 1.5;
}

/* Toggle Switch */
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 56px;
  height: 32px;
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
  border-radius: 32px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 24px;
  width: 24px;
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
  transform: translateX(24px);
}

/* Адаптивность */
@media (max-width: 768px) {
  .section-header {
    padding: 1rem 1.5rem;
  }

  .section-content {
    padding: 1.5rem;
  }

  .setting-item {
    flex-direction: column;
    gap: 1rem;
  }

  .setting-info {
    padding-right: 0;
  }

  .toggle-switch {
    align-self: flex-end;
  }
}
</style>
