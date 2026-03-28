/**
 * ConfirmModal - универсальное модальное окно подтверждения действий.
 */
<template>
  <teleport to="body">
    <div v-if="show" class="confirm-modal-overlay" @click="handleCancel">
      <div class="confirm-modal-content" @click.stop>
        <div class="confirm-modal-header">
          <h3>{{ title }}</h3>
          <button @click="handleCancel" class="close-btn">×</button>
        </div>
        
        <div class="confirm-modal-body">
          <p>{{ message }}</p>
        </div>
        
        <div class="confirm-modal-footer">
          <button @click="handleCancel" class="cancel-btn">
            {{ cancelText }}
          </button>
          <button @click="handleConfirm" class="confirm-btn" :class="confirmType">
            {{ confirmText }}
          </button>
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: 'Подтверждение действия'
  },
  message: {
    type: String,
    required: true
  },
  confirmText: {
    type: String,
    default: 'Подтвердить'
  },
  cancelText: {
    type: String,
    default: 'Отмена'
  },
  confirmType: {
    type: String,
    default: 'danger', // 'danger', 'warning', 'primary'
    validator: (value) => ['danger', 'warning', 'primary'].includes(value)
  }
})

const emit = defineEmits(['confirm', 'cancel'])

// Закрытие по Escape
const handleKeydown = (event) => {
  if (event.key === 'Escape') {
    handleCancel()
  }
}

watch(() => props.show, (newShow) => {
  if (newShow) {
    document.addEventListener('keydown', handleKeydown)
    document.body.style.overflow = 'hidden'
  } else {
    document.removeEventListener('keydown', handleKeydown)
    document.body.style.overflow = ''
  }
})

const handleConfirm = () => {
  emit('confirm')
}

const handleCancel = () => {
  emit('cancel')
}
</script>

<style scoped>
.confirm-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: var(--z-modal-overlay);
  backdrop-filter: var(--backdrop-filter-sm);
  animation: fadeIn 0.3s ease;
}

.confirm-modal-content {
  background: var(--bg-white);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-xl);
  width: 90%;
  max-width: 440px;
  max-height: 90vh;
  overflow: hidden;
  animation: modalSlideIn 0.3s ease-out;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.confirm-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg) var(--spacing-xl);
  border-bottom: 1px solid #e5e7eb;
  background: var(--gradient-card-light);
}

.confirm-modal-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
}

.close-btn {
  background: rgba(0, 0, 0, 0.05);
  border: none;
  font-size: 1.5rem;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  transition: var(--transition-base);
}

.close-btn:hover {
  background: rgba(0, 0, 0, 0.1);
  color: var(--text-primary);
  transform: rotate(90deg);
}

.confirm-modal-body {
  padding: var(--spacing-xl);
}

.confirm-modal-body p {
  margin: 0;
  color: var(--text-body);
  font-size: var(--font-size-base);
  line-height: var(--line-height-normal);
}

.confirm-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  padding: var(--spacing-lg) var(--spacing-xl);
  border-top: 1px solid #e5e7eb;
  background: var(--bg-light);
}

.cancel-btn {
  padding: 0.75rem 1.5rem;
  background: var(--bg-white);
  color: var(--text-muted);
  border: 2px solid #e5e7eb;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  transition: var(--transition-base);
}

.cancel-btn:hover {
  background: #f9fafb;
  border-color: #adb5bd;
  color: var(--text-secondary);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.confirm-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  transition: var(--transition-base);
  min-width: 100px;
  color: var(--text-white);
}

.confirm-btn:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-lg);
}

.confirm-btn.danger {
  background: var(--gradient-danger);
}

.confirm-btn.danger:hover {
  background: var(--gradient-danger-hover);
  box-shadow: 0 6px 20px rgba(220, 53, 69, 0.4);
}

.confirm-btn.warning {
  background: var(--gradient-warning);
  color: #212529;
}

.confirm-btn.warning:hover {
  background: linear-gradient(135deg, #d39e00 0%, #c49000 100%);
  box-shadow: 0 6px 20px rgba(255, 193, 7, 0.4);
}

.confirm-btn.primary {
  background: var(--gradient-info);
}

.confirm-btn.primary:hover {
  background: linear-gradient(135deg, #004085 0%, #003366 100%);
  box-shadow: 0 6px 20px rgba(0, 123, 255, 0.4);
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Адаптивность */
@media (max-width: 480px) {
  .confirm-modal-content {
    width: 95%;
    margin: 1rem;
    border-radius: var(--radius-xl);
  }

  .confirm-modal-header,
  .confirm-modal-body,
  .confirm-modal-footer {
    padding: 1rem;
  }

  .confirm-modal-footer {
    flex-direction: column-reverse;
  }

  .cancel-btn,
  .confirm-btn {
    width: 100%;
  }
}
</style>