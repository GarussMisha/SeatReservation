/**
 * WallDrawingCanvas - холст для рисования стен
 * Использует Canvas API для производительной отрисовки
 * С привязкой к сетке и предпросмотром
 */
<template>
  <div class="wall-canvas-container" ref="container">
    <canvas
      ref="canvas"
      class="wall-canvas"
      :style="{
        cursor: isPanning ? 'grabbing' : currentTool === 'wall' || currentTool === 'internal_wall' ? 'crosshair' : 'default'
      }"
      @mousedown="handleMouseDown"
      @mousemove="handleMouseMove"
      @mouseup="handleMouseUp"
      @dblclick="handleDoubleClick"
      @contextmenu.prevent="handleContextMenu"
    ></canvas>
    
    <!-- Координаты мыши (для отладки) -->
    <div class="mouse-coords">
      <span class="coord-label">X: </span>
      <span class="coord-value">{{ mouseCoords.x }}</span>
      <span class="coord-sep"> | </span>
      <span class="coord-label">Y: </span>
      <span class="coord-value">{{ mouseCoords.y }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoomEditorStore } from '@/stores/roomEditor'
import { icons } from '@/components/accets/index.js'

const props = defineProps({
  currentTool: {
    type: String,
    default: 'select'
  },
  gridSize: {
    type: Number,
    default: 20
  },
  zoom: {
    type: Number,
    default: 1
  },
  offset: {
    type: Object,
    default: () => ({ x: 0, y: 0 })
  },
  fieldWidth: {
    type: Number,
    default: 200
  },
  fieldHeight: {
    type: Number,
    default: 100
  },
  snapToGrid: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update-zoom', 'update-offset', 'drawing-state'])

const canvas = ref(null)
const ctx = ref(null)
const container = ref(null)
const store = useRoomEditorStore()

// Кэш для SVG изображений
const imageCache = {}

// Загрузка SVG изображений
const loadSvgImage = (src) => {
  return new Promise((resolve) => {
    if (imageCache[src]) {
      resolve(imageCache[src])
      return
    }
    
    const img = new Image()
    img.src = src
    img.onload = () => {
      imageCache[src] = img
      resolve(img)
    }
    img.onerror = () => {
      resolve(null)
    }
  })
}

// Состояние рисования
const isDrawing = ref(false)
const currentLine = ref([])
const mousePos = ref({ x: 0, y: 0 })
const selectedWall = ref(null)
const isDrawingCanvas = ref(false) // Флаг для предотвращения двойной отрисовки
const isDragging = ref(false) // Флаг перетаскивания объекта
const dragStart = ref({ x: 0, y: 0 }) // Начальная позиция перетаскивания
const isDraggingWallPoint = ref(false) // Флаг перетаскивания точки стены
const draggedPointIndex = ref(-1) // Индекс перетаскиваемой точки стены

// Координаты мыши для отображения (для отладки)
const mouseCoords = ref({ x: 0, y: 0 })

// Состояние перемещения
const isPanning = ref(false)
const panStart = ref({ x: 0, y: 0 })

// Размеры холста
const canvasWidth = ref(2000)
const canvasHeight = ref(1500)

// Типы стен
const wallTypes = {
  wall: { color: '#1e293b', width: 8, name: 'Стена' },
  internal_wall: { color: '#94a3b8', width: 3, name: 'Перегородка' },
  window: { color: '#0ea5e9', width: 6, name: 'Окно' }
}

// === Вычисляемые свойства ===

// Расчет длины завершенной части текущей линии в метрах (1 клетка = 0.5м)
const currentLineLength = computed(() => {
  if (currentLine.value.length < 2) return 0

  let totalLengthPx = 0
  for (let i = 0; i < currentLine.value.length - 1; i++) {
    const dx = currentLine.value[i + 1].x - currentLine.value[i].x
    const dy = currentLine.value[i + 1].y - currentLine.value[i].y
    totalLengthPx += Math.sqrt(dx * dx + dy * dy)
  }

  // Переводим пиксели в клетки (gridSize = 20px), затем в метры (1 клетка = 0.5м)
  const cells = totalLengthPx / props.gridSize
  return (cells * 0.5).toFixed(2)
})

// Расчет длины текущего сегмента до курсора мыши в метрах
const previewSegmentLength = computed(() => {
  if (!isDrawing.value || currentLine.value.length < 1) return 0

  const lastPoint = currentLine.value[currentLine.value.length - 1]
  const dx = mousePos.value.x - lastPoint.x
  const dy = mousePos.value.y - lastPoint.y
  const segmentLengthPx = Math.sqrt(dx * dx + dy * dy)
  
  // Переводим пиксели в клетки (gridSize = 20px), затем в метры (1 клетка = 0.5м)
  const cells = segmentLengthPx / props.gridSize
  return (cells * 0.5).toFixed(2)
})

// Общая длина строящейся стены (завершенная часть + сегмент до курсора)
const totalBuildingLength = computed(() => {
  if (!isDrawing.value) return '0'
  
  const completed = parseFloat(currentLineLength.value) || 0
  const preview = parseFloat(previewSegmentLength.value) || 0
  
  return (completed + preview).toFixed(2)
})

onMounted(async () => {
  updateCanvasSize()

  // Ждем пока canvas инициализируется
  await new Promise(resolve => setTimeout(resolve, 0))

  const c = canvas.value
  if (!c) return

  ctx.value = c.getContext('2d')

  // Инициализируем начальное смещение для центрирования поля
  if (!props.offset || (props.offset.x === 0 && props.offset.y === 0)) {
    const fieldWidthPx = props.fieldWidth * props.gridSize
    const fieldHeightPx = props.fieldHeight * props.gridSize
    emit('update-offset', {
      x: (canvasWidth.value - fieldWidthPx) / 2,
      y: (canvasHeight.value - fieldHeightPx) / 2
    })
  } else {
    // Если offset уже установлен, рисуем поле
    await draw()
  }

  document.addEventListener('keydown', handleKeyDown)
  window.addEventListener('resize', updateCanvasSize)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown)
  window.removeEventListener('resize', updateCanvasSize)
})

// === Обновление размеров ===

const updateCanvasSize = async () => {
  if (!canvas.value) return

  const container = canvas.value.parentElement
  canvasWidth.value = container.clientWidth
  canvasHeight.value = container.clientHeight

  canvas.value.width = canvasWidth.value
  canvas.value.height = canvasHeight.value

  await draw()
}

// === Функции отрисовки ===

const snapToGrid = (value) => {
  // Если привязка отключена, возвращаем значение как есть
  if (!props.snapToGrid) {
    return value
  }
  return Math.round(value / props.gridSize) * props.gridSize
}

// Получение точных координат мыши в пространстве поля (без привязки к сетке)
const getFieldMousePos = (e) => {
  if (!canvas.value) {
    return { x: 0, y: 0 }
  }
  
  const rect = canvas.value.getBoundingClientRect()
  const scaleX = canvasWidth.value / rect.width
  const scaleY = canvasHeight.value / rect.height

  // Получаем координаты мыши в пикселях canvas
  const x = (e.clientX - rect.left) * scaleX
  const y = (e.clientY - rect.top) * scaleY

  // Если offset ещё не установлен, возвращаем координаты без смещения
  if (!props.offset) {
    return {
      x: x,
      y: y
    }
  }

  // Учитываем смещение для получения координат в пространстве поля
  return {
    x: (x - props.offset.x),
    y: (y - props.offset.y)
  }
}

const getMousePos = (e) => {
  if (!canvas.value) {
    return { x: 0, y: 0 }
  }
  
  const rect = canvas.value.getBoundingClientRect()
  const scaleX = canvasWidth.value / rect.width
  const scaleY = canvasHeight.value / rect.height

  // Получаем координаты мыши в пикселях canvas
  const x = (e.clientX - rect.left) * scaleX
  const y = (e.clientY - rect.top) * scaleY

  // Учитываем смещение для получения координат в пространстве поля
  const fieldX = x - props.offset.x
  const fieldY = y - props.offset.y

  // Привязываем к сетке
  return {
    x: snapToGrid(fieldX),
    y: snapToGrid(fieldY)
  }
}

const draw = async () => {
  // Предотвращаем двойную отрисовку
  if (isDrawingCanvas.value) return
  if (!ctx.value) return

  isDrawingCanvas.value = true

  try {
    const c = ctx.value
    c.clearRect(0, 0, canvasWidth.value, canvasHeight.value)

    // Рисуем белый фон
    c.fillStyle = '#ffffff'
    c.fillRect(0, 0, canvasWidth.value, canvasHeight.value)

    // Если offset ещё не установлен, не рисуем поле
    if (!props.offset) {
      isDrawingCanvas.value = false
      return
    }

    // Сохраняем контекст для трансформаций
    c.save()

    // Применяем смещение (без масштабирования)
    c.translate(props.offset.x, props.offset.y)

    // Рисуем сетку
    drawGrid()

    // Рисуем границы поля
    drawFieldBounds()

    // 1. Сначала рисуем все остальные объекты (мебель, оборудование и т.д.) - снизу
    const otherObjects = store.objects.filter(obj =>
      !['wall', 'internal_wall', 'window'].includes(obj.object_type)
    )
    for (const obj of otherObjects) {
      await drawObject(obj)
    }

    // 2. Окна (снизу)
    const windows = store.objects.filter(obj => obj.object_type === 'window')
    windows.forEach(win => {
      drawWall(win, '#0ea5e9', 6)
    })

    // 3. Перегородки
    const partitions = store.objects.filter(obj => obj.object_type === 'internal_wall')
    partitions.forEach(part => {
      drawWall(part, '#94a3b8', 3)
    })

    // 4. Стены (сверху всех)
    const walls = store.objects.filter(obj => obj.object_type === 'wall')
    walls.forEach(wall => {
      drawWall(wall, '#1e293b', 8)
    })

    // 2.5. Рисуем текущую линию
    if (currentLine.value.length > 0 && isDrawing.value) {
      const wallType = wallTypes[props.currentTool] || wallTypes.wall
      const color = wallType.color
      const width = wallType.width

      // Рисуем завершенные сегменты
      for (let i = 0; i < currentLine.value.length - 1; i++) {
        drawLineSegment(
          currentLine.value[i],
          currentLine.value[i + 1],
          color,
          width
        )
      }

      // Рисуем предпросмотр до мыши
      drawLineSegment(
        currentLine.value[currentLine.value.length - 1],
        mousePos.value,
        color,
        width,
        true
      )
    }

    // Рисуем выделение
    if (selectedWall.value) {
      // Если это стена, перегородка или окно - рисуем выделение по точкам
      if (['wall', 'internal_wall', 'window'].includes(selectedWall.value.object_type)) {
        drawSelection(selectedWall.value)
      } else {
        // Для остальных объектов рисуем прямоугольник выделения
        drawObjectSelection(selectedWall.value)
      }
    }

    // Восстанавливаем контекст
    c.restore()
  } finally {
    isDrawingCanvas.value = false
  }
}

const drawGrid = () => {
  const c = ctx.value
  c.strokeStyle = '#e2e8f0'
  c.lineWidth = 1

  const fieldWidthPx = props.fieldWidth * props.gridSize
  const fieldHeightPx = props.fieldHeight * props.gridSize

  // Рисуем сетку
  c.beginPath()

  for (let x = 0; x <= fieldWidthPx; x += props.gridSize) {
    c.moveTo(x, 0)
    c.lineTo(x, fieldHeightPx)
  }

  for (let y = 0; y <= fieldHeightPx; y += props.gridSize) {
    c.moveTo(0, y)
    c.lineTo(fieldWidthPx, y)
  }

  c.stroke()
}

const drawSvgObjects = () => {
  // Здесь можно рисовать SVG иконки через ctx.drawImage()
  // Для простоты пока рисуем только стены
}

const drawFieldBounds = () => {
  const c = ctx.value
  const fieldWidthPx = props.fieldWidth * props.gridSize
  const fieldHeightPx = props.fieldHeight * props.gridSize

  c.strokeStyle = '#4CAF50'
  c.lineWidth = 3
  c.setLineDash([10, 5])
  c.strokeRect(0, 0, fieldWidthPx, fieldHeightPx)
  c.setLineDash([])

  // Подписи размеров
  c.fillStyle = '#4CAF50'
  c.font = '14px Arial'
  c.textAlign = 'center'
  c.fillText(`${props.fieldWidth} кл. (${props.fieldWidth * 0.5}м)`, fieldWidthPx / 2, 30)

  c.save()
  c.translate(30, fieldHeightPx / 2)
  c.rotate(-Math.PI / 2)
  c.fillText(`${props.fieldHeight} кл. (${props.fieldHeight * 0.5}м)`, 0, 0)
  c.restore()
}

// Отрисовка остальных объектов (мебель, оборудование)
const drawObject = async (obj) => {
  // Окна, стены и перегородки рисуются отдельно через drawWall
  const objectType = obj.object_type;
  if (objectType === 'wall' || objectType === 'internal_wall' || objectType === 'window') {
    return
  }

  if (!ctx.value) return
  const c = ctx.value

  // Маппинг типов объектов к иконкам
  const iconMap = {
    'workspace': icons.desktop,
    'printer': icons.printer,
    'kitchen': icons.kitchen,
    'meeting_room': icons.conferenceRoom,
    'staircase': icons.ladder,
    'restroom': icons.hanger,
    'toilet_female': icons.toiletWoman,
    'toilet_male': icons.toiletMan
  }

  const iconSrc = iconMap[obj.object_type]

  c.save()
  c.translate(obj.x, obj.y)
  c.rotate((obj.rotation || 0) * Math.PI / 180)

  // Используем размеры из объекта (width/height)
  const objWidth = obj.width || 100
  const objHeight = obj.height || 100

  if (iconSrc) {
    // Загружаем и рисуем SVG иконку
    const img = await loadSvgImage(iconSrc)
    if (img) {
      // Рисуем иконку центрированной с масштабированием
      c.drawImage(img, -objWidth / 2, -objHeight / 2, objWidth, objHeight)
    } else {
      // Если иконка не загрузилась, рисуем прямоугольник
      c.fillStyle = 'rgba(102, 126, 234, 0.2)'
      c.strokeStyle = '#667eea'
      c.lineWidth = 2
      c.fillRect(-objWidth / 2, -objHeight / 2, objWidth, objHeight)
      c.strokeRect(-objWidth / 2, -objHeight / 2, objWidth, objHeight)
    }
  } else {
    // Если иконки нет, рисуем прямоугольник
    c.fillStyle = 'rgba(102, 126, 234, 0.2)'
    c.strokeStyle = '#667eea'
    c.lineWidth = 2
    c.fillRect(-objWidth / 2, -objHeight / 2, objWidth, objHeight)
    c.strokeRect(-objWidth / 2, -objHeight / 2, objWidth, objHeight)
  }

  c.restore()
}

const drawWall = (wall, color, width) => {
  if (!wall.points || wall.points.length < 2) return
  
  for (let i = 0; i < wall.points.length - 1; i++) {
    drawLineSegment(wall.points[i], wall.points[i + 1], color, width)
  }
}

const drawLineSegment = (start, end, color, width, isPreview = false) => {
  const c = ctx.value
  c.beginPath()
  c.moveTo(start.x, start.y)
  c.lineTo(end.x, end.y)
  c.strokeStyle = color
  c.lineWidth = width
  c.lineCap = 'round'
  c.lineJoin = 'round'

  if (isPreview) {
    c.setLineDash([5, 5])
    c.globalAlpha = 0.6
  }

  c.stroke()
  c.setLineDash([])
  c.globalAlpha = 1
}

const drawSelection = (wall) => {
  const c = ctx.value
  c.strokeStyle = '#667eea'
  c.lineWidth = 2
  c.setLineDash([5, 5])

  wall.points.forEach((point, idx) => {
    c.beginPath()
    c.arc(point.x, point.y, 8, 0, Math.PI * 2)
    c.stroke()
    
    // Закрашиваем точки для лучшей видимости
    c.fillStyle = '#667eea'
    c.fill()
  })

  c.setLineDash([])
}

// Выделение для объектов (рабочие места, принтеры и т.д.)
const drawObjectSelection = (obj) => {
  const c = ctx.value
  const objWidth = obj.width || 100
  const objHeight = obj.height || 100
  
  c.strokeStyle = '#667eea'
  c.lineWidth = 2
  c.setLineDash([5, 5])
  c.strokeRect(obj.x - objWidth / 2, obj.y - objHeight / 2, objWidth, objHeight)
  c.setLineDash([])
  
  // Рисуем маркеры по углам
  c.fillStyle = '#667eea'
  const markerSize = 6
  c.fillRect(obj.x - objWidth / 2 - markerSize / 2, obj.y - objHeight / 2 - markerSize / 2, markerSize, markerSize)
  c.fillRect(obj.x + objWidth / 2 - markerSize / 2, obj.y - objHeight / 2 - markerSize / 2, markerSize, markerSize)
  c.fillRect(obj.x - objWidth / 2 - markerSize / 2, obj.y + objHeight / 2 - markerSize / 2, markerSize, markerSize)
  c.fillRect(obj.x + objWidth / 2 - markerSize / 2, obj.y + objHeight / 2 - markerSize / 2, markerSize, markerSize)
}

// === Обработчики событий ===

const handleMouseDown = async (e) => {
  // Правая кнопка мыши - завершить рисование
  if (e.button === 2) {
    if (isDrawing.value && currentLine.value.length >= 2) {
      finishDrawing()
    }
    return
  }

  // Средняя кнопка мыши - перемещение поля
  if (e.button === 1) {
    e.preventDefault()

    // Проверяем, что поле больше canvas (иначе перемещать не нужно)
    const fieldWidthPx = props.fieldWidth * props.gridSize
    const fieldHeightPx = props.fieldHeight * props.gridSize

    if (fieldWidthPx > canvasWidth.value || fieldHeightPx > canvasHeight.value) {
      isPanning.value = true
      panStart.value = { x: e.clientX - props.offset.x, y: e.clientY - props.offset.y }
    }
    return
  }

  // Левая кнопка мыши
  if (e.button === 0) {
    // Если инструмент "Выбор" - проверяем, попали ли в объект
    if (props.currentTool === 'select') {
      const pos = getMousePos(e)
      
      // Сначала проверяем, не кликнули ли на точку стены (для перетаскивания)
      if (selectedWall.value && selectedWall.value.points) {
        for (let i = 0; i < selectedWall.value.points.length; i++) {
          const point = selectedWall.value.points[i]
          const dist = Math.sqrt((pos.x - point.x) ** 2 + (pos.y - point.y) ** 2)
          if (dist < 10) {
            // Кликнули на точку стены - начинаем перетаскивание точки
            isDraggingWallPoint.value = true
            draggedPointIndex.value = i
            await draw()
            return
          }
        }
      }
      
      // Сначала ищем стены, перегородки и окна (по линиям)
      const allWalls = store.objects.filter(obj =>
        obj.object_type === 'wall' || obj.object_type === 'internal_wall' || obj.object_type === 'window'
      )

      let foundObject = null

      // Ищем стены
      for (let wall of allWalls) {
        if (!wall.points) continue

        for (let i = 0; i < wall.points.length - 1; i++) {
          const dist = pointToLineDistance(
            pos,
            wall.points[i],
            wall.points[i + 1]
          )
          if (dist < 10) {
            foundObject = wall
            break
          }
        }
        if (foundObject) break
      }

      // Если не нашли стены, ищем остальные объекты (по прямоугольнику)
      if (!foundObject) {
        const otherObjects = store.objects.filter(obj =>
          !['wall', 'internal_wall', 'window'].includes(obj.object_type)
        )

        for (let obj of otherObjects) {
          const objWidth = obj.width || 100
          const objHeight = obj.height || 100
          
          // Проверяем, попал ли клик в прямоугольник объекта
          const inX = pos.x >= obj.x - objWidth / 2 && pos.x <= obj.x + objWidth / 2
          const inY = pos.y >= obj.y - objHeight / 2 && pos.y <= obj.y + objHeight / 2
          
          if (inX && inY) {
            foundObject = obj
            break
          }
        }
      }

      // Если нашли объект - начинаем перетаскивание
      if (foundObject) {
        selectedWall.value = foundObject
        store.selectObject(foundObject)
        
        // Если это не стена, начинаем перетаскивание
        if (!['wall', 'internal_wall', 'window'].includes(foundObject.object_type)) {
          isDragging.value = true
          dragStart.value = {
            x: pos.x - foundObject.x,
            y: pos.y - foundObject.y
          }
        }
        await draw()
        return
      }
      
      // Если ничего не нашли, снимаем выделение
      selectedWall.value = null
      store.selectObject(null)
      await draw()
      return
    }
  }

  // Обработка инструментов для рисования линий (стены, перегородки, окна)
  if (['wall', 'internal_wall', 'window'].includes(props.currentTool)) {
    const pos = getMousePos(e)

    if (!isDrawing.value) {
      isDrawing.value = true
      currentLine.value = [pos]
    } else {
      currentLine.value.push(pos)
    }

    await draw()
    return
  }

  // Обработка инструментов для установки объектов (рабочие места, принтеры и т.д.)
  const objectTypes = ['workspace', 'printer', 'kitchen', 'meeting_room', 'staircase', 'restroom', 'toilet_female', 'toilet_male']
  if (objectTypes.includes(props.currentTool)) {
    const pos = getMousePos(e)
    
    // Определяем название и размеры объекта (базовый размер 100px = 100%)
    let objectName, defaultSize
    switch (props.currentTool) {
      case 'workspace':
        objectName = 'Рабочее место'
        defaultSize = 100
        break
      case 'printer':
        objectName = 'Принтер'
        defaultSize = 100
        break
      case 'kitchen':
        objectName = 'Кухня'
        defaultSize = 100
        break
      case 'meeting_room':
        objectName = 'Переговорная'
        defaultSize = 100
        break
      case 'staircase':
        objectName = 'Лестница'
        defaultSize = 100
        break
      case 'restroom':
        objectName = 'Раздевалка'
        defaultSize = 100
        break
      case 'toilet_female':
        objectName = 'Женский туалет'
        defaultSize = 100
        break
      case 'toilet_male':
        objectName = 'Мужской туалет'
        defaultSize = 100
        break
      default:
        objectName = 'Объект'
        defaultSize = 100
    }

    const newObject = {
      id: Date.now(),
      object_type: props.currentTool,
      x: pos.x,
      y: pos.y,
      width: defaultSize,
      height: defaultSize,
      rotation: props.currentTool === 'workspace' ? 0 : 0,
      name: objectName,
      is_active: true
    }

    store.addObject(newObject)
    await draw()
    return
  }
}

const handleMouseMove = async (e) => {
  // Если canvas не существует, выходим
  if (!canvas.value) return
  
  if (isPanning.value) {
    const newOffset = {
      x: e.clientX - panStart.value.x,
      y: e.clientY - panStart.value.y
    }

    emit('update-offset', newOffset)
    return
  }

  // Обработка перетаскивания точки стены
  if (isDraggingWallPoint.value && selectedWall.value && selectedWall.value.points) {
    const pos = getMousePos(e)
    // Обновляем координаты точки
    selectedWall.value.points[draggedPointIndex.value] = { x: pos.x, y: pos.y }
    // Обновляем объект в store
    store.updateObject(selectedWall.value.id, { points: [...selectedWall.value.points] })
    await draw()
    return
  }

  // Обработка перетаскивания объекта
  if (isDragging.value && selectedWall.value) {
    const pos = getMousePos(e)
    const newX = pos.x - dragStart.value.x
    const newY = pos.y - dragStart.value.y
    
    // Обновляем координаты объекта
    store.updateObject(selectedWall.value.id, { x: newX, y: newY })
    await draw()
    return
  }

  // Обновляем координаты мыши для отображения
  const fieldPos = getFieldMousePos(e)
  mouseCoords.value = {
    x: Math.round(fieldPos.x),
    y: Math.round(fieldPos.y)
  }

  mousePos.value = getMousePos(e)
  if (isDrawing.value) {
    await draw()
  }
}

const handleMouseUp = async (e) => {
  if (e.button === 1) {
    isPanning.value = false
  }
  if (e.button === 0) {
    // Если завершили перетаскивание точки стены
    if (isDraggingWallPoint.value) {
      isDraggingWallPoint.value = false
      draggedPointIndex.value = -1
    }
    // Если завершили перетаскивание объекта - просто снимаем флаг перетаскивания
    // Выделение остаётся, чтобы можно было открыть настройки
    if (isDragging.value) {
      isDragging.value = false
    }
  }
}

const handleContextMenu = async (e) => {
  e.preventDefault()
  if (isDrawing.value && currentLine.value.length >= 2) {
    await finishDrawing()
  }
}

const handleDoubleClick = async () => {
  if (isDrawing.value && currentLine.value.length >= 2) {
    await finishDrawing()
  }
}

const handleKeyDown = async (e) => {
  if (e.key === 'Escape') {
    currentLine.value = []
    isDrawing.value = false
    await draw()
  }
  if (e.key === 'Delete' && selectedWall.value) {
    await deleteSelected()
  }
  if (e.key === 'z' && (e.ctrlKey || e.metaKey)) {
    await undoLastPoint()
  }
}

// === Функции рисования ===

const finishDrawing = async () => {
  if (currentLine.value.length >= 2) {
    // Определяем тип объекта
    let objectType, objectName;
    if (props.currentTool === 'internal_wall') {
      objectType = 'internal_wall';
      objectName = 'Перегородка';
    } else if (props.currentTool === 'window') {
      objectType = 'window';
      objectName = 'Окно';
    } else {
      objectType = 'wall';
      objectName = 'Стена';
    }

    // Создаем объект стены/окна
    const wall = {
      id: Date.now(),
      object_type: objectType,
      points: [...currentLine.value],
      x: currentLine.value[0].x,
      y: currentLine.value[0].y,
      width: 10,
      height: 10,
      rotation: 0,
      name: objectName,
      is_active: true
    }

    store.addObject(wall)

    currentLine.value = []
    isDrawing.value = false
    await draw()
  }
}

const undoLastPoint = async () => {
  if (currentLine.value.length > 0) {
    currentLine.value.pop()
    if (currentLine.value.length === 0) {
      isDrawing.value = false
    }
    await draw()
  }
}

const pointToLineDistance = (point, lineStart, lineEnd) => {
  const A = point.x - lineStart.x
  const B = point.y - lineStart.y
  const C = lineEnd.x - lineStart.x
  const D = lineEnd.y - lineStart.y
  
  const dot = A * C + B * D
  const lenSq = C * C + D * D
  let param = -1
  
  if (lenSq !== 0) param = dot / lenSq
  
  let xx, yy
  
  if (param < 0) {
    xx = lineStart.x
    yy = lineStart.y
  } else if (param > 1) {
    xx = lineEnd.x
    yy = lineEnd.y
  } else {
    xx = lineStart.x + param * C
    yy = lineStart.y + param * D
  }
  
  const dx = point.x - xx
  const dy = point.y - yy
  return Math.sqrt(dx * dx + dy * dy)
}

const deleteSelected = async () => {
  if (!selectedWall.value) return

  store.deleteObject(selectedWall.value.id)
  selectedWall.value = null
  await draw()
}

// === Экспорт ===

const exportToImage = () => {
  return canvas.value.toDataURL('image/png')
}

defineExpose({
  exportToImage
})

// === Watchers ===

watch(() => [props.offset, props.fieldWidth, props.fieldHeight], async () => {
  await draw()
}, { deep: true })

// Перерисовка при изменении объектов в store
watch(() => store.objects, async () => {
  await draw()
}, { deep: true })

// При включении привязки к сетке - округляем позиции всех объектов
watch(() => props.snapToGrid, async (newValue) => {
  if (newValue) {
    // Округляем позиции всех объектов по сетке
    store.objects.forEach(obj => {
      const newX = snapToGrid(obj.x)
      const newY = snapToGrid(obj.y)
      
      // Если позиция изменилась, обновляем объект
      if (newX !== obj.x || newY !== obj.y) {
        store.updateObject(obj.id, { x: newX, y: newY })
      }
      
      // Для стен также округляем точки
      if (obj.points && Array.isArray(obj.points)) {
        const newPoints = obj.points.map(point => ({
          x: snapToGrid(point.x),
          y: snapToGrid(point.y)
        }))
        store.updateObject(obj.id, { points: newPoints })
      }
    })
    await draw()
  }
}, { deep: true })

// Отправка состояния рисования
watch([isDrawing, currentLine, previewSegmentLength, () => props.currentTool], () => {
  emit('drawing-state', {
    isDrawing: isDrawing.value,
    currentLine: currentLine.value,
    currentLineLength: previewSegmentLength.value,
    currentTool: props.currentTool
  })
}, { deep: true })
</script>

<style scoped>
.wall-canvas-container {
  position: relative;
  width: 100%;
  height: 100%;
  background: #ffffff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.wall-canvas {
  width: 100%;
  height: 100%;
  display: block;
}

.canvas-hint {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(255, 255, 255, 0.95);
  padding: 24px 32px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  pointer-events: none;
  z-index: 10;
}

.canvas-hint.drawing {
  background: rgba(255, 243, 199, 0.95);
  border: 2px solid #f59e0b;
}

.hint-content {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.hint-icon {
  font-size: 2.5rem;
  flex-shrink: 0;
}

.hint-text {
  text-align: left;
}

.hint-text p {
  font-size: 0.95rem;
  color: #475569;
  margin: 6px 0;
  line-height: 1.4;
}

.hint-text strong {
  color: #667eea;
  font-weight: 600;
}

.canvas-hint.drawing .hint-text strong {
  color: #f59e0b;
}

/* Координаты мыши */
.mouse-coords {
  position: absolute;
  bottom: 20px;
  left: 20px;
  background: rgba(255, 255, 255, 0.95);
  padding: 8px 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 10;
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
}

.coord-label {
  color: #64748b;
  font-weight: 500;
}

.coord-value {
  color: #1e293b;
  font-weight: 600;
}

.coord-sep {
  color: #cbd5e1;
  margin: 0 4px;
}
</style>
