/**
 * PropertiesPanel - правая панель свойств выбранного объекта
 */
<template>
  <div v-if="selectedObject" class="properties-panel">
    <div class="panel-header">
      <h3 class="panel-title">Свойства объекта</h3>
      <button @click="$emit('delete', selectedObject.id)" class="btn-delete" title="Удалить">
        🗑️
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
        <input
          id="obj-name"
          v-model="localName"
          type="text"
          class="property-input"
          placeholder="Введите название"
          @change="updateProperty('name', localName)"
        />
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

      <!-- Позиция -->
      <div class="property-group">
        <label class="property-label">Позиция</label>
        <div class="property-row">
          <label for="obj-x" class="property-sublabel">X</label>
          <input
            id="obj-x"
            v-model.number="localX"
            type="number"
            class="property-input small"
            @change="updateProperty('x', localX)"
          />
        </div>
        <div class="property-row">
          <label for="obj-y" class="property-sublabel">Y</label>
          <input
            id="obj-y"
            v-model.number="localY"
            type="number"
            class="property-input small"
            @change="updateProperty('y', localY)"
          />
        </div>
      </div>

      <!-- Размеры -->
      <div class="property-group">
        <label class="property-label">Размеры</label>
        <div class="property-row">
          <label for="obj-width" class="property-sublabel">Ширина</label>
          <input
            id="obj-width"
            v-model.number="localWidth"
            type="number"
            class="property-input small"
            @change="updateProperty('width', localWidth)"
          />
        </div>
        <div class="property-row">
          <label for="obj-height" class="property-sublabel">Высота</label>
          <input
            id="obj-height"
            v-model.number="localHeight"
            type="number"
            class="property-input small"
            @change="updateProperty('height', localHeight)"
          />
        </div>
      </div>

      <!-- Поворот -->
      <div class="property-group">
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

    <div class="panel-footer">
      <button @click="duplicateObject" class="btn-duplicate">
        📋 Дублировать
      </button>
    </div>
  </div>

  <div v-else class="properties-panel empty">
    <div class="empty-state">
      <span class="empty-icon">📋</span>
      <p>Выберите объект<br>для редактирования</p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'

const props = defineProps({
  selectedObject: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update', 'delete'])

// Локальные копии для двухстороннего связывания
const localName = ref('')
const localDescription = ref('')
const localX = ref(0)
const localY = ref(0)
const localWidth = ref(0)
const localHeight = ref(0)
const localRotation = ref(0)
const localActive = ref(true)

// Обновляем локальные значения при изменении выбранного объекта
watch(() => props.selectedObject, (newObj) => {
  if (newObj) {
    localName.value = newObj.name || ''
    localDescription.value = newObj.description || ''
    localX.value = newObj.x || 0
    localY.value = newObj.y || 0
    localWidth.value = newObj.width || 100
    localHeight.value = newObj.height || 50
    localRotation.value = newObj.rotation || 0
    localActive.value = newObj.is_active !== undefined ? newObj.is_active : true
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

const rotateObject = (degrees) => {
  if (props.selectedObject) {
    const newRotation = (localRotation.value + degrees + 360) % 360
    localRotation.value = newRotation
    emit('update', props.selectedObject.id, { rotation: newRotation })
  }
}

const duplicateObject = () => {
  if (props.selectedObject) {
    const duplicated = {
      ...props.selectedObject,
      id: Date.now(),
      x: props.selectedObject.x + 20,
      y: props.selectedObject.y + 20,
      name: (props.selectedObject.name || '') + ' (копия)'
    }
    emit('update', props.selectedObject.id, duplicated)
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

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  cursor: pointer;
}

.panel-footer {
  padding: 1rem;
  border-top: 1px solid #e0e0e0;
}

.btn-duplicate {
  width: 100%;
  padding: 0.75rem;
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-duplicate:hover {
  background: #e8e8e8;
}

.empty-state {
  text-align: center;
  color: #999;
}

.empty-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 1rem;
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
