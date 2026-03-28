/**
 * PropertiesPanel - правая панель свойств выбранного объекта
 */
<template>
  <div v-if="selectedObject" class="properties-panel">
    <div class="panel-header">
      <h3 class="panel-title">Свойства объекта</h3>
      <button @click="handleDelete" class="btn-delete" title="Удалить">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
        </svg>
      </button>
    </div>

    <div class="panel-content">
      <!-- Тип объекта -->
      <div class="property-group">
        <label class="property-label">Тип</label>
        <div class="property-value">{{ getObjectTypeName(selectedObject.object_type) }}</div>
      </div>

      <!-- Название -->
      <div class="property-group">
        <label for="obj-name" class="property-label">Название</label>
        <div class="name-input-wrapper">
          <input
            id="obj-name"
            v-model="localName"
            type="text"
            class="property-input"
            placeholder="Введите название"
            :disabled="isSavingName"
            @blur="updateWorkspaceName(localName)"
            @keyup.enter="updateWorkspaceName(localName)"
          />
          <span v-if="isSavingName" class="saving-indicator">
            <svg class="saving-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
          </span>
        </div>
        <small v-if="selectedObject.object_type === 'workspace'" class="help-text">
          Нажмите Enter или кликните вне поля для сохранения
        </small>
      </div>

      <!-- Описание -->
      <div class="property-group">
        <label for="obj-description" class="property-label">Описание</label>
        <textarea
          id="obj-description"
          v-model="localDescription"
          class="property-textarea"
          placeholder="Введите описание"
          rows="3"
          @change="updateProperty('description', localDescription)"
        ></textarea>
      </div>

      <!-- Позиция и размеры (только для объектов, не для стен) -->
      <div v-if="!['wall', 'internal_wall', 'window'].includes(selectedObject.object_type)" class="property-group">
        <label class="property-label">Масштаб (%)</label>
        <div class="property-row">
          <label for="obj-scale" class="property-sublabel">Масштаб</label>
          <input
            id="obj-scale"
            v-model.number="localScale"
            type="number"
            min="10"
            max="500"
            class="property-input small"
            @change="updateScale(localScale)"
          />
          <span class="size-unit">%</span>
        </div>
      </div>

      <!-- Поворот (только для рабочих мест) -->
      <div v-if="selectedObject.object_type === 'workspace'" class="property-group">
        <label for="obj-rotation" class="property-label">Поворот (градусы)</label>
        <div class="rotation-control">
          <button @click="rotateObject(-90)" class="btn-rotate">↺</button>
          <input
            id="obj-rotation"
            v-model.number="localRotation"
            type="number"
            class="property-input"
            @change="updateProperty('rotation', localRotation)"
          />
          <button @click="rotateObject(90)" class="btn-rotate">↻</button>
        </div>
      </div>

      <!-- Активен -->
      <div v-if="selectedObject.object_type === 'workspace'" class="property-group">
        <label class="checkbox-label">
          <input
            v-model="localActive"
            type="checkbox"
            @change="updateProperty('is_active', localActive)"
          />
          <span>Активное рабочее место</span>
        </label>
      </div>
    </div>
  </div>

  <div v-else class="properties-panel empty">
    <div class="empty-state">
      <svg class="empty-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
      </svg>
      <p>Выберите объект<br>для редактирования</p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoomEditorStore } from '@/stores/roomEditor'
import { roomObjectsAPI } from '@/services/roomObjects'
import { useNotificationStore } from '@/stores/notifications'

const props = defineProps({
  selectedObject: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update', 'delete'])

const editorStore = useRoomEditorStore()
const notificationStore = useNotificationStore()

// Локальные копии для двухстороннего связывания
const localName = ref('')
const localDescription = ref('')
const localScale = ref(100) // Масштаб в процентах (100% = базовый размер)
const localRotation = ref(0)
const localActive = ref(true)

// Состояние для сохранения названия
const isSavingName = ref(false)
const workspaceOnPlanId = ref(null)

// Обновляем локальные значения при изменении выбранного объекта
watch(() => props.selectedObject, (newObj) => {
  if (newObj) {
    localName.value = newObj.name || ''
    localDescription.value = newObj.description || ''
    // Вычисляем масштаб в процентах (базовый размер 100px = 100%)
    localScale.value = Math.round((newObj.width || 100) / 100 * 100)
    localRotation.value = newObj.rotation || 0
    localActive.value = newObj.is_active !== undefined ? newObj.is_active : true
    
    // Получаем workspace_on_plan_id для рабочих мест
    if (newObj.object_type === 'workspace' && newObj.workspace_on_plan_id) {
      workspaceOnPlanId.value = newObj.workspace_on_plan_id
    }
  }
}, { immediate: true })

const getObjectTypeName = (type) => {
  const names = {
    wall: 'Стена',
    door: 'Дверь',
    window: 'Окно',
    workspace: 'Рабочее место',
    printer: 'Принтер',
    kitchen: 'Кухня',
    meeting_room: 'Переговорная',
    staircase: 'Лестница',
    restroom: 'Комната отдыха'
  }
  return names[type] || type
}

const updateProperty = (property, value) => {
  if (props.selectedObject) {
    emit('update', props.selectedObject.id, { [property]: value })
  }
}

const handleDelete = () => {
  if (confirm('Вы уверены, что хотите удалить этот объект?')) {
    emit('delete', props.selectedObject.id)
  }
}

// Обновление названия рабочего места через API
const updateWorkspaceName = async (newName) => {
  if (!props.selectedObject || !workspaceOnPlanId.value) return
  
  const roomId = editorStore.currentRoom?.id
  if (!roomId) {
    notificationStore.error('Помещение не выбрано', 'Ошибка')
    return
  }
  
  if (!newName || !newName.trim()) {
    notificationStore.error('Название не может быть пустым', 'Ошибка')
    return
  }
  
  try {
    isSavingName.value = true
    await roomObjectsAPI.updateWorkspaceName(roomId, workspaceOnPlanId.value, newName.trim())
    notificationStore.success('Название рабочего места обновлено', 'Успешно')
  } catch (error) {
    console.error('Ошибка обновления названия:', error)
    const errorMessage = error.response?.data?.detail || 'Не удалось обновить название'
    notificationStore.error(errorMessage, 'Ошибка')
    // Возвращаем старое название при ошибке
    localName.value = props.selectedObject.name || ''
  } finally {
    isSavingName.value = false
  }
}

// Обновление масштаба (в процентах)
const updateScale = (scalePercent) => {
  if (!props.selectedObject) return

  // Ограничиваем от 10% до 500%
  const clampedScale = Math.max(10, Math.min(500, scalePercent))
  const newSize = Math.round(clampedScale / 100 * 100)

  emit('update', props.selectedObject.id, {
    width: newSize,
    height: newSize
  })
}

// Поворот объекта
const rotateObject = (degrees) => {
  if (props.selectedObject) {
    const newRotation = (localRotation.value + degrees + 360) % 360
    localRotation.value = newRotation
    emit('update', props.selectedObject.id, { rotation: newRotation })
  }
}
</script>

<style scoped>
.properties-panel {
  width: 280px;
  background: #ffffff;
  border-left: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.properties-panel.empty {
  justify-content: center;
  align-items: center;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.panel-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #333;
}

.btn-delete {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.25rem;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.btn-delete:hover {
  opacity: 1;
}

.panel-content {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
}

.property-group {
  margin-bottom: 1.25rem;
}

.property-label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
  font-weight: 500;
  color: #666;
}

.property-value {
  padding: 0.5rem;
  background: #f5f5f5;
  border-radius: 6px;
  font-size: 0.9rem;
  color: #333;
}

.property-input,
.property-textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 0.9rem;
  transition: border-color 0.2s;
}

.property-input:focus,
.property-textarea:focus {
  outline: none;
  border-color: #2196F3;
}

.name-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.name-input-wrapper .property-input {
  flex: 1;
  padding-right: 2.5rem;
}

.saving-indicator {
  position: absolute;
  right: 0.75rem;
  display: inline-flex;
  align-items: center;
}

.saving-icon-svg {
  width: 18px;
  height: 18px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.help-text {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: #999;
}

.property-input.small {
  width: 80px;
}

.property-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.property-sublabel {
  font-size: 0.8rem;
  color: #666;
  min-width: 20px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  cursor: pointer;
}

.size-unit {
  font-size: 0.85rem;
  color: #999;
}

.rotation-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-rotate {
  padding: 0.5rem;
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.btn-rotate:hover {
  background: #e8e8e8;
}

.empty-state {
  text-align: center;
  color: #999;
}

.empty-icon-svg {
  width: 60px;
  height: 60px;
  display: block;
  margin-bottom: 1rem;
  color: var(--text-muted);
  opacity: 0.5;
}

.btn-delete svg {
  width: 20px;
  height: 20px;
}

.empty-state p {
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.5;
}

/* Scrollbar */
.panel-content::-webkit-scrollbar {
  width: 6px;
}

.panel-content::-webkit-scrollbar-track {
  background: #f5f5f5;
}

.panel-content::-webkit-scrollbar-thumb {
  background: #d0d0d0;
  border-radius: 3px;
}
</style>
