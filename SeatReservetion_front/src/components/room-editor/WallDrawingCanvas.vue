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
      @contextmenu.prevent
    ></canvas>
    
    <!-- Подсказка -->
    <div v-if="!isDrawing && (currentTool === 'wall' || currentTool === 'internal_wall')" class="canvas-hint">
      <span class="hint-icon">🎯</span>
      <span class="hint-text">Кликните для начала рисования стены</span>
    </div>
    
    <!-- Информация о масштабе -->
    <div class="zoom-info">
      <span class="zoom-value">{{ Math.round(zoom * 100) }}%</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoomEditorStore } from '@/stores/roomEditor'

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
  }
})

const emit = defineEmits(['wall-completed', 'update-zoom', 'update-offset'])

const canvas = ref(null)
const ctx = ref(null)
const container = ref(null)
const store = useRoomEditorStore()

// Состояние рисования
const isDrawing = ref(false)
const currentLine = ref([])
const mousePos = ref({ x: 0, y: 0 })
const selectedWall = ref(null)

// Состояние перемещения
const isPanning = ref(false)
const panStart = ref({ x: 0, y: 0 })

// Размеры холста
const canvasWidth = ref(2000)
const canvasHeight = ref(1500)

// Ограничения масштаба
const MIN_ZOOM = 0.1
const MAX_ZOOM = 5

// Типы стен
const wallTypes = {
  wall: { color: '#1e293b', width: 8, name: 'Стена' },
  internal_wall: { color: '#94a3b8', width: 3, name: 'Перегородка' }
}

onMounted(async () => {
  updateCanvasSize()
  
  // Ждем пока canvas инициализируется
  await new Promise(resolve => setTimeout(resolve, 0))
  
  const c = canvas.value
  if (!c) return
  
  ctx.value = c.getContext('2d')
  
  // Инициализируем начальное смещение для центрирования поля
  if (props.offset.x === 0 && props.offset.y === 0) {
    const fieldWidthPx = props.fieldWidth * props.gridSize
    const fieldHeightPx = props.fieldHeight * props.gridSize
    emit('update-offset', {
      x: (canvasWidth.value - fieldWidthPx * props.zoom) / 2,
      y: (canvasHeight.value - fieldHeightPx * props.zoom) / 2
    })
  }
  
  draw()
  
  document.addEventListener('keydown', handleKeyDown)
  window.addEventListener('resize', updateCanvasSize)
  
  // Добавляем не-пассивный обработчик для wheel
  if (container.value) {
    container.value.addEventListener('wheel', handleWheel, { passive: false })
  }
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown)
  window.removeEventListener('resize', updateCanvasSize)
  
  // Удаляем обработчик wheel
  if (container.value) {
    container.value.removeEventListener('wheel', handleWheel)
  }
})

// === Обновление размеров ===

const updateCanvasSize = () => {
  if (!canvas.value) return
  
  const container = canvas.value.parentElement
  canvasWidth.value = container.clientWidth
  canvasHeight.value = container.clientHeight
  
  canvas.value.width = canvasWidth.value
  canvas.value.height = canvasHeight.value
  
  draw()
}

// === Функции отрисовки ===

const snapToGrid = (value) => {
  return Math.round(value / props.gridSize) * props.gridSize
}

const getMousePos = (e) => {
  const rect = canvas.value.getBoundingClientRect()
  const scaleX = canvasWidth.value / rect.width
  const scaleY = canvasHeight.value / rect.height
  
  // Учитываем масштаб и смещение
  const x = (e.clientX - rect.left) * scaleX
  const y = (e.clientY - rect.top) * scaleY
  
  return {
    x: snapToGrid((x - props.offset.x) / props.zoom),
    y: snapToGrid((y - props.offset.y) / props.zoom)
  }
}

const draw = () => {
  if (!ctx.value) return
  
  const c = ctx.value
  c.clearRect(0, 0, canvasWidth.value, canvasHeight.value)
  
  // Рисуем белый фон
  c.fillStyle = '#ffffff'
  c.fillRect(0, 0, canvasWidth.value, canvasHeight.value)
  
  // Сохраняем контекст для трансформаций
  c.save()
  
  // Применяем масштаб и смещение
  c.translate(props.offset.x, props.offset.y)
  c.scale(props.zoom, props.zoom)
  
  // Рисуем сетку
  drawGrid()
  
  // Рисуем границы поля
  drawFieldBounds()
  
  // Восстанавливаем контекст перед рисованием объектов
  c.restore()
  
  // Рисуем готовые стены из store (уже с трансформациями)
  c.save()
  c.translate(props.offset.x, props.offset.y)
  c.scale(props.zoom, props.zoom)
  
  const walls = store.objects.filter(obj => obj.object_type === 'wall')
  walls.forEach(wall => {
    drawWall(wall, '#1e293b', 8)
  })
  
  // Рисуем перегородки
  const partitions = store.objects.filter(obj => obj.object_type === 'internal_wall')
  partitions.forEach(part => {
    drawWall(part, '#94a3b8', 3)
  })
  
  // Рисуем текущую линию
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
    drawSelection(selectedWall.value)
  }
  
  // Восстанавливаем контекст
  c.restore()
}

const drawGrid = () => {
  const c = ctx.value
  c.strokeStyle = '#e2e8f0'
  c.lineWidth = 1 / props.zoom
  
  const fieldWidthPx = props.fieldWidth * props.gridSize
  const fieldHeightPx = props.fieldHeight * props.gridSize
  
  // Рисуем только видимую часть сетки для производительности
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

const drawFieldBounds = () => {
  const c = ctx.value
  const fieldWidthPx = props.fieldWidth * props.gridSize
  const fieldHeightPx = props.fieldHeight * props.gridSize

  c.strokeStyle = '#4CAF50'
  c.lineWidth = 3 / props.zoom
  c.setLineDash([10, 5])
  c.strokeRect(0, 0, fieldWidthPx, fieldHeightPx)
  c.setLineDash([])

  // Подписи размеров (рисуем внутри поля чтобы не обрезалось)
  c.fillStyle = '#4CAF50'
  c.font = `${14 / props.zoom}px Arial`
  c.textAlign = 'center'
  c.fillText(`${props.fieldWidth} кл. (${props.fieldWidth * 0.5}м)`, fieldWidthPx / 2, 30 / props.zoom)

  c.save()
  c.translate(30 / props.zoom, fieldHeightPx / 2)
  c.rotate(-Math.PI / 2)
  c.fillText(`${props.fieldHeight} кл. (${props.fieldHeight * 0.5}м)`, 0, 0)
  c.restore()
}

const drawSvgObjects = () => {
  // Здесь можно рисовать SVG иконки через ctx.drawImage()
  // Для простоты пока рисуем только стены
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
  c.lineWidth = width / props.zoom
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
  c.lineWidth = 2 / props.zoom
  c.setLineDash([5, 5])
  
  wall.points.forEach(point => {
    c.beginPath()
    c.arc(point.x, point.y, 8 / props.zoom, 0, Math.PI * 2)
    c.stroke()
  })
  
  c.setLineDash([])
}

// === Обработчики событий ===

const handleMouseDown = (e) => {
  // Средняя кнопка мыши - перемещение
  if (e.button === 1) {
    e.preventDefault()
    isPanning.value = true
    panStart.value = { x: e.clientX - props.offset.x, y: e.clientY - props.offset.y }
    return
  }
  
  if (props.currentTool === 'select') {
    selectWall(e)
    return
  }
  
  if (!['wall', 'internal_wall'].includes(props.currentTool)) {
    return
  }
  
  const pos = getMousePos(e)
  
  if (!isDrawing.value) {
    isDrawing.value = true
    currentLine.value = [pos]
  } else {
    currentLine.value.push(pos)
  }
  
  draw()
}

const handleMouseMove = (e) => {
  if (isPanning.value) {
    const newOffset = {
      x: e.clientX - panStart.value.x,
      y: e.clientY - panStart.value.y
    }
    emit('update-offset', newOffset)
    return
  }
  
  mousePos.value = getMousePos(e)
  if (isDrawing.value) {
    draw()
  }
}

const handleMouseUp = (e) => {
  if (e.button === 1) {
    isPanning.value = false
  }
}

const handleDoubleClick = () => {
  if (isDrawing.value && currentLine.value.length >= 2) {
    finishDrawing()
  }
}

const handleWheel = (e) => {
  e.preventDefault()
  
  const scaleBy = 1.1
  const newZoom = e.deltaY < 0 ? props.zoom * scaleBy : props.zoom / scaleBy
  const clampedZoom = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, newZoom))
  
  emit('update-zoom', clampedZoom)
}

const handleKeyDown = (e) => {
  if (e.key === 'Escape') {
    currentLine.value = []
    isDrawing.value = false
    draw()
  }
  if (e.key === 'Delete' && selectedWall.value) {
    deleteSelected()
  }
  if (e.key === 'z' && (e.ctrlKey || e.metaKey)) {
    undoLastPoint()
  }
}

// === Функции рисования ===

const finishDrawing = () => {
  if (currentLine.value.length >= 2) {
    // Создаем объект стены
    const wall = {
      id: Date.now(),
      object_type: props.currentTool === 'internal_wall' ? 'internal_wall' : 'wall',
      points: [...currentLine.value],
      x: currentLine.value[0].x,
      y: currentLine.value[0].y,
      width: 10,
      height: 10,
      rotation: 0,
      name: props.currentTool === 'internal_wall' ? 'Перегородка' : 'Стена',
      is_active: true
    }
    
    store.addObject(wall)
    emit('wall-completed', wall)
    
    currentLine.value = []
    isDrawing.value = false
    draw()
  }
}

const undoLastPoint = () => {
  if (currentLine.value.length > 0) {
    currentLine.value.pop()
    if (currentLine.value.length === 0) {
      isDrawing.value = false
    }
    draw()
  }
}

const selectWall = (e) => {
  const pos = getMousePos(e)
  const allWalls = store.objects.filter(obj => 
    obj.object_type === 'wall' || obj.object_type === 'internal_wall'
  )
  
  selectedWall.value = null
  
  for (let wall of allWalls) {
    if (!wall.points) continue
    
    for (let i = 0; i < wall.points.length - 1; i++) {
      const dist = pointToLineDistance(
        pos,
        wall.points[i],
        wall.points[i + 1]
      )
      if (dist < 10) {
        selectedWall.value = wall
        store.selectObject(wall)
        break
      }
    }
    if (selectedWall.value) break
  }
  
  draw()
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

const deleteSelected = () => {
  if (!selectedWall.value) return
  
  store.deleteObject(selectedWall.value.id)
  selectedWall.value = null
  draw()
}

// === Экспорт ===

const exportToImage = () => {
  return canvas.value.toDataURL('image/png')
}

defineExpose({
  exportToImage
})

// === Watchers ===

watch(() => [props.zoom, props.offset, props.fieldWidth, props.fieldHeight], () => {
  draw()
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
  padding: 20px 30px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 12px;
  pointer-events: none;
  z-index: 10;
}

.hint-icon {
  font-size: 2rem;
}

.hint-text {
  font-size: 1rem;
  color: #475569;
  font-weight: 500;
}

.zoom-info {
  position: absolute;
  bottom: 20px;
  right: 20px;
  background: rgba(255, 255, 255, 0.95);
  padding: 8px 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.zoom-value {
  font-size: 0.9rem;
  font-weight: 600;
  color: #667eea;
}
</style>
