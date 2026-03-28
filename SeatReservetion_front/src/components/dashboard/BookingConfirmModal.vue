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
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal-overlay);
  padding: 1rem;
  backdrop-filter: var(--backdrop-filter-sm);
}

.modal-container {
  background: var(--bg-white);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-xl);
  max-width: 480px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  animation: modal-slide-in 0.3s ease-out;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.modal-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  padding: var(--spacing-lg) var(--spacing-xl);
  border-bottom: 1px solid #f0f0f0;
  background: var(--gradient-card-light);
}

.header-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.header-icon svg {
  width: 28px;
  height: 28px;
}

.header-icon.book {
  background: var(--gradient-success);
}

.header-icon.book svg {
  color: var(--text-white);
}

.header-icon.cancel {
  background: var(--gradient-danger);
}

.header-icon.cancel svg {
  color: var(--text-white);
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
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.close-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: rgba(0, 0, 0, 0.05);
  border-radius: var(--radius-full);
  cursor: pointer;
  font-size: 1.5rem;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition-base);
}

.close-btn:hover {
  background: rgba(0, 0, 0, 0.1);
  color: var(--text-primary);
  transform: rotate(90deg);
}

.modal-body {
  padding: var(--spacing-xl);
}

.workspace-info {
  background: var(--gradient-card-light);
  padding: var(--spacing-lg);
  border-radius: var(--radius-xl);
  margin-bottom: var(--spacing-lg);
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.info-row {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: 0.5rem;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-label {
  font-weight: var(--font-weight-semibold);
  color: var(--text-muted);
  min-width: 100px;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.info-value {
  font-weight: var(--font-weight-medium);
  color: var(--text-secondary);
}

.confirm-message {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--text-body);
  line-height: var(--line-height-normal);
}

.warning-box {
  margin-top: var(--spacing-lg);
  padding: var(--spacing-lg);
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(251, 146, 60, 0.1) 100%);
  border-left: 4px solid var(--accent-warning);
  border-radius: var(--radius-lg);
  display: flex;
  gap: var(--spacing-sm);
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
  gap: var(--spacing-sm);
  padding: var(--spacing-lg) var(--spacing-xl);
  border-top: 1px solid #e5e7eb;
  background: var(--bg-light);
}

.btn {
  flex: 1;
  padding: 0.875rem 1.5rem;
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: var(--transition-base);
}

.btn-cancel {
  background: var(--bg-white);
  color: var(--text-muted);
  border: 2px solid #e5e7eb;
}

.btn-cancel:hover:not(:disabled) {
  background: #f9fafb;
  border-color: #adb5bd;
  color: var(--text-secondary);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-cancel:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-confirm {
  color: var(--text-white);
}

.btn-confirm.book {
  background: var(--gradient-success);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
}

.btn-confirm.book:hover:not(:disabled) {
  background: var(--gradient-success-hover);
  box-shadow: 0 6px 16px rgba(40, 167, 69, 0.4);
  transform: translateY(-2px);
}

.btn-confirm.cancel {
  background: var(--gradient-danger);
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
}

.btn-confirm.cancel:hover:not(:disabled) {
  background: var(--gradient-danger-hover);
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
