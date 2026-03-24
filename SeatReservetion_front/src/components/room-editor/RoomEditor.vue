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
      @cancel="handleCancel"
    />

    <div class="editor-body">
      <!-- Левая панель - палитра объектов -->
      <ObjectPalette
        :current-tool="currentTool"
        @select-tool="handleSelectTool"
      />

      <!-- Центральная область - холст -->
      <EditorCanvas
        :objects="objects"
        :zoom="zoom"
        :offset="offset"
        :current-tool="currentTool"
        :grid-size="gridSize"
        :show-grid="showGrid"
        @select-object="handleSelectObject"
        @update-object="handleUpdateObject"
        @delete-object="handleDeleteObject"
        @add-object="handleAddObject"
        @set-offset="handleSetOffset"
        @set-zoom="handleSetZoom"
      />

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
import EditorCanvas from './EditorCanvas.vue'
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
const canUndo = computed(() => editorStore.canUndo)
const canRedo = computed(() => editorStore.canRedo)

// === Методы ===

const handleSelectTool = (tool) => {
  editorStore.setTool(tool)
}

const handleSelectObject = (object) => {
  editorStore.selectObject(object)
}

const handleAddObject = (object) => {
  editorStore.addObject(object)
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
</style>
