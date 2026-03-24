/**
 * EditorCanvas - холст для рисования плана помещения
 * Использует vue-konva для рендеринга
 */
<template>
  <div class="editor-canvas" ref="canvasContainer">
    <v-stage
      ref="stage"
      :config="stageConfig"
      @mousedown="handleStageMouseDown"
      @touchstart="handleStageMouseDown"
      @wheel="handleWheel"
    >
      <!-- Слой с сеткой -->
      <v-layer ref="gridLayer">
        <v-rect
          v-if="showGrid"
          :config="{
            x: 0,
            y: 0,
            width: stageWidth,
            height: stageHeight,
            fill: 'white'
          }"
        />
        <!-- Рисуем сетку -->
        <v-group v-if="showGrid">
          <v-line
            v-for="i in gridLinesX"
            :key="'v' + i"
            :config="{
              points: [i * gridSize, 0, i * gridSize, stageHeight],
              stroke: '#e0e0e0',
              strokeWidth: 1
            }"
          />
          <v-line
            v-for="i in gridLinesY"
            :key="'h' + i"
            :config="{
              points: [0, i * gridSize, stageWidth, i * gridSize],
              stroke: '#e0e0e0',
              strokeWidth: 1
            }"
          />
        </v-group>
      </v-layer>

      <!-- Слой с объектами -->
      <v-layer ref="objectsLayer">
        <!-- Стены -->
        <v-rect
          v-for="wall in walls"
          :key="wall.id"
          :config="{
            ...getWallConfig(wall),
            fill: wall.id === selectedObjectId ? '#2196F3' : '#9e9e9e',
            stroke: wall.id === selectedObjectId ? '#1976D2' : '#757575',
            strokeWidth: wall.id === selectedObjectId ? 3 : 2,
            draggable: currentTool === 'select',
            shadowBlur: wall.id === selectedObjectId ? 10 : 0,
            shadowColor: 'blue'
          }"
          @click="() => selectObject(wall)"
          @dragend="handleDragEnd(wall, $evt)"
        />

        <!-- Двери -->
        <v-rect
          v-for="door in doors"
          :key="door.id"
          :config="{
            ...getObjectConfig(door),
            fill: door.id === selectedObjectId ? '#2196F3' : '#FF9800',
            stroke: door.id === selectedObjectId ? '#1976D2' : '#F57C00',
            strokeWidth: door.id === selectedObjectId ? 3 : 2,
            draggable: currentTool === 'select',
            shadowBlur: door.id === selectedObjectId ? 10 : 0
          }"
          @click="() => selectObject(door)"
          @dragend="handleDragEnd(door, $evt)"
        />

        <!-- Окна -->
        <v-rect
          v-for="window in windows"
          :key="window.id"
          :config="{
            ...getObjectConfig(window),
            fill: window.id === selectedObjectId ? '#2196F3' : '#4FC3F7',
            stroke: window.id === selectedObjectId ? '#1976D2' : '#039BE5',
            strokeWidth: window.id === selectedObjectId ? 3 : 2,
            draggable: currentTool === 'select',
            shadowBlur: window.id === selectedObjectId ? 10 : 0
          }"
          @click="() => selectObject(window)"
          @dragend="handleDragEnd(window, $evt)"
        />

        <!-- Рабочие места -->
        <v-rect
          v-for="workspace in workspaces"
          :key="workspace.id"
          :config="{
            ...getObjectConfig(workspace),
            fill: workspace.id === selectedObjectId ? '#2196F3' : '#4CAF50',
            stroke: workspace.id === selectedObjectId ? '#1976D2' : '#388E3C',
            strokeWidth: workspace.id === selectedObjectId ? 3 : 2,
            draggable: currentTool === 'select',
            shadowBlur: workspace.id === selectedObjectId ? 10 : 0,
            cornerRadius: 4
          }"
          @click="() => selectObject(workspace)"
          @dragend="handleDragEnd(workspace, $evt)"
        >
          <!-- Текст с названием -->
          <v-text
            :config="{
              text: workspace.name || 'Место',
              fontSize: 10,
              fontFamily: 'Arial',
              fill: '#333',
              align: 'center',
              verticalAlign: 'middle',
              width: workspace.width,
              height: workspace.height,
              listening: false
            }"
          />
        </v-rect>

        <!-- Другие объекты -->
        <v-rect
          v-for="obj in otherObjects"
          :key="obj.id"
          :config="{
            ...getObjectConfig(obj),
            fill: obj.id === selectedObjectId ? '#2196F3' : '#9C27B0',
            stroke: obj.id === selectedObjectId ? '#1976D2' : '#7B1FA2',
            strokeWidth: obj.id === selectedObjectId ? 3 : 2,
            draggable: currentTool === 'select',
            shadowBlur: obj.id === selectedObjectId ? 10 : 0,
            cornerRadius: 4
          }"
          @click="() => selectObject(obj)"
          @dragend="handleDragEnd(obj, $evt)"
        >
          <v-text
            :config="{
              text: getObjectName(obj.object_type),
              fontSize: 10,
              fontFamily: 'Arial',
              fill: '#333',
              align: 'center',
              verticalAlign: 'middle',
              width: obj.width,
              height: obj.height,
              listening: false
            }"
          />
        </v-rect>

        <!-- Трансформер для выделения -->
        <v-transformer
          v-if="selectedObjectId"
          ref="transformer"
          :config="{
            nodes: transformerNodes,
            padding: 5,
            borderStroke: '#2196F3',
            borderDash: [4, 4],
            anchorStroke: '#2196F3',
            anchorFill: '#ffffff',
            anchorSize: 10,
            rotateAnchorOffset: 30
          }"
        />
      </v-layer>
    </v-stage>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  objects: {
    type: Array,
    default: () => []
  },
  zoom: {
    type: Number,
    default: 1
  },
  offset: {
    type: Object,
    default: () => ({ x: 0, y: 0 })
  },
  currentTool: {
    type: String,
    default: 'select'
  },
  gridSize: {
    type: Number,
    default: 20
  },
  showGrid: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits([
  'select-object',
  'update-object',
  'delete-object',
  'add-object',
  'set-offset',
  'set-zoom'
])

const canvasContainer = ref(null)
const stage = ref(null)
const transformer = ref(null)

const stageWidth = computed(() => canvasContainer.value?.clientWidth || 800)
const stageHeight = computed(() => canvasContainer.value?.clientHeight || 600)

const gridLinesX = computed(() => Math.ceil(stageWidth.value / props.gridSize))
const gridLinesY = computed(() => Math.ceil(stageHeight.value / props.gridSize))

const selectedObjectId = computed(() => {
  const selected = props.objects.find(obj => obj.selected)
  return selected?.id || null
})

const transformerNodes = computed(() => {
  if (!selectedObjectId.value) return []
  // В реальной реализации нужно возвращать Konva.Node
  return []
})

// Фильтрация объектов по типам
const walls = computed(() => props.objects.filter(obj => obj.object_type === 'wall'))
const doors = computed(() => props.objects.filter(obj => obj.object_type === 'door'))
const windows = computed(() => props.objects.filter(obj => obj.object_type === 'window'))
const workspaces = computed(() => props.objects.filter(obj => obj.object_type === 'workspace'))
const otherObjects = computed(() => props.objects.filter(obj =>
  !['wall', 'door', 'window', 'workspace'].includes(obj.object_type)
))

const stageConfig = computed(() => ({
  width: stageWidth.value,
  height: stageHeight.value,
  scaleX: props.zoom,
  scaleY: props.zoom,
  x: props.offset.x,
  y: props.offset.y
}))

// === Конфигурация объектов ===

const getWallConfig = (wall) => ({
  x: wall.x,
  y: wall.y,
  width: wall.width || 200,
  height: wall.height || 10,
  rotation: wall.rotation || 0
})

const getObjectConfig = (obj) => ({
  x: obj.x,
  y: obj.y,
  width: obj.width || 100,
  height: obj.height || 50,
  rotation: obj.rotation || 0
})

const getObjectName = (type) => {
  const names = {
    printer: 'Принтер',
    kitchen: 'Кухня',
    meeting_room: 'Переговорка',
    staircase: 'Лестница',
    restroom: 'Отдых'
  }
  return names[type] || type
}

// === Обработчики событий ===

const selectObject = (object) => {
  emit('select-object', object)
}

const handleStageMouseDown = (e) => {
  // Клик на пустом месте - снимаем выделение
  if (e.target === e.target.getStage()) {
    emit('select-object', null)
    
    // Если активен инструмент добавления
    if (props.currentTool !== 'select') {
      // Получаем координаты с учетом масштаба и смещения
      const pos = e.target.getStage().getPointerPosition()
      const x = (pos.x - props.offset.x) / props.zoom
      const y = (pos.y - props.offset.y) / props.zoom
      
      // Скругляем до сетки
      const snappedX = Math.round(x / props.gridSize) * props.gridSize
      const snappedY = Math.round(y / props.gridSize) * props.gridSize
      
      // Создаем новый объект
      const newObject = {
        object_type: props.currentTool,
        x: snappedX,
        y: snappedY,
        width: props.currentTool === 'wall' ? 200 : 100,
        height: props.currentTool === 'wall' ? 10 : 50,
        rotation: 0,
        name: '',
        is_active: true
      }
      
      emit('add-object', newObject)
    }
  }
}

const handleDragEnd = (object, evt) => {
  const node = evt.target
  const x = node.x()
  const y = node.y()
  
  // Скругляем до сетки
  const snappedX = Math.round(x / props.gridSize) * props.gridSize
  const snappedY = Math.round(y / props.gridSize) * props.gridSize
  
  node.x(snappedX)
  node.y(snappedY)
  
  emit('update-object', object.id, { x: snappedX, y: snappedY })
}

const handleWheel = (e) => {
  e.evt.preventDefault()
  
  const scaleBy = 1.1
  const stageInstance = stage.value.getNode()
  const oldScale = props.zoom
  const pointer = stageInstance.getPointerPosition()
  
  const mousePointTo = {
    x: (pointer.x - props.offset.x) / oldScale,
    y: (pointer.y - props.offset.y) / oldScale
  }
  
  const newScale = e.evt.deltaY < 0 ? oldScale * scaleBy : oldScale / scaleBy
  const clampedScale = Math.max(0.1, Math.min(5, newScale))
  
  emit('set-zoom', clampedScale)
  emit('set-offset', {
    x: pointer.x - mousePointTo.x * clampedScale,
    y: pointer.y - mousePointTo.y * clampedScale
  })
}
</script>

<style scoped>
.editor-canvas {
  flex: 1;
  background: #f5f5f5;
  overflow: hidden;
}

.editor-canvas :deep(canvas) {
  cursor: crosshair;
}

.editor-canvas :deep(canvas.select) {
  cursor: default;
}
</style>
