/**
 * NotificationToast - компонент для отображения toast-уведомлений различных типов (success, error, warning, info).
 */
<template>
  <teleport to="body">
    <div class="toast-container">
      <transition-group name="toast" tag="div">
        <div
          v-for="notification in notifications"
          :key="notification.id"
          :class="['toast', `toast--${notification.type}`]"
          @click="removeNotification(notification.id)"
        >
          <div class="toast-content">
            <div class="toast-icon">
              <svg v-if="notification.type === 'success'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <svg v-else-if="notification.type === 'error'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <svg v-else-if="notification.type === 'warning'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
              <svg v-else-if="notification.type === 'info'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <div class="toast-message">
              <strong v-if="notification.title">{{ notification.title }}</strong>
              <p>{{ notification.message }}</p>
            </div>
          </div>
          <button 
            @click.stop="removeNotification(notification.id)"
            class="toast-close"
          >
            ×
          </button>
        </div>
      </transition-group>
    </div>
  </teleport>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useNotificationStore } from '../stores/notifications'

const notificationStore = useNotificationStore()
const notifications = computed(() => notificationStore.notifications)

const removeNotification = (id) => {
  notificationStore.removeNotification(id)
}

// Автоматическое удаление уведомлений
let autoRemoveTimer

onMounted(() => {
  // Запускаем таймер для автоматического удаления уведомлений
  autoRemoveTimer = setInterval(() => {
    notifications.value.forEach(notification => {
      if (notification.autoRemove && notification.timestamp) {
        const elapsed = Date.now() - notification.timestamp
        if (elapsed > notification.duration) {
          notificationStore.removeNotification(notification.id)
        }
      }
    })
  }, 1000)
})

onUnmounted(() => {
  if (autoRemoveTimer) {
    clearInterval(autoRemoveTimer)
  }
})
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 100px;
  right: 20px;
  z-index: 9999;
  max-width: 420px;
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 16px 20px;
  margin-bottom: 12px;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  cursor: pointer;
  pointer-events: all;
  min-width: 320px;
  max-width: 420px;
  position: relative;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.toast::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: inherit;
  filter: blur(0.5px);
  z-index: -1;
}

.toast:hover {
  transform: translateX(-6px) translateY(-2px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.18);
}

.toast-content {
  display: flex;
  align-items: flex-start;
  flex: 1;
}

.toast-icon {
  margin-right: 16px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  flex-shrink: 0;
}

.toast-icon svg {
  width: 20px;
  height: 20px;
}

.toast-message {
  flex: 1;
}

.toast-message strong {
  display: block;
  margin-bottom: 4px;
  font-size: 1rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
}

.toast-message p {
  margin: 0;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.5;
}

.toast-close {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  padding: 8px;
  margin-left: 12px;
  line-height: 1;
  transition: all 0.3s ease;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.toast-close:hover {
  background: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 1);
  transform: scale(1.1);
}

.toast--success {
  background: linear-gradient(135deg,
    rgba(34, 197, 94, 0.9) 0%,
    rgba(22, 163, 74, 0.85) 100%);
  border: 1px solid rgba(34, 197, 94, 0.3);
  box-shadow: 0 8px 32px rgba(34, 197, 94, 0.15);
}

.toast--success .toast-icon {
  background: rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.95);
}

.toast--error {
  background: linear-gradient(135deg,
    rgba(239, 68, 68, 0.9) 0%,
    rgba(220, 38, 38, 0.85) 100%);
  border: 1px solid rgba(239, 68, 68, 0.3);
  box-shadow: 0 8px 32px rgba(239, 68, 68, 0.15);
}

.toast--error .toast-icon {
  background: rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.95);
}

.toast--warning {
  background: linear-gradient(135deg,
    rgba(245, 158, 11, 0.9) 0%,
    rgba(217, 119, 6, 0.85) 100%);
  border: 1px solid rgba(245, 158, 11, 0.3);
  box-shadow: 0 8px 32px rgba(245, 158, 11, 0.15);
}

.toast--warning .toast-icon {
  background: rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.95);
}

.toast--info {
  background: linear-gradient(135deg,
    rgba(59, 130, 246, 0.9) 0%,
    rgba(37, 99, 235, 0.85) 100%);
  border: 1px solid rgba(59, 130, 246, 0.3);
  box-shadow: 0 8px 32px rgba(59, 130, 246, 0.15);
}

.toast--info .toast-icon {
  background: rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.95);
}

/* Анимации */
.toast-enter-active {
  transition: all 0.3s ease-out;
}

.toast-leave-active {
  transition: all 0.3s ease-in;
}

.toast-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.toast-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

.toast-move {
  transition: transform 0.3s ease;
}

/* Адаптивность */
@media (max-width: 768px) {
  .toast-container {
    left: 16px;
    right: 16px;
    top: 90px;
    max-width: none;
  }
  
  .toast {
    min-width: auto;
    width: 100%;
    padding: 14px 16px;
    margin-bottom: 10px;
  }
  
  .toast-message strong {
    font-size: 0.95rem;
  }
  
  .toast-message p {
    font-size: 0.85rem;
  }
  
  .toast-icon {
    width: 28px;
    height: 28px;
    font-size: 1.2rem;
    margin-right: 12px;
  }
}

@media (max-width: 480px) {
  .toast-container {
    top: 80px;
    left: 12px;
    right: 12px;
  }
  
  .toast {
    padding: 12px 14px;
    min-width: auto;
  }
  
  .toast-message strong {
    font-size: 0.9rem;
  }
  
  .toast-message p {
    font-size: 0.8rem;
  }
  
  .toast-icon {
    width: 24px;
    height: 24px;
    font-size: 1.1rem;
    margin-right: 10px;
  }
}
</style>