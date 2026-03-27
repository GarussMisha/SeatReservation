/**
 * BookingConfirmModal - модальное окно подтверждения бронирования/отмены
 */
<template>
  <transition name="modal-fade">
    <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
      <div class="modal-container" @click.stop>
        <div class="modal-header">
          <div class="header-icon" :class="mode">
            {{ mode === 'book' ? '✅' : '❌' }}
          </div>
          <h3 class="modal-title">{{ title }}</h3>
          <button @click="close" class="close-btn">×</button>
        </div>

        <div class="modal-body">
          <div class="workspace-info">
            <div class="info-row">
              <span class="info-label">🪑 Место:</span>
              <span class="info-value">{{ workspaceName }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">📅 Дата:</span>
              <span class="info-value">{{ formattedDate }}</span>
            </div>
            <div class="info-row" v-if="roomName">
              <span class="info-label">🏢 Помещение:</span>
              <span class="info-value">{{ roomName }}</span>
            </div>
          </div>

          <p class="confirm-message">{{ message }}</p>

          <div v-if="showWarning" class="warning-box">
            <span class="warning-icon">⚠️</span>
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
  font-size: 1.5rem;
  flex-shrink: 0;
}

.header-icon.book {
  background: linear-gradient(135deg, rgba(40, 167, 69, 0.1) 0%, rgba(34, 197, 94, 0.1) 100%);
}

.header-icon.cancel {
  background: linear-gradient(135deg, rgba(220, 53, 69, 0.1) 0%, rgba(239, 68, 68, 0.1) 100%);
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
