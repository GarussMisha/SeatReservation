/**
 * BookingConfirmModal - модальное окно подтверждения бронирования/отмены
 */
<template>
  <transition name="modal-fade">
    <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
      <div class="modal-container" @click.stop>
        <div class="modal-header">
          <div class="header-icon" :class="mode">
            <svg v-if="mode === 'book'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
          <h3 class="modal-title">{{ title }}</h3>
          <button @click="close" class="close-btn">×</button>
        </div>

        <div class="modal-body">
          <div class="workspace-info">
            <div class="info-row">
              <span class="info-label">
                <svg class="info-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
                </svg>
                Место:
              </span>
              <span class="info-value">{{ workspaceName }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">
                <svg class="info-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                </svg>
                Дата:
              </span>
              <span class="info-value">{{ formattedDate }}</span>
            </div>
            <div class="info-row" v-if="roomName">
              <span class="info-label">
                <svg class="info-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
                </svg>
                Помещение:
              </span>
              <span class="info-value">{{ roomName }}</span>
            </div>
          </div>

          <p class="confirm-message">{{ message }}</p>

          <div v-if="showWarning" class="warning-box">
            <svg class="warning-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
            </svg>
            <span class="warning-text">{{ warningText }}</span>
          </div>
        </div>

        <div class="modal-footer">
          <button
            @click="handleCancel"
            class="btn btn-cancel"
            :disabled="isLoading"
          >
            {{ cancelText }}
          </button>
          <button
            @click="handleConfirm"
            class="btn btn-confirm"
            :class="mode"
            :disabled="isLoading"
          >
            {{ isLoading ? 'Обработка...' : confirmText }}
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { computed, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  mode: {
    type: String,
    default: 'book', // 'book' или 'cancel'
    validator: (value) => ['book', 'cancel'].includes(value)
  },
  workspaceName: {
    type: String,
    default: ''
  },
  workspaceId: {
    type: [Number, String],
    default: null
  },
  bookingId: {
    type: [Number, String],
    default: null
  },
  date: {
    type: String,
    default: ''
  },
  roomName: {
    type: String,
    default: ''
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'confirm', 'cancel'])

// Вычисляемые свойства
const title = computed(() => {
  return props.mode === 'book'
    ? 'Подтверждение бронирования'
    : 'Отмена бронирования'
})

const message = computed(() => {
  if (props.mode === 'book') {
    return `Вы хотите забронировать рабочее место "${props.workspaceName}" на ${props.formattedDate || props.date}?`
  } else {
    return 'Вы уверены, что хотите отменить это бронирование? Это действие нельзя отменить.'
  }
})

const formattedDate = computed(() => {
  if (!props.date) return ''
  const d = new Date(props.date)
  return d.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
})

const showWarning = computed(() => {
  return props.mode === 'cancel'
})

const warningText = computed(() => {
  return 'После отмены бронирования место может быть занято другим пользователем.'
})

const confirmText = computed(() => {
  return props.mode === 'book' ? 'Забронировать' : 'Отменить бронь'
})

const cancelText = computed(() => {
  return props.mode === 'book' ? 'Отмена' : 'Назад'
})

// Методы
const close = () => {
  emit('close')
}

const handleOverlayClick = () => {
  if (!props.isLoading) {
    close()
  }
}

const handleCancel = () => {
  emit('cancel')
  close()
}

const handleConfirm = () => {
  emit('confirm', {
    workspaceId: props.workspaceId,
    bookingId: props.bookingId,
    date: props.date
  })
}

// Обработка Escape
const handleEscape = (e) => {
  if (e.key === 'Escape' && props.show && !props.isLoading) {
    close()
  }
}

// Блокировка прокрутки фона
watch(() => props.show, (newValue) => {
  if (newValue) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})

onMounted(() => {
  document.addEventListener('keydown', handleEscape)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscape)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1rem;
  backdrop-filter: blur(4px);
}

.modal-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 480px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  animation: modal-slide-in 0.3s ease-out;
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem 1.5rem 1rem;
  border-bottom: 1px solid #f0f0f0;
}

.header-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.header-icon svg {
  width: 28px;
  height: 28px;
}

.header-icon.book {
  background: linear-gradient(135deg, rgba(40, 167, 69, 0.1) 0%, rgba(34, 197, 94, 0.1) 100%);
}

.header-icon.cancel {
  background: linear-gradient(135deg, rgba(220, 53, 69, 0.1) 0%, rgba(239, 68, 68, 0.1) 100%);
}

.info-icon-svg {
  width: 16px;
  height: 16px;
  vertical-align: middle;
  margin-right: 4px;
}

.warning-icon-svg {
  width: 20px;
  height: 20px;
  margin-right: 8px;
  flex-shrink: 0;
}

.modal-title {
  flex: 1;
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #1f2937;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: #f5f5f5;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.5rem;
  color: #666;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #e0e0e0;
  color: #333;
}

.modal-body {
  padding: 1.5rem;
}

.workspace-info {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  padding: 1rem;
  border-radius: 12px;
  margin-bottom: 1rem;
}

.info-row {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-label {
  font-weight: 600;
  color: #666;
  min-width: 100px;
}

.info-value {
  font-weight: 500;
  color: #333;
}

.confirm-message {
  margin: 0;
  font-size: 0.95rem;
  color: #666;
  line-height: 1.6;
}

.warning-box {
  margin-top: 1rem;
  padding: 1rem;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(251, 146, 60, 0.1) 100%);
  border-left: 4px solid #f59e0b;
  border-radius: 8px;
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

.warning-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.warning-text {
  font-size: 0.9rem;
  color: #92400e;
  line-height: 1.5;
}

.modal-footer {
  display: flex;
  gap: 1rem;
  padding: 1rem 1.5rem 1.5rem;
  border-top: 1px solid #f0f0f0;
}

.btn {
  flex: 1;
  padding: 0.875rem 1.5rem;
  border: none;
  border-radius: 10px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-cancel {
  background: #f5f5f5;
  color: #666;
}

.btn-cancel:hover {
  background: #e8e8e8;
}

.btn-cancel:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-confirm {
  color: white;
}

.btn-confirm.book {
  background: linear-gradient(135deg, #28a745 0%, #218838 100%);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
}

.btn-confirm.book:hover:not(:disabled) {
  background: linear-gradient(135deg, #34ce57 0%, #28a745 100%);
  box-shadow: 0 6px 16px rgba(40, 167, 69, 0.4);
  transform: translateY(-2px);
}

.btn-confirm.cancel {
  background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
}

.btn-confirm.cancel:hover:not(:disabled) {
  background: linear-gradient(135deg, #e74a3b 0%, #d32f2f 100%);
  box-shadow: 0 6px 16px rgba(220, 53, 69, 0.4);
  transform: translateY(-2px);
}

.btn-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

/* Анимации */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

@keyframes modal-slide-in {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
</style>
