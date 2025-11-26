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
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  backdrop-filter: blur(8px) saturate(1.5);
}

.confirm-modal-content {
  background: #ffffff;
  border-radius: 20px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
  width: 90%;
  max-width: 420px;
  max-height: 90vh;
  overflow: hidden;
  animation: modalSlideIn 0.3s ease-out;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.confirm-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
  background: #f8f9fa;
  border-radius: 20px 20px 0 0;
}

.confirm-modal-header h3 {
  margin: 0;
  color: #333333;
  font-size: 1.25rem;
  font-weight: 600;
}

.close-btn {
  background: #f5f5f5;
  border: 1px solid #ddd;
  font-size: 1.5rem;
  color: #666;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s;
}

.close-btn:hover {
  background-color: #e0e0e0;
  color: #333;
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.confirm-modal-body {
  padding: 1.5rem;
}

.confirm-modal-body p {
  margin: 0;
  color: #333333;
  font-size: 1rem;
  line-height: 1.5;
}

.confirm-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.5rem;
  border-top: 1px solid #e0e0e0;
  background: #f8f9fa;
  border-radius: 0 0 20px 20px;
}

.cancel-btn {
  padding: 0.75rem 1.5rem;
  background: #f8f9fa;
  color: #6c757d;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s;
}

.cancel-btn:hover {
  background-color: #e9ecef;
  border-color: #adb5bd;
  color: #495057;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.confirm-btn {
  padding: 0.75rem 1.5rem;
  border: 2px solid;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s;
  min-width: 100px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.confirm-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.confirm-btn.danger {
  background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
  border-color: #dc3545;
  color: white;
}

.confirm-btn.danger:hover {
  background: linear-gradient(135deg, #c82333 0%, #bd2130 100%);
  border-color: #bd2130;
  box-shadow: 0 6px 20px rgba(220, 53, 69, 0.4);
}

.confirm-btn.warning {
  background: linear-gradient(135deg, #ffc107 0%, #e0a800 100%);
  border-color: #ffc107;
  color: #212529;
}

.confirm-btn.warning:hover {
  background: linear-gradient(135deg, #e0a800 0%, #d39e00 100%);
  border-color: #d39e00;
  box-shadow: 0 6px 20px rgba(255, 193, 7, 0.4);
}

.confirm-btn.primary {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  border-color: #007bff;
  color: white;
}

.confirm-btn.primary:hover {
  background: linear-gradient(135deg, #0056b3 0%, #004085 100%);
  border-color: #004085;
  box-shadow: 0 6px 20px rgba(0, 123, 255, 0.4);
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
    border-radius: 16px;
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