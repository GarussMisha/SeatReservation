/**
 * RoomModal - модальное окно для добавления и редактирования помещений в админ-панели.
 */
<template>
  <div class="modal-overlay" @click="close">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>{{ isEdit ? 'Редактировать помещение' : 'Добавить помещение' }}</h2>
        <button @click="close" class="close-btn">×</button>
      </div>
      
      <form @submit.prevent="handleSubmit" class="modal-body">
        <div class="form-group">
          <label for="name">
            Название
            <span class="required">*</span>
          </label>
          <input
            id="name"
            v-model="formData.name"
            type="text"
            required
            placeholder="Введите название помещения"
          >
        </div>

        <div class="form-group">
          <label for="description">Описание</label>
          <textarea
            id="description"
            v-model="formData.description"
            placeholder="Описание помещения (необязательно)"
            rows="3"
          ></textarea>
        </div>

        <div class="form-group">
          <label for="address">
            Адрес
            <span class="required">*</span>
          </label>
          <input
            id="address"
            v-model="formData.address"
            type="text"
            required
            placeholder="Введите адрес помещения"
          >
        </div>

        <div class="form-group">
          <label for="status_id">Статус</label>
          <select
            id="status_id"
            v-model="formData.status_id"
          >
            <option
              v-for="status in roomStatuses"
              :key="status.id"
              :value="status.id"
            >
              {{ status.name }}
            </option>
          </select>
        </div>

        <div class="form-note">
          <span class="note-asterisk">*</span>
          <span class="note-text">Обязательные поля</span>
        </div>

        <div class="modal-footer">
          <button type="button" @click="close" class="cancel-btn">Отмена</button>
          <button type="submit" class="save-btn">
            {{ isEdit ? 'Сохранить' : 'Добавить' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  room: {
    type: Object,
    default: null
  },
  statuses: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'save'])

// Локальные данные
const formData = ref({
  name: '',
  description: '',
  address: '',
  status_id: 1
})

// Вычисляемые свойства
const isEdit = computed(() => !!props.room)

// Фильтруем статусы - для помещений только active (1) и inactive (2)
const roomStatuses = computed(() => {
  if (!props.statuses || props.statuses.length === 0) return []
  
  return props.statuses.filter(status => 
    status.id === 1 || status.id === 2  // Только active и inactive
  )
})

// Инициализация формы
watch(() => props.room, (newRoom) => {
  if (newRoom) {
    formData.value = {
      name: newRoom.name || '',
      description: newRoom.description || '',
      address: newRoom.address || '',
      status_id: newRoom.status_id || 1
    }
  } else {
    formData.value = {
      name: '',
      description: '',
      address: '',
      status_id: 1
    }
  }
}, { immediate: true })

// Методы
const close = () => {
  emit('close')
}

const handleSubmit = () => {
  emit('save', { ...formData.value })
}
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
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(8px) saturate(1.5);
}

.modal-content {
  background: #ffffff;
  border-radius: 20px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
  background: #f8f9fa;
  border-radius: 20px 20px 0 0;
}

.modal-header h2 {
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
  width: 30px;
  height: 30px;
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

.modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

.form-group label .required {
  color: var(--accent-danger);
  font-weight: 700;
  margin-left: 2px;
}

.form-note {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.note-asterisk {
  color: var(--accent-danger);
  font-weight: 700;
  font-size: var(--font-size-sm);
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s, box-shadow 0.3s;
  background: #ffffff;
  color: #333333;
}

.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s, box-shadow 0.3s;
  background: #ffffff;
  color: #333333;
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%23666666' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 0.5rem center;
  background-repeat: no-repeat;
  background-size: 1.5em 1.5em;
  padding-right: 2.5rem;
}

.form-group input::placeholder,
.form-group textarea::placeholder {
  color: #999999;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
  background: #ffffff;
}

/* Стили для опций выпадающего списка */
.form-group select option {
  background: #ffffff;
  color: #333333;
  padding: 0.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
  background: #f8f9fa;
  border-radius: 0 0 20px 20px;
  padding: 1.5rem;
}

.cancel-btn {
  padding: 0.75rem 1.5rem;
  background: #f8f9fa;
  color: #6c757d;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 500;
  font-size: 0.95rem;
}

.cancel-btn:hover {
  background-color: #e9ecef;
  border-color: #adb5bd;
  color: #495057;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.save-btn {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  color: white;
  border: 2px solid #007bff;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 500;
  font-size: 0.95rem;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
}

.save-btn:hover {
  background: linear-gradient(135deg, #0056b3 0%, #004085 100%);
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(0, 123, 255, 0.4);
}

/* Адаптивность для мобильных устройств */
@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    margin: 1rem;
    border-radius: 16px;
  }

  .modal-header {
    padding: 1rem;
  }

  .modal-body {
    padding: 1rem;
  }

  .modal-footer {
    flex-direction: column-reverse;
    gap: 0.75rem;
    padding: 1rem;
  }

  .cancel-btn,
  .save-btn {
    width: 100%;
    margin: 0;
  }
}
</style>