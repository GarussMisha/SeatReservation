/**
 * EditorCanvas - холст для рисования плана помещения
 * Использует vue-konva для рендеринга
 * 
 * Исправления:
 * - Бесконечная сетка
 * - Перемещение на средней кнопке мыши
 * - Выравнивание по сетке
 */
<template>
  <div class="editor-canvas" ref="canvasContainer" :style="{ cursor: canvasCursor }">
    <v-stage
      ref="stage"
      :config="stageConfig"
      @mousedown="handleStageMouseDown"
      @mousemove="handleStageMouseMove"
      @mouseup="handleStageMouseUp"
      @touchstart="handleStageMouseDown"
      @touchmove="handleStageMouseMove"
      @touchend="handleStageMouseUp"
      @wheel="handleWheel"
      @contentMousedown="handleContentMouseDown"
    >
      <!-- Слой с сеткой -->
      <v-layer ref="gridLayer">
        <!-- Белый фон -->
        <v-rect
          :config="{
            x: -10000,
            y: -10000,
            width: 20000,
            height: 20000,
            fill: '#ffffff'
          }"
        />
        
        <!-- Рисуем сетку -->
        <v-group v-if="showGrid">
          <v-line
            v-for="i in gridLinesX"
            :key="'v' + i"
            :config="{
              points: [i * gridSize, -10000, i * gridSize, 10000],
              stroke: '#e0e0e0',
              strokeWidth: 1
            }"
          />
          <v-line
            v-for="i in gridLinesY"
            :key="'h' + i"
            :config="{
              points: [-10000, i * gridSize, 10000, i * gridSize],
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
            draggable: currentTool === 'select' && !isPanning,
            shadowBlur: wall.id === selectedObjectId ? 10 : 0,
            shadowColor: 'blue'
          }"
          @click="() => selectObject(wall)"
          @dragstart="handleDragStart"
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
            draggable: currentTool === 'select' && !isPanning,
            shadowBlur: door.id === selectedObjectId ? 10 : 0
          }"
          @click="() => selectObject(door)"
          @dragstart="handleDragStart"
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
            draggable: currentTool === 'select' && !isPanning,
            shadowBlur: window.id === selectedObjectId ? 10 : 0
          }"
          @click="() => selectObject(window)"
          @dragstart="handleDragStart"
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
            draggable: currentTool === 'select' && !isPanning,
            shadowBlur: workspace.id === selectedObjectId ? 10 : 0,
            cornerRadius: 4
          }"
          @click="() => selectObject(workspace)"
          @dragstart="handleDragStart"
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
            draggable: currentTool === 'select' && !isPanning,
            shadowBlur: obj.id === selectedObjectId ? 10 : 0,
            cornerRadius: 4
          }"
          @click="() => selectObject(obj)"
          @dragstart="handleDragStart"
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

        <!-- Линия для рисования стены (превью) -->
        <v-line
          v-if="isDrawingWall && wallPreview.length > 0"
          :config="{
            points: wallPreview,
            stroke: '#2196F3',
            strokeWidth: 4,
            dash: [10, 5],
            lineCap: 'round',
            lineJoin: 'round'
          }"
        />
      </v-layer>
    </v-stage>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

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
const isPanning = ref(false)
const isDrawingWall = ref(false)
const wallPreview = ref([])
const canvasCursor = ref('default')

const stageWidth = computed(() => canvasContainer.value?.clientWidth || 800)
const stageHeight = computed(() => canvasContainer.value?.clientHeight || 600)

// Бесконечная сетка - рисуем линии с большим запасом
const gridLinesX = computed(() => Math.ceil(stageWidth.value / props.gridSize) * 2)
const gridLinesY = computed(() => Math.ceil(stageHeight.value / props.gridSize) * 2)

const selectedObjectId = computed(() => {
  const selected = props.objects.find(obj => obj.selected)
  return selected?.id || null
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

// === Выравнивание по сетке ===

const snapToGrid = (value) => {
  return Math.round(value / props.gridSize) * props.gridSize
}

// === Обработчики событий ===

const selectObject = (object) => {
  emit('select-object', object)
}

const handleContentMouseDown = (e) => {
  // Средняя кнопка мыши (колесико) - начало перемещения
  if (e.evt.button === 1) {
    e.evt.preventDefault()
    isPanning.value = true
    canvasCursor.value = 'grabbing'
    
    const stageInstance = stage.value.getNode()
    stageInstance.draggable(true)
    stageInstance.setDragBoundFunc((pos) => {
      emit('set-offset', pos)
      return pos
    })
  }
}

const handleStageMouseDown = (e) => {
  // Левая кнопка мыши
  if (e.evt.button === 0) {
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
        const snappedX = snapToGrid(x)
        const snappedY = snapToGrid(y)
        
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
}

const handleStageMouseMove = (e) => {
  // Обновление позиции при перемещении
  if (isPanning.value) {
    const stageInstance = stage.value.getNode()
    emit('set-offset', {
      x: stageInstance.x(),
      y: stageInstance.y()
    })
  }
}

const handleStageMouseUp = (e) => {
  // Завершение перемещения
  if (e.evt.button === 1 || e.evt.button === undefined) {
    isPanning.value = false
    canvasCursor.value = 'default'
    
    const stageInstance = stage.value.getNode()
    stageInstance.draggable(false)
    stageInstance.setDragBoundFunc(null)
  }
}

const handleDragStart = (e) => {
  // При начале перетаскивания объекта
  if (isPanning.value) {
    e.target.stopDrag()
  }
}

const handleDragEnd = (object, evt) => {
  const node = evt.target
  const x = node.x()
  const y = node.y()
  
  // Скругляем до сетки
  const snappedX = snapToGrid(x)
  const snappedY = snapToGrid(y)
  
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

// === Обновление курсора ===

watch(() => props.currentTool, (newTool) => {
  if (newTool === 'select') {
    canvasCursor.value = 'default'
  } else if (newTool === 'wall') {
    canvasCursor.value = 'crosshair'
  } else {
    canvasCursor.value = 'copy'
  }
})

// === Глобальные обработчики для перемещения на средней кнопке ===

// Добавляем глобальные обработчики при монтировании
const addGlobalListeners = () => {
  const container = canvasContainer.value
  if (!container) return
  
  container.addEventListener('mousedown', (evt) => {
    // Средняя кнопка мыши (button === 1)
    if (evt.button === 1) {
      evt.preventDefault()
      isPanning.value = true
      canvasCursor.value = 'grabbing'
      
      const stageInstance = stage.value?.getNode()
      if (stageInstance) {
        stageInstance.draggable(true)
      }
    }
  })
  
  container.addEventListener('mouseup', (evt) => {
    if (evt.button === 1) {
      isPanning.value = false
      canvasCursor.value = 'default'
      
      const stageInstance = stage.value?.getNode()
      if (stageInstance) {
        stageInstance.draggable(false)
      }
    }
  })
  
  container.addEventListener('mousemove', (evt) => {
    if (isPanning.value) {
      evt.preventDefault()
      const stageInstance = stage.value?.getNode()
      if (stageInstance) {
        const pos = stageInstance.position()
        emit('set-offset', pos)
      }
    }
  })
  
  // Блокируем контекстное меню при нажатии колесика
  container.addEventListener('contextmenu', (evt) => {
    evt.preventDefault()
  })
}

onMounted(() => {
  addGlobalListeners()
})
</script>

<style scoped>
.editor-canvas {
  flex: 1;
  background: #f5f5f5;
  overflow: hidden;
  position: relative;
}

.editor-canvas :deep(canvas) {
  outline: none;
}
</style>
