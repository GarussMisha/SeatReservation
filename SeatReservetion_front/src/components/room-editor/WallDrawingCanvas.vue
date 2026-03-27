/**
 * WallDrawingCanvas - холст для рисования стен
 * Использует Canvas API для производительной отрисовки
 * С привязкой к сетке и предпросмотром
 */
<template>
  <div class="wall-canvas-container">
    <canvas
      ref="canvas"
      class="wall-canvas"
      @mousedown="handleMouseDown"
      @mousemove="handleMouseMove"
      @mouseup="handleMouseUp"
      @dblclick="handleDoubleClick"
      @contextmenu.prevent
    ></canvas>
    
    <!-- Подсказка -->
    <div v-if="!isDrawing && currentTool === 'wall'" class="canvas-hint">
      <span class="hint-icon">🎯</span>
      <span class="hint-text">Кликните для начала рисования стены</span>
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
  }
})

const emit = defineEmits(['wall-completed'])

const canvas = ref(null)
const ctx = ref(null)
const store = useRoomEditorStore()

// Состояние рисования
const isDrawing = ref(false)
const currentLine = ref([])
const mousePos = ref({ x: 0, y: 0 })
const selectedWall = ref(null)

// Размеры холста
const canvasWidth = 2000
const canvasHeight = 1500

// Типы стен
const wallTypes = {
  wall: { color: '#1e293b', width: 8, name: 'Стена' },
  internal_wall: { color: '#94a3b8', width: 3, name: 'Перегородка' }
}

onMounted(() => {
  const c = canvas.value
  c.width = canvasWidth
  c.height = canvasHeight
  ctx.value = c.getContext('2d')
  
  draw()
  
  document.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown)
})

// === Функции отрисовки ===

const snapToGrid = (value) => {
  return Math.round(value / props.gridSize) * props.gridSize
}

const getMousePos = (e) => {
  const rect = canvas.value.getBoundingClientRect()
  const scaleX = canvasWidth / rect.width
  const scaleY = canvasHeight / rect.height
  return {
    x: snapToGrid((e.clientX - rect.left) * scaleX),
    y: snapToGrid((e.clientY - rect.top) * scaleY)
  }
}

const draw = () => {
  const c = ctx.value
  c.clearRect(0, 0, canvasWidth, canvasHeight)
  
  // Рисуем сетку
  drawGrid()
  
  // Рисуем готовые стены из store
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
}

const drawGrid = () => {
  const c = ctx.value
  c.strokeStyle = '#e2e8f0'
  c.lineWidth = 1
  
  for (let x = 0; x <= canvasWidth; x += props.gridSize) {
    c.beginPath()
    c.moveTo(x, 0)
    c.lineTo(x, canvasHeight)
    c.stroke()
  }
  
  for (let y = 0; y <= canvasHeight; y += props.gridSize) {
    c.beginPath()
    c.moveTo(0, y)
    c.lineTo(canvasWidth, y)
    c.stroke()
  }
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
  
  wall.points.forEach(point => {
    c.beginPath()
    c.arc(point.x, point.y, 8, 0, Math.PI * 2)
    c.stroke()
  })
  
  c.setLineDash([])
}

// === Обработчики событий ===

const handleMouseDown = (e) => {
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
  mousePos.value = getMousePos(e)
  if (isDrawing.value) {
    draw()
  }
}

const handleMouseUp = () => {
  // Продолжаем рисовать
}

const handleDoubleClick = () => {
  if (isDrawing.value && currentLine.value.length >= 2) {
    finishDrawing()
  }
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
  cursor: crosshair;
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
</style>
