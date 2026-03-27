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
      <!-- Слой 1: Белый фон (самый нижний) -->
      <v-layer ref="backgroundLayer">
        <v-rect
          :config="{
            x: -50000,
            y: -50000,
            width: 100000,
            height: 100000,
            fill: '#ffffff'
          }"
        />
      </v-layer>

      <!-- Слой 2: Сетка -->
      <v-layer ref="gridLayer">
        <v-group v-if="showGrid">
          <!-- Ограниченная сетка -->
          <v-line
            v-for="i in Math.ceil(fieldWidth)"
            :key="'v' + i"
            :config="{
              points: [i * gridSize, 0, i * gridSize, fieldHeight * gridSize],
              stroke: '#e0e0e0',
              strokeWidth: 1
            }"
          />
          <v-line
            v-for="i in Math.ceil(fieldHeight)"
            :key="'h' + i"
            :config="{
              points: [0, i * gridSize, fieldWidth * gridSize, i * gridSize],
              stroke: '#e0e0e0',
              strokeWidth: 1
            }"
          />
        </v-group>
        
        <!-- Границы поля -->
        <v-rect
          :config="{
            x: 0,
            y: 0,
            width: fieldWidth * gridSize,
            height: fieldHeight * gridSize,
            stroke: '#4CAF50',
            strokeWidth: 3,
            dash: [10, 5],
            listening: false
          }"
        />
        
        <!-- Подписи размеров -->
        <v-text
          :config="{
            text: fieldWidth + ' клеток (' + (fieldWidth * 0.5) + 'м)',
            x: fieldWidth * gridSize / 2,
            y: -10,
            fontSize: 12,
            fontFamily: 'Arial',
            fill: '#4CAF50',
            align: 'center',
            listening: false
          }"
        />
        <v-text
          :config="{
            text: fieldHeight + ' клеток (' + (fieldHeight * 0.5) + 'м)',
            x: -10,
            y: fieldHeight * gridSize / 2,
            fontSize: 12,
            fontFamily: 'Arial',
            fill: '#4CAF50',
            align: 'center',
            rotation: -90,
            listening: false
          }"
        />
      </v-layer>

      <!-- Слой 3: Объекты (самый верхний) -->
      <v-layer ref="objectsLayer">
        <!-- Стены - черные прямоугольники -->
        <v-rect
          v-for="wall in walls"
          :key="wall.id"
          :config="{
            ...getWallConfig(wall),
            fill: '#000000',
            stroke: wall.id === selectedObjectId ? '#2196F3' : '#000000',
            strokeWidth: wall.id === selectedObjectId ? 3 : 1,
            draggable: currentTool === 'select' && !isPanning,
            shadowBlur: wall.id === selectedObjectId ? 5 : 0,
            shadowColor: '#000000'
          }"
          @click="() => selectObject(wall)"
          @dragstart="handleDragStart"
          @dragend="(e) => handleDragEnd(wall, e)"
          @tap="() => selectObject(wall)"
        />

        <!-- Двери - дуга открытия + прямоугольник полотна -->
        <v-group
          v-for="door in doors"
          :key="door.id"
          :config="{
            x: door.x,
            y: door.y,
            rotation: door.rotation || 0,
            draggable: currentTool === 'select' && !isPanning
          }"
          @click="() => selectObject(door)"
          @dragstart="handleDragStart"
          @dragend="(e) => handleDragEnd(door, e)"
          @tap="() => selectObject(door)"
        >
          <!-- Полотно двери -->
          <v-rect
            :config="{
              x: 0,
              y: 0,
              width: door.width || 80,
              height: 4,
              fill: '#000000',
              stroke: door.id === selectedObjectId ? '#2196F3' : '#000000',
              strokeWidth: door.id === selectedObjectId ? 3 : 1
            }"
          />
          <!-- Дуга открытия двери -->
          <v-arc
            :config="{
              x: 0,
              y: 0,
              radius: door.width || 80,
              angle: 90,
              stroke: '#666666',
              strokeWidth: 1,
              dash: [5, 5]
            }"
          />
          <!-- Линия траектории -->
          <v-line
            :config="{
              points: [0, 0, 0, -(door.width || 80)],
              stroke: '#666666',
              strokeWidth: 1,
              dash: [3, 3]
            }"
          />
        </v-group>

        <!-- Окна - прямоугольник с диагональными линиями -->
        <v-group
          v-for="window in windows"
          :key="window.id"
          :config="{
            x: window.x,
            y: window.y,
            rotation: window.rotation || 0,
            draggable: currentTool === 'select' && !isPanning
          }"
          @click="() => selectObject(window)"
          @dragstart="handleDragStart"
          @dragend="(e) => handleDragEnd(window, e)"
          @tap="() => selectObject(window)"
        >
          <!-- Основная рамка окна -->
          <v-rect
            :config="{
              x: 0,
              y: 0,
              width: window.width || 200,
              height: window.height || 10,
              fill: '#ffffff',
              stroke: window.id === selectedObjectId ? '#2196F3' : '#000000',
              strokeWidth: window.id === selectedObjectId ? 3 : 2
            }"
          />
          <!-- Диагональные линии (штриховка стекла) -->
          <v-line
            :config="{
              points: [5, 0, window.width - 5, window.height],
              stroke: '#666666',
              strokeWidth: 1
            }"
          />
          <v-line
            :config="{
              points: [window.width - 5, 0, 5, window.height],
              stroke: '#666666',
              strokeWidth: 1
            }"
          />
        </v-group>

        <!-- Рабочие места - прямоугольник со стулом (полукруг) -->
        <v-group
          v-for="workspace in workspaces"
          :key="workspace.id"
          :config="{
            x: workspace.x,
            y: workspace.y,
            rotation: workspace.rotation || 0,
            draggable: currentTool === 'select' && !isPanning
          }"
          @click="() => selectObject(workspace)"
          @dragstart="handleDragStart"
          @dragend="(e) => handleDragEnd(workspace, e)"
          @tap="() => selectObject(workspace)"
        >
          <!-- Стол - прямоугольник -->
          <v-rect
            :config="{
              x: 20,
              y: 10,
              width: 50,
              height: 30,
              stroke: workspace.id === selectedObjectId ? '#2196F3' : '#757575',
              strokeWidth: workspace.id === selectedObjectId ? 3 : 3,
              fill: 'none',
              cornerRadius: 4
            }"
          />
          <!-- Стул - полукруг с широкой стороны стола -->
          <v-arc
            :config="{
              x: 70,
              y: 25,
              radius: 12,
              angle: 180,
              stroke: '#757575',
              strokeWidth: 3,
              fill: 'none',
              rotation: 90
            }"
          />
        </v-group>

        <!-- Принтер - прямоугольник с надписью -->
        <v-rect
          v-for="printer in printers"
          :key="printer.id"
          :config="{
            x: printer.x,
            y: printer.y,
            rotation: printer.rotation || 0,
            width: printer.width || 100,
            height: printer.height || 50,
            stroke: printer.id === selectedObjectId ? '#2196F3' : '#757575',
            strokeWidth: printer.id === selectedObjectId ? 3 : 3,
            fill: 'none',
            cornerRadius: 8,
            draggable: currentTool === 'select' && !isPanning
          }"
          @click="() => selectObject(printer)"
          @dragstart="handleDragStart"
          @dragend="(e) => handleDragEnd(printer, e)"
          @tap="() => selectObject(printer)"
        />

        <!-- Переговорные -->
        <v-image
          v-for="meeting in meetingRooms"
          :key="meeting.id"
          :config="{
            x: meeting.x,
            y: meeting.y,
            rotation: meeting.rotation || 0,
            image: getIconImage('meeting_room'),
            width: 40,
            height: 40,
            offset: { x: 20, y: 20 },
            draggable: currentTool === 'select' && !isPanning
          }"
          @click="() => selectObject(meeting)"
          @dragstart="handleDragStart"
          @dragend="(e) => handleDragEnd(meeting, e)"
          @tap="() => selectObject(meeting)"
        />

        <!-- Кухня -->
        <v-image
          v-for="kitchen in kitchens"
          :key="kitchen.id"
          :config="{
            x: kitchen.x,
            y: kitchen.y,
            rotation: kitchen.rotation || 0,
            image: getIconImage('kitchen'),
            width: 40,
            height: 40,
            offset: { x: 20, y: 20 },
            draggable: currentTool === 'select' && !isPanning
          }"
          @click="() => selectObject(kitchen)"
          @dragstart="handleDragStart"
          @dragend="(e) => handleDragEnd(kitchen, e)"
          @tap="() => selectObject(kitchen)"
        />

        <!-- Лестница -->
        <v-image
          v-for="staircase in staircases"
          :key="staircase.id"
          :config="{
            x: staircase.x,
            y: staircase.y,
            rotation: staircase.rotation || 0,
            image: getIconImage('ladder'),
            width: 40,
            height: 40,
            offset: { x: 20, y: 20 },
            draggable: currentTool === 'select' && !isPanning
          }"
          @click="() => selectObject(staircase)"
          @dragstart="handleDragStart"
          @dragend="(e) => handleDragEnd(staircase, e)"
          @tap="() => selectObject(staircase)"
        />

        <!-- Раздевалка -->
        <v-image
          v-for="restroom in restrooms"
          :key="restroom.id"
          :config="{
            x: restroom.x,
            y: restroom.y,
            rotation: restroom.rotation || 0,
            image: getIconImage('hanger'),
            width: 40,
            height: 40,
            offset: { x: 20, y: 20 },
            draggable: currentTool === 'select' && !isPanning
          }"
          @click="() => selectObject(restroom)"
          @dragstart="handleDragStart"
          @dragend="(e) => handleDragEnd(restroom, e)"
          @tap="() => selectObject(restroom)"
        />

        <!-- Женский туалет -->
        <v-image
          v-for="toiletFemale in toiletsFemale"
          :key="toiletFemale.id"
          :config="{
            x: toiletFemale.x,
            y: toiletFemale.y,
            rotation: toiletFemale.rotation || 0,
            image: getIconImage('toilet_woman'),
            width: 40,
            height: 40,
            offset: { x: 20, y: 20 },
            draggable: currentTool === 'select' && !isPanning
          }"
          @click="() => selectObject(toiletFemale)"
          @dragstart="handleDragStart"
          @dragend="(e) => handleDragEnd(toiletFemale, e)"
          @tap="() => selectObject(toiletFemale)"
        />

        <!-- Мужской туалет -->
        <v-image
          v-for="toiletMale in toiletsMale"
          :key="toiletMale.id"
          :config="{
            x: toiletMale.x,
            y: toiletMale.y,
            rotation: toiletMale.rotation || 0,
            image: getIconImage('toilet_man'),
            width: 40,
            height: 40,
            offset: { x: 20, y: 20 },
            draggable: currentTool === 'select' && !isPanning
          }"
          @click="() => selectObject(toiletMale)"
          @dragstart="handleDragStart"
          @dragend="(e) => handleDragEnd(toiletMale, e)"
          @tap="() => selectObject(toiletMale)"
        />

        <!-- Другие объекты - серый прямоугольник -->
        <v-rect
          v-for="obj in otherObjects"
          :key="obj.id"
          :config="{
            ...getObjectConfig(obj),
            fill: '#f5f5f5',
            stroke: '#000000',
            strokeWidth: 2,
            draggable: currentTool === 'select' && !isPanning,
            cornerRadius: 2
          }"
          @click="() => selectObject(obj)"
          @dragstart="handleDragStart"
          @dragend="(e) => handleDragEnd(obj, e)"
          @tap="() => selectObject(obj)"
        >
          <v-text
            :config="{
              text: getObjectName(obj.object_type),
              fontSize: 11,
              fontFamily: 'Arial',
              fill: '#000000',
              align: 'center',
              verticalAlign: 'middle',
              width: obj.width,
              height: obj.height,
              listening: false
            }"
          />
        </v-rect>

        <!-- SVG объекты (стрелки, текст) временно удалены -->

        <!-- Линия для рисования стены (превью) -->
        <v-line
          v-if="isDrawingWall && wallPreview.length > 0"
          :config="{
            points: wallPreview,
            stroke: '#000000',
            strokeWidth: 2,
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
import { getIconUrl } from '@/components/accets/index.js'

// Кэшированные изображения для иконок
const iconImages = {}

const getIconImage = (iconName) => {
  const url = getIconUrl(iconName)
  if (!url) return null
  
  if (!iconImages[iconName]) {
    const img = new Image()
    img.src = url
    iconImages[iconName] = img
  }
  return iconImages[iconName]
}

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
  },
  fieldWidth: {
    type: Number,
    default: 200
  },
  fieldHeight: {
    type: Number,
    default: 100
  }
})

const emit = defineEmits([
  'select-object',
  'update-object',
  'delete-object',
  'add-object',
  'set-offset',
  'set-zoom',
  'select-tool',
  // События для Konva v-group
  'click',
  'tap',
  'dragstart',
  'dragend'
])

const canvasContainer = ref(null)
const stage = ref(null)
const isPanning = ref(false)
const isDrawingWall = ref(false)
const wallPreview = ref([])
const canvasCursor = ref('default')

const stageWidth = computed(() => canvasContainer.value?.clientWidth || 800)
const stageHeight = computed(() => canvasContainer.value?.clientHeight || 600)

// Размеры поля в пикселях
const fieldWidthPx = computed(() => props.fieldWidth * props.gridSize)
const fieldHeightPx = computed(() => props.fieldHeight * props.gridSize)

const selectedObjectId = computed(() => {
  const selected = props.objects.find(obj => obj.selected)
  return selected?.id || null
})

// Фильтрация объектов по типам
const walls = computed(() => props.objects.filter(obj => obj.object_type === 'wall'))
const doors = computed(() => props.objects.filter(obj => obj.object_type === 'door'))
const windows = computed(() => props.objects.filter(obj => obj.object_type === 'window'))
const workspaces = computed(() => props.objects.filter(obj => obj.object_type === 'workspace'))
const printers = computed(() => props.objects.filter(obj => obj.object_type === 'printer'))
const meetingRooms = computed(() => props.objects.filter(obj => obj.object_type === 'meeting_room'))
const kitchens = computed(() => props.objects.filter(obj => obj.object_type === 'kitchen'))
const staircases = computed(() => props.objects.filter(obj => obj.object_type === 'staircase'))
const restrooms = computed(() => props.objects.filter(obj => obj.object_type === 'restroom'))
const toiletsFemale = computed(() => props.objects.filter(obj => obj.object_type === 'toilet_female'))
const toiletsMale = computed(() => props.objects.filter(obj => obj.object_type === 'toilet_male'))
const otherObjects = computed(() => props.objects.filter(obj =>
  !['wall', 'door', 'window', 'workspace', 'printer', 'meeting_room', 'kitchen', 'staircase', 'restroom', 'toilet_female', 'toilet_male'].includes(obj.object_type)
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
    meeting_room: 'Переговорная',
    staircase: 'Лестница',
    restroom: 'Зона отдыха',
    arrow: '',
    text: ''
  }
  return names[type] || type
}

// === Выравнивание по сетке ===

// Шаг привязки к сетке (половина клетки = 10px)
const snapStep = props.gridSize / 2

const snapToGrid = (value) => {
  return Math.round(value / snapStep) * snapStep
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
  // === ОТЛАДКА ===
  // console.log('handleStageMouseDown:', {
  //   button: e.evt.button,
  //   target: e.target,
  //   targetType: e.target.getClassName(),
  //   currentTool: props.currentTool,
  //   isSelect: props.currentTool === 'select'
  // })

  // Левая кнопка мыши
  if (e.evt.button === 0) {
    // Проверяем, что клик был по фону (Rect) или по stage
    const isBackground = e.target.getClassName() === 'Rect' || e.target === e.target.getStage()
    
    if (isBackground) {
      emit('select-object', null)

      // Если активен инструмент добавления (не select)
      if (props.currentTool !== 'select') {
        // Получаем координаты с учетом масштаба и смещения
        const pos = e.target.getStage().getPointerPosition()
        // console.log('Pointer position:', pos)
        
        const x = (pos.x - props.offset.x) / props.zoom
        const y = (pos.y - props.offset.y) / props.zoom
        // console.log('Calculated position:', { x, y })

        // Скругляем до сетки
        const snappedX = snapToGrid(x)
        const snappedY = snapToGrid(y)
        // console.log('Snapped position:', { snappedX, snappedY })

        // Проверяем, что координаты в пределах поля
        if (snappedX < 0 || snappedX > fieldWidthPx.value || snappedY < 0 || snappedY > fieldHeightPx.value) {
          console.warn('Объект вне поля:', { x: snappedX, y: snappedY })
          return
        }

        // Создаем новый объект с уникальным ID
        let newObject = {
          id: Date.now(), // Уникальный временный ID
          object_type: props.currentTool,
          x: snappedX,
          y: snappedY,
          rotation: 0,
          name: '',
          description: '',
          is_active: true
        }

        // Размеры по умолчанию для разных типов объектов
        if (props.currentTool === 'wall') {
          newObject.width = 200
          newObject.height = 10
        } else if (props.currentTool === 'door') {
          newObject.width = 80
          newObject.height = 10
        } else if (props.currentTool === 'window') {
          newObject.width = 200
          newObject.height = 10
        } else if (props.currentTool === 'arrow') {
          newObject.width = 20
          newObject.height = 5
        } else if (props.currentTool === 'text') {
          newObject.width = 100
          newObject.height = 30
          newObject.description = 'Текст'
        } else {
          newObject.width = 100
          newObject.height = 50
        }

        // console.log('Добавление объекта:', newObject)
        emit('add-object', newObject)
        
        // Переключаем инструмент на select после добавления
        emit('select-tool', 'select')
        
        // Принудительно перерисовываем все слои
        setTimeout(() => {
          const stageInstance = stage.value?.getNode()
          if (stageInstance) {
            stageInstance.batchDraw()
          }
        }, 10)
      } else {
        // console.log('Инструмент select, объект не создаем')
      }
    } else {
      // console.log('Клик по объекту:', e.target.getClassName())
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
  // === ОТЛАДКА ===
  // console.log('handleDragEnd:', { object, evt: !!evt, evtTarget: evt?.target })
  
  // Konva передает событие как объект с target
  const node = evt?.target || object
  
  // Если node это сам объект (не Konva Node), пропускаем
  if (!node || typeof node.x !== 'function') {
    console.warn('handleDragEnd: node не является Konva Node')
    return
  }
  
  const x = node.x()
  const y = node.y()

  // Скругляем до сетки (10px)
  const snappedX = snapToGrid(x)
  const snappedY = snapToGrid(y)

  // === ОТЛАДКА ===
  // console.log('Перемещение:', { oldX: x, oldY: y, newX: snappedX, newY: snappedY })

  // Обновляем позицию узла
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
  
  // Ограничиваем масштаб: от 0.2 до 3 (было 0.1 до 5)
  const clampedScale = Math.max(0.2, Math.min(3, newScale))

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

// Переменные для отслеживания перемещения
let panStartX = 0
let panStartY = 0
let panOffsetStartX = 0
let panOffsetStartY = 0
let animationFrameId = null

// Функция для плавного обновления позиции
const updatePosition = (newOffsetX, newOffsetY) => {
  const stageInstance = stage.value?.getNode()
  if (stageInstance) {
    // Отменяем предыдущий кадр, если он еще не выполнен
    if (animationFrameId !== null) {
      cancelAnimationFrame(animationFrameId)
    }

    // Используем requestAnimationFrame для плавности
    animationFrameId = requestAnimationFrame(() => {
      // Ограничиваем перемещение, чтобы поле было видно
      // Показываем поле с небольшим запасом (100px)
      const margin = 100
      
      // Максимальное смещение влево/вправо
      const maxOffsetX = Math.max(0, fieldWidthPx.value * props.zoom - stageWidth.value + margin)
      // Максимальное смещение вверх/вниз
      const maxOffsetY = Math.max(0, fieldHeightPx.value * props.zoom - stageHeight.value + margin)

      const clampedX = Math.max(-maxOffsetX, Math.min(margin, newOffsetX))
      const clampedY = Math.max(-maxOffsetY, Math.min(margin, newOffsetY))

      stageInstance.x(clampedX)
      stageInstance.y(clampedY)
      stageInstance.batchDraw()
      animationFrameId = null
    })
  }

  // Отправляем новое смещение в store
  emit('set-offset', { x: newOffsetX, y: newOffsetY })
}

// Добавляем глобальные обработчики при монтировании
const addGlobalListeners = () => {
  const container = canvasContainer.value
  if (!container) return
  
  container.addEventListener('mousedown', (evt) => {
    // Средняя кнопка мыши (button === 1)
    if (evt.button === 1) {
      evt.preventDefault()
      evt.stopPropagation()
      
      isPanning.value = true
      canvasCursor.value = 'grabbing'
      
      // Сохраняем начальную позицию мыши
      panStartX = evt.clientX
      panStartY = evt.clientY
      
      // Сохраняем текущее смещение холста
      const stageInstance = stage.value?.getNode()
      if (stageInstance) {
        panOffsetStartX = stageInstance.x()
        panOffsetStartY = stageInstance.y()
      }
    }
  })
  
  container.addEventListener('mouseup', (evt) => {
    if (evt.button === 1) {
      evt.preventDefault()
      isPanning.value = false
      canvasCursor.value = 'default'
      
      // Отменяем ожидающий кадр
      if (animationFrameId !== null) {
        cancelAnimationFrame(animationFrameId)
        animationFrameId = null
      }
    }
  })
  
  container.addEventListener('mousemove', (evt) => {
    if (isPanning.value) {
      evt.preventDefault()
      evt.stopPropagation()
      
      // Вычисляем смещение мыши
      const deltaX = evt.clientX - panStartX
      const deltaY = evt.clientY - panStartY
      
      // Обновляем позицию холста
      const newOffsetX = panOffsetStartX + deltaX
      const newOffsetY = panOffsetStartY + deltaY
      
      // Плавное обновление позиции
      updatePosition(newOffsetX, newOffsetY)
    }
  })
  
  // Блокируем контекстное меню при нажатии колесика
  container.addEventListener('contextmenu', (evt) => {
    evt.preventDefault()
    evt.stopPropagation()
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
