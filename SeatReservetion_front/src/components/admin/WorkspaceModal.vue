/**
 * WorkspaceModal - модальное окно для добавления и редактирования рабочих мест в админ-панели.
 */
 <template>
  <div class="modal-overlay" @click="close">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>{{ isEdit ? 'Редактировать рабочее место' : 'Добавить рабочее место' }}</h2>
        <button @click="close" class="close-btn">×</button>
      </div>

      <form @submit.prevent="handleSubmit" class="modal-body">
        <div class="form-group">
          <label for="name">
            Название рабочего места
            <span class="required">*</span>
          </label>
          <input
            id="name"
            v-model="formData.name"
            type="text"
            required
            placeholder="Введите название рабочего места"
          >
        </div>

        <div class="form-group">
          <label for="room_id">
            Помещение
            <span class="required">*</span>
          </label>
          <select
            id="room_id"
            v-model="formData.room_id"
            required
          >
            <option
              v-for="room in rooms"
              :key="room.id"
              :value="room.id"
            >
              {{ room.name }} ({{ room.address }})
            </option>
          </select>
        </div>

        <div class="form-group">
          <label for="status_id">Статус</label>
          <select
            id="status_id"
            v-model="formData.status_id"
            required
          >
            <option :value="10">Свободно</option>
            <option :value="11">Занято</option>
            <option :value="2">Неактивно</option>
          </select>
        </div>

        <div class="status-hint">
          <svg class="hint-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <span class="hint-text">{{ getStatusHint(formData.status_id) }}</span>
        </div>

        <div class="form-note">
          <span class="note-asterisk">*</span>
          <span class="note-text">Обязательные поля</span>
        </div>

        <!-- Оставляем is_active для обратной совместимости, но скрываем -->
        <div class="form-group" style="display: none;">
          <label class="checkbox-label">
            <input
              id="is_active"
              v-model="formData.is_active"
              type="checkbox"
            >
            <span class="checkmark"></span>
            Активное рабочее место (устаревшее)
          </label>
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
  workspace: {
    type: Object,
    default: null
  },
  rooms: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'save'])

// Статусы по умолчанию (должны совпадать с бэкендом)
const defaultStatuses = {
  FREE: 10,         // free (Свободно)
  OCCUPIED: 11,     // occupied (Занято)
  INACTIVE: 2       // inactive (Не активно)
}

// Локальные данные
const formData = ref({
  name: '',
  room_id: null,
  status_id: defaultStatuses.FREE,
  is_active: true // Для обратной совместимости
})

// Вычисляемые свойства
const isEdit = computed(() => !!props.workspace)

// Подсказка для статуса
const getStatusHint = (statusId) => {
  const hints = {
    [defaultStatuses.FREE]: 'Рабочее место доступно для бронирования',
    [defaultStatuses.OCCUPIED]: 'Рабочее место занято (есть активное бронирование)',
    [defaultStatuses.INACTIVE]: 'Рабочее место отключено и недоступно для бронирования'
  }
  return hints[statusId] || ''
}

// Инициализация формы
watch(() => props.workspace, (newWorkspace) => {
  if (newWorkspace) {
    formData.value = {
      name: newWorkspace.name || '',
      room_id: newWorkspace.room_id || null,
      status_id: newWorkspace.status_id || defaultStatuses.FREE,
      is_active: newWorkspace.is_active !== undefined ? newWorkspace.is_active : true
    }
  } else {
    formData.value = {
      name: '',
      room_id: props.rooms.length > 0 ? props.rooms[0].id : null,
      status_id: defaultStatuses.FREE,
      is_active: true
    }
  }
}, { immediate: true })

// Методы
const close = () => {
  emit('close')
}

const handleSubmit = () => {
  // Синхронизируем is_active со status_id для обратной совместимости
  formData.value.is_active = formData.value.status_id !== defaultStatuses.INACTIVE
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

/* Стили для выпадающего списка */
.form-group select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%23666666' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 0.5rem center;
  background-repeat: no-repeat;
  background-size: 1.5em 1.5em;
  padding-right: 2.5rem;
}

/* Стили для опций выпадающего списка */
.form-group select option {
  background: #ffffff;
  color: #333333;
  padding: 0.5rem;
}

.status-hint {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  border-left: 3px solid var(--primary-start);
  border-radius: var(--radius-md);
  margin-bottom: 1rem;
}

.hint-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  color: var(--primary-start);
}

.hint-text {
  font-size: var(--font-size-sm);
  color: var(--text-body);
  line-height: var(--line-height-normal);
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #333333;
  font-size: 0.95rem;
  position: relative;
  padding-left: 1.8em;
  height: 1.4em;
  margin-bottom: 0;
}

.checkbox-label input[type="checkbox"] {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.checkbox-label .checkmark {
  position: absolute;
  top: 0;
  left: 0;
  height: 1.2em;
  width: 1.2em;
  background-color: #f8f9fa;
  border: 2px solid #e0e0e0;
  border-radius: 4px;
  transition: all 0.3s;
}

.checkbox-label:hover .checkmark {
  background-color: #e9ecef;
  border-color: #adb5bd;
}

.checkbox-label input:checked ~ .checkmark {
  background-color: #007bff;
  border-color: #007bff;
}

.checkbox-label .checkmark:after {
  content: "";
  position: absolute;
  display: none;
}

.checkbox-label input:checked ~ .checkmark:after {
  display: block;
}

.checkbox-label .checkmark:after {
  left: 0.4em;
  top: 0.15em;
  width: 0.25em;
  height: 0.5em;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
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