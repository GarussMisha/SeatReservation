/**
 * RoomPlanCanvas - отображение плана помещения на Canvas 2D
 * Использует тот же подход что и WallDrawingCanvas в редакторе
 */
<template>
  <div class="room-plan-canvas-container" ref="container">
    <canvas
      ref="canvas"
      class="room-plan-canvas"
      :style="{
        cursor: isPanning ? 'grabbing' : 'default'
      }"
      @mousedown="handleMouseDown"
      @mousemove="handleMouseMove"
      @mouseup="handleMouseUp"
      @click="handleClick"
      @wheel="handleWheel"
    ></canvas>

    <!-- Элементы управления зумом -->
    <div class="zoom-controls">
      <button @click="zoomIn" class="zoom-btn" title="Приблизить">+</button>
      <span class="zoom-level">{{ Math.round(zoom * 100) }}%</span>
      <button @click="zoomOut" class="zoom-btn" title="Отдалить">−</button>
      <button @click="resetView" class="zoom-btn" title="Сбросить вид">⊡</button>
    </div>

    <!-- Легенда -->
    <div class="legend">
      <div class="legend-item">
        <span class="legend-color available"></span>
        <span class="legend-label">Свободно</span>
      </div>
      <div class="legend-item">
        <span class="legend-color booked"></span>
        <span class="legend-label">Занято</span>
      </div>
      <div class="legend-item">
        <span class="legend-color my-booking"></span>
        <span class="legend-label">Моё бронирование</span>
      </div>
      <div class="legend-item">
        <span class="legend-color inactive"></span>
        <span class="legend-label">Не активно</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { roomObjectsAPI } from '@/services/roomObjects'
import { useAuthStore } from '@/stores/auth'
import { icons } from '@/components/accets/index.js'

const props = defineProps({
  roomId: {
    type: Number,
    required: true
  },
  selectedDate: {
    type: String,
    default: null
  },
  fieldWidth: {
    type: Number,
    default: 50
  },
  fieldHeight: {
    type: Number,
    default: 50
  },
  disabled: {
    type: Boolean,
    default: false  // Если true - блокировка взаимодействия
  }
})

const emit = defineEmits(['workspace-click', 'workspace-hover', 'workspaces-loaded'])

const authStore = useAuthStore()
const container = ref(null)
const canvas = ref(null)
const ctx = ref(null)

// Состояние
const workspaces = ref([])
const walls = ref([])
const zoom = ref(1)
const offset = ref({ x: 50, y: 50 })
const isPanning = ref(false)
const lastPos = ref({ x: 0, y: 0 })
const hoveredWorkspace = ref(null)
const imageCache = ref({})
const selectedWorkspace = ref(null)

// Цвета
const wallColor = '#999'
const doorColor = '#8B4513'
const windowColor = '#87CEEB'

// Цвета рабочих мест (3 статуса: available, booked, inactive)
const workspaceColors = {
  available: '#22c55e',    // Зелёный - свободно
  booked: '#3b82f6',       // Синий - занято
  myBooking: '#8b5cf6',    // Фиолетовый - моё бронирование
  inactive: '#6b7280'      // Серый - не активно
}

// Загрузка SVG изображения
const loadSvgImage = (src) => {
  return new Promise((resolve) => {
    if (imageCache.value[src]) {
      resolve(imageCache.value[src])
      return
    }

    const img = new Image()
    img.src = src
    img.onload = () => {
      imageCache.value[src] = img
      resolve(img)
    }
    img.onerror = () => {
      resolve(null)
    }
  })
}

// Отрисовка
const draw = async () => {
  if (!ctx.value || !canvas.value) return

  const c = ctx.value
  const width = canvas.value.width
  const height = canvas.value.height

  c.clearRect(0, 0, width, height)

  // Белый фон
  c.fillStyle = '#ffffff'
  c.fillRect(0, 0, width, height)

  c.save()

  // Применяем трансформации
  c.translate(offset.value.x, offset.value.y)
  c.scale(zoom.value, zoom.value)

  // Рисуем сетку
  drawGrid(c)

  // Рисуем стены
  walls.value.forEach(wall => {
    if (wall.points && wall.points.length >= 4) {
      c.beginPath()
      c.moveTo(wall.points[0], wall.points[1])
      for (let i = 2; i < wall.points.length; i += 2) {
        c.lineTo(wall.points[i], wall.points[i + 1])
      }
      c.strokeStyle = wallColor
      c.lineWidth = wall.thickness || 10
      c.lineCap = 'round'
      c.lineJoin = 'round'
      c.stroke()
    }
  })

  // Рисуем рабочие места
  for (const workspace of workspaces.value) {
    await drawWorkspace(c, workspace)
  }

  c.restore()
}

const drawGrid = (c) => {
  const gridSize = 20
  const fieldW = props.fieldWidth * gridSize
  const fieldH = props.fieldHeight * gridSize

  c.strokeStyle = '#e0e0e0'
  c.lineWidth = 1 / zoom.value

  for (let x = 0; x <= fieldW; x += gridSize) {
    c.beginPath()
    c.moveTo(x, 0)
    c.lineTo(x, fieldH)
    c.stroke()
  }

  for (let y = 0; y <= fieldH; y += gridSize) {
    c.beginPath()
    c.moveTo(0, y)
    c.lineTo(fieldW, y)
    c.stroke()
  }
}

const drawWorkspace = async (c, workspace) => {
  // В редакторе obj.x, obj.y - это ЦЕНТР объекта, а не левый верхний угол
  const centerX = workspace.x || 0
  const centerY = workspace.y || 0
  const width = workspace.width || 100
  const height = workspace.height || 50
  const rotation = (workspace.rotation || 0) * Math.PI / 180

  c.save()
  // Используем x,y как центр (как в редакторе)
  c.translate(centerX, centerY)
  c.rotate(rotation)

  // Фон
  c.fillStyle = workspaceColors[workspace.status] || workspaceColors.inactive
  c.globalAlpha = workspace.status === 'booked' ? 0.5 : (workspace.status === 'inactive' ? 0.3 : 1)

  // Тень для доступных и своих мест
  if (workspace.status === 'available' || workspace.status === 'myBooking') {
    c.shadowColor = workspaceColors[workspace.status]
    c.shadowBlur = 10
    c.shadowOpacity = 0.3
  }

  // Прямоугольник со скруглением (рисуем от центра)
  const radius = 4
  c.beginPath()
  c.moveTo(-width / 2 + radius, -height / 2)
  c.lineTo(width / 2 - radius, -height / 2)
  c.quadraticCurveTo(width / 2, -height / 2, width / 2, -height / 2 + radius)
  c.lineTo(width / 2, height / 2 - radius)
  c.quadraticCurveTo(width / 2, height / 2, width / 2 - radius, height / 2)
  c.lineTo(-width / 2 + radius, height / 2)
  c.quadraticCurveTo(-width / 2, height / 2, -width / 2, height / 2 - radius)
  c.lineTo(-width / 2, -height / 2 + radius)
  c.quadraticCurveTo(-width / 2, -height / 2, -width / 2 + radius, -height / 2)
  c.closePath()
  c.fill()

  c.shadowBlur = 0
  c.globalAlpha = 1

  // SVG иконка или эмодзи
  const iconSrc = icons.desktop
  if (imageCache.value[iconSrc]) {
    const img = imageCache.value[iconSrc]
    const iconSize = Math.min(width, height) * 0.8
    c.drawImage(img, -iconSize / 2, -iconSize / 2, iconSize, iconSize)
  } else {
    // Запасной вариант - эмодзи
    c.font = `${Math.min(width, height) * 0.5}px Arial`
    c.textAlign = 'center'
    c.textBaseline = 'middle'
    c.fillStyle = '#000'
    c.fillText('🪑', 0, 0)
  }

  c.restore()
}

// Обработчики событий
const handleMouseDown = (e) => {
  // Только левая кнопка мыши для навигации
  if (e.button !== 0) return
  
  isPanning.value = true
  lastPos.value = { x: e.clientX, y: e.clientY }
}

const handleMouseMove = (e) => {
  if (!isPanning.value) return

  const dx = e.clientX - lastPos.value.x
  const dy = e.clientY - lastPos.value.y

  offset.value = {
    x: offset.value.x + dx,
    y: offset.value.y + dy
  }

  lastPos.value = { x: e.clientX, y: e.clientY }
  draw()
}

const handleMouseUp = (e) => {
  isPanning.value = false
}

const handleClick = (e) => {
  // Если компонент заблокирован - игнорируем клики
  if (props.disabled) {
    console.log('Помещение не активно, клики заблокированы')
    return
  }
  
  // Проверяем, был ли это клик (не перетаскивание)
  if (isPanning.value) return
  
  const rect = canvas.value.getBoundingClientRect()
  const mouseX = (e.clientX - rect.left - offset.value.x) / zoom.value
  const mouseY = (e.clientY - rect.top - offset.value.y) / zoom.value

  // Проверяем клик по рабочему месту
  for (const ws of workspaces.value) {
    const x = ws.x || 0
    const y = ws.y || 0
    const width = ws.width || 100
    const height = ws.height || 50
    
    // Проверяем попадание в прямоугольник
    if (mouseX >= x - width / 2 && mouseX <= x + width / 2 &&
        mouseY >= y - height / 2 && mouseY <= y + height / 2) {
      
      // Проверяем что место не заблокировано
      if (ws.status === 'inactive') {
        console.log(`Рабочее место "${ws.name}" не активно, клик заблокирован`)
        return
      }
      
      // Только свободные места или свои бронирования
      if (ws.status === 'available' || ws.status === 'myBooking') {
        selectedWorkspace.value = ws
        emit('workspace-click', ws)
      }
      return
    }
  }
}

const handleWheel = (e) => {
  e.preventDefault()

  const scaleBy = 1.1
  const rect = canvas.value.getBoundingClientRect()
  const mouseX = e.clientX - rect.left - offset.value.x
  const mouseY = e.clientY - rect.top - offset.value.y

  const direction = e.deltaY > 0 ? -1 : 1
  const newZoom = direction > 0
    ? Math.min(zoom.value * scaleBy, 5)
    : Math.max(zoom.value / scaleBy, 0.2)

  zoom.value = newZoom

  offset.value = {
    x: e.clientX - rect.left - mouseX * (newZoom / zoom.value),
    y: e.clientY - rect.top - mouseY * (newZoom / zoom.value)
  }

  draw()
}

const zoomIn = () => {
  zoom.value = Math.min(zoom.value * 1.2, 5)
  draw()
}

const zoomOut = () => {
  zoom.value = Math.max(zoom.value / 1.2, 0.2)
  draw()
}

const resetView = () => {
  zoom.value = 1
  offset.value = { x: 50, y: 50 }
  centerView()
  draw()
}

const centerView = () => {
  if (workspaces.value.length === 0 && walls.value.length === 0) return

  let minX = Infinity, maxX = -Infinity
  let minY = Infinity, maxY = -Infinity

  // Границы стен
  walls.value.forEach(wall => {
    if (wall.points && wall.points.length >= 4) {
      for (let i = 0; i < wall.points.length; i += 2) {
        minX = Math.min(minX, wall.points[i])
        maxX = Math.max(maxX, wall.points[i])
        minY = Math.min(minY, wall.points[i + 1])
        maxY = Math.max(maxY, wall.points[i + 1])
      }
    }
  })

  // Границы рабочих мест
  workspaces.value.forEach(ws => {
    const x = ws.x || 0
    const y = ws.y || 0
    const w = ws.width || 100
    const h = ws.height || 50
    minX = Math.min(minX, x)
    maxX = Math.max(maxX, x + w)
    minY = Math.min(minY, y)
    maxY = Math.max(maxY, y + h)
  })

  const padding = 100
  minX -= padding
  minY -= padding
  maxX += padding
  maxY += padding

  const contentWidth = maxX - minX
  const contentHeight = maxY - minY

  const canvasWidth = canvas.value?.width || 800
  const canvasHeight = canvas.value?.height || 600

  const scaleX = canvasWidth / contentWidth
  const scaleY = canvasHeight / contentHeight
  const newZoom = Math.min(scaleX, scaleY, 2) * 0.9

  zoom.value = newZoom
  offset.value = {
    x: (canvasWidth - (maxX + minX) * newZoom) / 2,
    y: (canvasHeight - (maxY + minY) * newZoom) / 2
  }
}

// Загрузка данных
const loadRoomPlan = async () => {
  if (!props.roomId) return

  try {
    // Загружаем план
    const plan = await roomObjectsAPI.getRoomPlan(props.roomId)
    const allObjects = plan.objects || []

    // Обрабатываем стены
    walls.value = allObjects
      .filter(obj => ['wall', 'internal_wall'].includes(obj.object_type))
      .map(obj => {
        if (obj.properties && obj.properties.points) {
          const rawPoints = obj.properties.points
          let flatPoints = []
          
          if (Array.isArray(rawPoints)) {
            if (rawPoints.length > 0 && typeof rawPoints[0] === 'object') {
              flatPoints = rawPoints.flatMap(p => [p.x || 0, p.y || 0])
            } else {
              flatPoints = rawPoints.map(p => typeof p === 'number' ? p : 0)
            }
          }
          
          return { ...obj, points: flatPoints }
        }
        return { ...obj, points: [obj.x || 0, obj.y || 0, (obj.x || 0) + (obj.width || 100), (obj.y || 0)] }
      })

    // Загружаем рабочие места
    const data = await roomObjectsAPI.getWorkspacesWithLocations(props.roomId, props.selectedDate)
    console.log('Загруженные рабочие места:', data)
    
    const userId = authStore.user?.id
    console.log('Текущий userId:', userId)

    workspaces.value = data.map(ws => {
      // Backend теперь сам определяет статус: available, booked, inactive
      // Нам нужно только определить "myBooking"
      const booking = ws.current_booking || ws.currentBooking
      
      // Проверяем это ли наше бронирование И оно активное (status_id=13 confirmed)
      const CONFIRMED_STATUS = 13
      const isMyBooking = booking && booking.account_id === userId && booking.status_id === CONFIRMED_STATUS
      
      console.log(`Workspace ${ws.name}:`)
      console.log(`  - backend_status: ${ws.status}`)
      console.log(`  - booking: ${booking ? `{id: ${booking.id}, account_id: ${booking.account_id}, status_id: ${booking.status_id}}` : 'null'}`)
      console.log(`  - isMyBooking: ${isMyBooking}`)
      console.log(`  - final_status: ${isMyBooking ? 'myBooking' : ws.status}`)
      
      return {
        ...ws,
        status: isMyBooking ? 'myBooking' : ws.status,
        currentBooking: booking,
        current_booking: booking
      }
    })

    console.log('Обработанные рабочие места:', workspaces.value)

    // Отправляем статистику
    emit('workspaces-loaded', workspaces.value)

    // Центрируем
    centerView()

    // Рисуем
    await draw()
  } catch (error) {
    console.error('Ошибка загрузки плана:', error)
  }
}

// Lifecycle
onMounted(() => {
  if (canvas.value) {
    ctx.value = canvas.value.getContext('2d')
    
    // Устанавливаем размеры
    const resize = () => {
      if (container.value && canvas.value) {
        canvas.value.width = container.value.clientWidth
        canvas.value.height = container.value.clientHeight
        draw()
      }
    }
    
    resize()
    window.addEventListener('resize', resize)
    
    // Предзагружаем иконку
    loadSvgImage(icons.desktop).then(() => {
      loadRoomPlan()
    })
    
    onUnmounted(() => {
      window.removeEventListener('resize', resize)
    })
  }
})

// Watchers
watch(() => props.selectedDate, loadRoomPlan)
watch(() => props.roomId, loadRoomPlan)

// Экспортируем методы
defineExpose({
  centerView,
  resetView,
  refreshPlan: loadRoomPlan  // Добавляем метод обновления
})
</script>

<style scoped>
.room-plan-canvas-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 500px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 249, 250, 0.98) 100%);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.15);
}

.room-plan-canvas {
  width: 100%;
  height: 100%;
  cursor: default;
}

.zoom-controls {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  background: white;
  padding: 0.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.zoom-btn {
  width: 36px;
  height: 36px;
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 6px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  cursor: pointer;
  font-size: 1.25rem;
  color: #667eea;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.zoom-btn:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
}

.zoom-level {
  text-align: center;
  font-size: 0.85rem;
  color: #666;
  padding: 0.25rem 0;
}

.legend {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: white;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.legend-color.available {
  background: #22c55e;
}

.legend-color.booked {
  background: #3b82f6;
}

.legend-color.my-booking {
  background: #8b5cf6;
}

.legend-color.inactive {
  background: #6b7280;
}

.legend-label {
  font-size: 0.85rem;
  color: #333;
}
</style>
