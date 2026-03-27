/**
 * RoomEditor - главный компонент редактора помещений
 * Предоставляет интерфейс для создания плана помещения
 */
<template>
  <div class="room-editor">
    <!-- Верхняя панель инструментов -->
    <EditorToolbar
      :zoom="zoom"
      :can-undo="canUndo"
      :can-redo="canRedo"
      @zoom-in="handleZoomIn"
      @zoom-out="handleZoomOut"
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
        @select-tool="handleSelectTool"
        @update-field-size="handleUpdateFieldSize"
      />

      <!-- Центральная область - холст -->
      <div class="canvas-wrapper">
        <WallDrawingCanvas
          :current-tool="currentTool"
          :grid-size="gridSize"
          @wall-completed="handleWallCompleted"
        />
      </div>

      <!-- Правая панель - свойства объекта -->
      <PropertiesPanel
        :selected-object="selectedObject"
        @update="handleUpdateObject"
        @delete="handleDeleteObject"
      />
    </div>
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
  
  // Принудительно перерисовываем холст после добавления объекта
  setTimeout(() => {
    const canvas = document.querySelector('.editor-canvas canvas')
    if (canvas) {
      const stage = canvas._konva
      if (stage) {
        const objectsLayer = stage.findOne('.objectsLayer')
        if (objectsLayer) {
          objectsLayer.batchDraw()
        }
      }
    }
  }, 0)
}

const handleWallCompleted = (wall) => {
  notificationStore.success(`Стена добавлена (${wall.points.length} точек)`, 'Успешно')
}

const handleUpdateObject = (objectId, updates) => {
  editorStore.updateObject(objectId, updates)
}

const handleDeleteObject = (objectId) => {
  editorStore.deleteObject(objectId)
}

const handleSetOffset = (newOffset) => {
  editorStore.setOffset(newOffset)
}

const handleSetZoom = (newZoom) => {
  editorStore.setZoom(newZoom)
}

const handleZoomIn = () => {
  editorStore.setZoom(zoom.value + 0.1)
}

const handleZoomOut = () => {
  editorStore.setZoom(zoom.value - 0.1)
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

  try {
    await roomObjectsAPI.saveRoomPlan(currentRoom.value.id, objects.value)
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
    editorStore.loadObjects(plan.objects || [])
    editorStore.setCurrentRoom({ id: roomId })
  } catch (error) {
    console.error('Ошибка загрузки плана:', error)
    // Если план не найден, продолжаем с пустым редактором
    editorStore.setCurrentRoom({ id: roomId })
  }
}

onMounted(() => {
  loadRoomData()
})

onUnmounted(() => {
  editorStore.clearEditor()
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
}

.canvas-wrapper {
  flex: 1;
  overflow: hidden;
  background: #f5f5f5;
  position: relative;
}
</style>
