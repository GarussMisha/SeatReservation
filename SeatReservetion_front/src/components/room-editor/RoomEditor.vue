/**
 * RoomEditor - главный компонент редактора помещений
 * Предоставляет интерфейс для создания плана помещения
 */
<template>
  <div class="room-editor">
    <!-- Верхняя панель инструментов -->
    <EditorToolbar
      :can-undo="canUndo"
      :can-redo="canRedo"
      @undo="handleUndo"
      @redo="handleRedo"
      @save="handleSave"
      @clear="handleClear"
      @cancel="handleCancel"
    />

    <div class="editor-body">
      <!-- Левая панель - палитра объектов -->
      <ObjectPalette
        :current-tool="currentTool"
        :field-width="fieldWidth"
        :field-height="fieldHeight"
        :is-drawing="isDrawing"
        :current-line-length="currentLineLength"
        :show-grid="showGrid"
        @select-tool="handleSelectTool"
        @update-field-size="handleUpdateFieldSize"
        @toggle-snap="handleToggleSnap"
        @toggle-grid="handleToggleGrid"
      />

      <!-- Центральная область - холст -->
      <div class="canvas-wrapper">
        <WallDrawingCanvas
          :current-tool="currentTool"
          :grid-size="gridSize"
          :zoom="zoom"
          :offset="offset"
          :field-width="fieldWidth"
          :field-height="fieldHeight"
          :snap-to-grid="snapToGrid"
          @update-zoom="handleUpdateZoom"
          @update-offset="handleUpdateOffset"
          @drawing-state="handleDrawingState"
        />
      </div>

      <!-- Правая панель - свойства объекта -->
      <PropertiesPanel
        :selected-object="selectedObject"
        @update="handleUpdateObject"
        @delete="handleDeleteObject"
      />
    </div>

    <!-- Нижняя панель с подсказками (общая для всех панелей) -->
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useRoomEditorStore } from '@/stores/roomEditor'
import { useNotificationStore } from '@/stores/notifications'
import { roomObjectsAPI } from '@/services/roomObjects'

import EditorToolbar from './EditorToolbar.vue'
import ObjectPalette from './ObjectPalette.vue'
import WallDrawingCanvas from './WallDrawingCanvas.vue'
import PropertiesPanel from './PropertiesPanel.vue'

const router = useRouter()
const route = useRoute()
const editorStore = useRoomEditorStore()
const notificationStore = useNotificationStore()

// Состояние рисования (получаем от WallDrawingCanvas)
const isDrawing = ref(false)
const currentLineLength = ref('0')
const snapToGrid = ref(true) // Привязка к сетке

// Обработчик состояния рисования
const handleDrawingState = (state) => {
  isDrawing.value = state.isDrawing
  currentLineLength.value = state.currentLineLength
}

// Обработчик переключения привязки к сетке
const handleToggleSnap = (enabled) => {
  snapToGrid.value = enabled
}

// Обработчик переключения отображения сетки
const handleToggleGrid = (enabled) => {
  editorStore.showGrid = enabled
}

// Единый метод для перерисовки холста
const requestRedraw = () => {
  setTimeout(() => {
    const canvas = document.querySelector('.wall-canvas')
    if (canvas && canvas._konva) {
      canvas._konva.batchDraw()
    }
  }, 100)
}

// Состояние из store
const currentRoom = computed(() => editorStore.currentRoom)
const objects = computed(() => editorStore.objects)
const selectedObject = computed(() => editorStore.selectedObject)
const currentTool = computed(() => editorStore.currentTool)
const zoom = computed(() => editorStore.zoom)
const offset = computed(() => editorStore.offset)
const gridSize = computed(() => editorStore.gridSize)
const showGrid = computed(() => editorStore.showGrid)
const fieldWidth = computed(() => editorStore.fieldWidth)
const fieldHeight = computed(() => editorStore.fieldHeight)
const canUndo = computed(() => editorStore.canUndo)
const canRedo = computed(() => editorStore.canRedo)

// === Методы ===

const handleSelectTool = (tool) => {
  editorStore.setTool(tool)
}

const handleSelectObject = (object) => {
  editorStore.selectObject(object)
}

const handleUpdateFieldSize = (dimension, value) => {
  const numValue = parseInt(value)
  if (dimension === 'width' && !isNaN(numValue)) {
    editorStore.setFieldWidth(numValue)
  } else if (dimension === 'height' && !isNaN(numValue)) {
    editorStore.setFieldHeight(numValue)
  }
}

const handleAddObject = (object) => {
  editorStore.addObject(object)
  requestRedraw()
}

const handleUpdateZoom = (newZoom) => {
  editorStore.setZoom(newZoom)
}

const handleUpdateOffset = (newOffset) => {
  editorStore.setOffset(newOffset)
}

const handleUpdateObject = (objectId, updates) => {
  editorStore.updateObject(objectId, updates)
}

const handleDeleteObject = (objectId) => {
  editorStore.deleteObject(objectId)
}

const handleUndo = () => {
  editorStore.undo()
}

const handleRedo = () => {
  editorStore.redo()
}

const handleSave = async () => {
  if (!currentRoom.value) {
    notificationStore.error('Помещение не выбрано', 'Ошибка')
    return
  }

  console.log('Сохранение плана. Объекты:', objects.value)
  console.log('Размеры поля:', fieldWidth.value, fieldHeight.value)

  try {
    await roomObjectsAPI.saveRoomPlan(
      currentRoom.value.id,
      objects.value,
      fieldWidth.value,
      fieldHeight.value
    )
    notificationStore.success('План помещения сохранен', 'Успешно')
  } catch (error) {
    console.error('Ошибка сохранения плана:', error)
    notificationStore.error('Не удалось сохранить план помещения', 'Ошибка')
  }
}

const handleClear = async () => {
  if (!currentRoom.value) {
    notificationStore.error('Помещение не выбрано', 'Ошибка')
    return
  }

  if (!confirm('Вы уверены, что хотите удалить все объекты на плане? Это действие нельзя отменить.')) {
    return
  }

  try {
    await roomObjectsAPI.clearRoomPlan(currentRoom.value.id)
    editorStore.clearEditor()
    editorStore.setCurrentRoom(currentRoom.value)
    notificationStore.success('План помещения очищен', 'Успешно')
  } catch (error) {
    console.error('Ошибка очистки плана:', error)
    notificationStore.error('Не удалось очистить план помещения', 'Ошибка')
  }
}

const handleCancel = () => {
  router.push('/admin')
}

// === Загрузка данных ===

const loadRoomData = async () => {
  const roomId = route.params.roomId

  if (!roomId) {
    notificationStore.error('ID помещения не указан', 'Ошибка')
    router.push('/admin')
    return
  }

  try {
    // Получаем план помещения
    const plan = await roomObjectsAPI.getRoomPlan(roomId)
    console.log('Загруженный план:', plan)
    
    editorStore.loadObjects(plan.objects || [])

    // Восстанавливаем размеры поля если они сохранены
    if (plan.fieldWidth) {
      editorStore.setFieldWidth(plan.fieldWidth)
    }
    if (plan.fieldHeight) {
      editorStore.setFieldHeight(plan.fieldHeight)
    }

    editorStore.setCurrentRoom({ id: roomId })
    
    // Перерисовываем холст после загрузки
    requestRedraw()
  } catch (error) {
    console.error('Ошибка загрузки плана:', error)
    // Если план не найден, продолжаем с пустым редактором
    editorStore.setCurrentRoom({ id: roomId })
  }
}

onMounted(() => {
  loadRoomData()
})
</script>

<style scoped>
.room-editor {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f5f5;
}

.editor-body {
  display: flex;
  flex: 1;
  overflow: hidden;
  min-width: fit-content;
}

.canvas-wrapper {
  flex: 1;
  overflow: hidden;
  background: #f5f5f5;
  position: relative;
  min-width: 0;
}
</style>
