/**
 * InteractiveRoomPlan - интерактивный план помещения
 * Отрисовка плана с рабочими местами с использованием Konva.js
 */
<template>
  <div class="room-plan-container" ref="container">
    <div class="room-plan-wrapper">
      <Stage
        ref="stage"
        :width="stageWidth"
        :height="stageHeight"
        :scale="{ x: zoom, y: zoom }"
        :position="{ x: offset.x, y: offset.y }"
        @mousedown="handleStageMouseDown"
        @touchstart="handleStageMouseDown"
        @wheel="handleWheel"
      >
        <Layer ref="layer">
          <!-- Сетка -->
          <Group v-if="showGrid">
            <template v-for="i in gridLinesX" :key="'vx' + i">
              <Line
                :points="[i * gridSize, 0, i * gridSize, props.fieldHeight * gridSize]"
                stroke="#e0e0e0"
                :strokeWidth="1 / zoom"
              />
            </template>
            <template v-for="i in gridLinesY" :key="'vy' + i">
              <Line
                :points="[0, i * gridSize, props.fieldWidth * gridSize, i * gridSize]"
                stroke="#e0e0e0"
                :strokeWidth="1 / zoom"
              />
            </template>
          </Group>

          <!-- Стены -->
          <template v-for="wall in walls" :key="wall.id">
            <Line
              v-if="wall.points && wall.points.length >= 4"
              :points="wall.points"
              :stroke="wallColor"
              :strokeWidth="wall.width || wall.thickness || 10"
              lineCap="round"
              lineJoin="round"
            />
            <Line
              v-else
              :points="[0, 0, wall.width || 100, 0]"
              :stroke="wallColor"
              :strokeWidth="wall.height || wall.thickness || 10"
              :x="wall.x"
              :y="wall.y"
              :rotation="wall.rotation || 0"
              lineCap="round"
              lineJoin="round"
            />
          </template>

          <!-- Двери -->
          <template v-for="door in doors" :key="door.id">
            <Rect
              :x="door.x"
              :y="door.y"
              :width="door.width || 80"
              :height="door.height || 10"
              :fill="doorColor"
              :rotation="door.rotation || 0"
            />
          </template>

          <!-- Окна -->
          <template v-for="window in windows" :key="window.id">
            <Rect
              :x="window.x"
              :y="window.y"
              :width="window.width || 100"
              :height="window.height || 10"
              :fill="windowColor"
              :rotation="window.rotation || 0"
            />
          </template>

          <!-- Рабочие места -->
          <template v-for="workspace in workspaces" :key="workspace.id">
            <Group
              :x="(workspace.x || 0) + (workspace.width || 100) / 2"
              :y="(workspace.y || 0) + (workspace.height || 50) / 2"
              :rotation="workspace.rotation || 0"
              @mouseenter="handleWorkspaceMouseEnter(workspace)"
              @mouseleave="handleWorkspaceMouseLeave"
              @click="handleWorkspaceClick(workspace)"
            >
              <!-- Фон рабочего места (прямоугольник) -->
              <Rect
                :width="workspace.width || 100"
                :height="workspace.height || 50"
                :x="-(workspace.width || 100) / 2"
                :y="-(workspace.height || 50) / 2"
                :fill="getWorkspaceColor(workspace.status)"
                :opacity="getWorkspaceOpacity(workspace.status)"
                :cornerRadius="4"
                :shadowBlur="workspace.status === 'available' || workspace.status === 'myBooking' ? 10 : 0"
                :shadowColor="getWorkspaceColor(workspace.status)"
                :shadowOpacity="0.3"
              />

              <!-- SVG иконка рабочего места -->
 <template v-if="imageCache[icons.desktop]">
                <KonvaImage
                  :image="imageCache[icons.desktop]"
                  :width="(workspace.width || 100) * 0.8"
                  :height="(workspace.height || 50) * 0.8"
                  :x="-(workspace.width || 100) * 0.4"
                  :y="-(workspace.height || 50) * 0.4"
                />
              </template>
              <template v-else>
                <Circle
                  :radius="Math.min(workspace.width || 100, workspace.height || 50) * 0.25"
                  fill="#667eea"
                  x="0"
                  y="0"
                />
                <Rect
                  :width="workspace.width || 100"
                  :height="workspace.height || 50"
                />
              </template>

              <!-- Название (при наведении) -->
              <Text
                v-if="hoveredWorkspace?.id === workspace.id"
                :text="workspace.name"
                :fontSize="12"
                :y="-(workspace.height || 50) / 2 - 20"
                align="center"
                :width="workspace.width || 100"
                fill="#333"
                fontStyle="bold"
              />
            </Group>
          </template>

          <!-- Тултип при наведении -->
          <Group v-if="tooltip.visible" :x="tooltip.x" :y="tooltip.y">
            <Rect
              :width="tooltip.width"
              :height="tooltip.height"
              :x="-tooltip.width / 2"
              :y="-tooltip.height - 10"
              fill="white"
              stroke="#667eea"
              :strokeWidth="2"
              :cornerRadius="8"
              :shadowBlur="10"
              shadowColor="black"
              :shadowOpacity="0.2"
            />
            <Text
              :text="tooltip.text"
              :fontSize="14"
              :y="-tooltip.height - 5"
              align="center"
              :width="tooltip.width"
              fill="#333"
              fontStyle="bold"
            />
            <Text
              v-if="tooltip.subtext"
              :text="tooltip.subtext"
              :fontSize="12"
              :y="-tooltip.height + 15"
              align="center"
              :width="tooltip.width"
              fill="#666"
            />
          </Group>
        </Layer>
      </Stage>
    </div>

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
        <span class="legend-label">Неактивно</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { Stage, Layer, Rect, Text, Line, Group, Image as KonvaImage } from 'vue-konva'
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
  showGrid: {
    type: Boolean,
    default: true
  },
  gridSize: {
    type: Number,
    default: 20
  },
  fieldWidth: {
    type: Number,
    default: 50
  },
  fieldHeight: {
    type: Number,
    default: 50
  }
})

const emit = defineEmits(['workspace-click', 'workspace-hover', 'workspaces-loaded'])

const authStore = useAuthStore()
const container = ref(null)
const stage = ref(null)
const layer = ref(null)

// Состояние
const workspaces = ref([])
const walls = ref([])
const doors = ref([])
const windows = ref([])
const zoom = ref(1)
const offset = ref({ x: 50, y: 50 })
const hoveredWorkspace = ref(null)
const tooltip = ref({
  visible: false,
  x: 0,
  y: 0,
  text: '',
  subtext: '',
  width: 200,
  height: 60
})

// Кэш для SVG изображений
const imageCache = ref({})

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

// Вычисляемые размеры сцены
const stageWidth = computed(() => {
  return container.value?.clientWidth || 800
})

const stageHeight = computed(() => {
  return container.value?.clientHeight || 600
})

const gridLinesX = computed(() => props.fieldWidth)
const gridLinesY = computed(() => props.fieldHeight)

// Цвета
const wallColor = '#999'
const doorColor = '#8B4513' // Коричневый
const windowColor = '#87CEEB' // Голубой

const workspaceColors = {
  available: '#22c55e',
  booked: '#3b82f6',
  myBooking: '#8b5cf6',
  inactive: '#6b7280'
}

const workspaceOpacities = {
  available: 1,
  booked: 0.5,
  myBooking: 1,
  inactive: 0.3
}

// Методы
const getWorkspaceColor = (status) => {
  return workspaceColors[status] || workspaceColors.inactive
}

const getWorkspaceOpacity = (status) => {
  return workspaceOpacities[status] || workspaceOpacities.inactive
}

const loadRoomPlan = async () => {
  if (!props.roomId) return

  try {
    // Загружаем ВЕСЬ план помещения (как в RoomEditor)
    const plan = await roomObjectsAPI.getRoomPlan(props.roomId)
    const allObjects = plan.objects || []
    
    console.log('Загруженный план помещения:', plan)
    console.log('Всего объектов:', allObjects.length)

    // Обрабатываем стены с восстановлением points
    walls.value = allObjects
      .filter(obj => ['wall', 'internal_wall'].includes(obj.object_type))
      .map(obj => {
        // Восстанавливаем points из properties
        if (obj.properties && obj.properties.points) {
          console.log('Стена с points:', obj.object_type, obj.properties.points)
          // Преобразуем массив объектов [{x, y}, ...] в плоский массив [x1, y1, x2, y2, ...]
          const rawPoints = obj.properties.points
          let flatPoints = []
          
          if (Array.isArray(rawPoints)) {
            if (rawPoints.length > 0 && typeof rawPoints[0] === 'object') {
              // Массив объектов [{x, y}, {x, y}, ...]
              flatPoints = rawPoints.flatMap(p => [p.x || 0, p.y || 0])
            } else {
              // Уже плоский массив [x1, y1, x2, y2, ...]
              flatPoints = rawPoints.map(p => typeof p === 'number' ? p : 0)
            }
          }
          
          console.log('Преобразованные points:', flatPoints)
          
          return {
            ...obj,
            points: flatPoints
          }
        }
        // Если points нет, используем координаты
        return {
          ...obj,
          points: [obj.x || 0, obj.y || 0, (obj.x || 0) + (obj.width || 100), (obj.y || 0)]
        }
      })
    
    console.log('Обработанные стены:', walls.value)
    
    // Обрабатываем двери
    doors.value = allObjects
      .filter(obj => obj.object_type === 'door')
      .map(obj => ({
        ...obj,
        width: obj.width || 80,
        height: obj.height || 10
      }))
    
    // Обрабатываем окна
    windows.value = allObjects
      .filter(obj => obj.object_type === 'window')
      .map(obj => ({
        ...obj,
        width: obj.width || 100,
        height: obj.height || 10
      }))
    
    // Загружаем рабочие места с координатами и статусами на выбранную дату
    const data = await roomObjectsAPI.getWorkspacesWithLocations(
      props.roomId,
      props.selectedDate
    )

    // Устанавливаем свои бронирования
    const userId = authStore.user?.id
    workspaces.value = data.map(ws => ({
      ...ws,
      status: ws.currentBooking?.account_id === userId ? 'myBooking' : ws.status,
      currentBooking: ws.currentBooking
    }))

    // Отправляем статистику родителю
    emit('workspaces-loaded', workspaces.value)

    // Центрируем вид по ВСЕМ объектам (стены + рабочие места)
    centerViewByAllObjects(allObjects)
  } catch (error) {
    console.error('Ошибка загрузки плана:', error)
  }
}

const centerViewByAllObjects = (allObjects) => {
  if (allObjects.length === 0) return

  // Находим границы всех объектов (стены, двери, окна, рабочие места)
  let minX = Infinity, maxX = -Infinity
  let minY = Infinity, maxY = -Infinity

  allObjects.forEach(obj => {
    // Для стен с points используем их
    if (obj.object_type === 'wall' || obj.object_type === 'internal_wall') {
      const rawPoints = obj.properties?.points
      let points = []
      
      if (rawPoints && Array.isArray(rawPoints)) {
        // Преобразуем [{x, y}, ...] в [x1, y1, ...]
        if (rawPoints.length > 0 && typeof rawPoints[0] === 'object') {
          points = rawPoints.flatMap(p => [p.x || 0, p.y || 0])
        } else {
          points = rawPoints
        }
      } else {
        points = [obj.x || 0, obj.y || 0, (obj.x || 0) + (obj.width || 100), (obj.y || 0)]
      }
      
      for (let i = 0; i < points.length; i += 2) {
        const x = points[i] || 0
        const y = points[i + 1] || 0
        minX = Math.min(minX, x)
        maxX = Math.max(maxX, x)
        minY = Math.min(minY, y)
        maxY = Math.max(maxY, y)
      }
    } else {
      // Для остальных объектов используем x, y, width, height
      const x = obj.x || 0
      const y = obj.y || 0
      const width = obj.width || 100
      const height = obj.height || 50
      
      minX = Math.min(minX, x)
      maxX = Math.max(maxX, x + width)
      minY = Math.min(minY, y)
      maxY = Math.max(maxY, y + height)
    }
  })

  console.log('Границы объектов:', { minX, maxX, minY, maxY })

  // Добавляем отступы
  const padding = 100
  minX -= padding
  minY -= padding
  maxX += padding
  maxY += padding

  const contentWidth = maxX - minX
  const contentHeight = maxY - minY

  console.log('Размеры контента:', contentWidth, contentHeight)

  // Вычисляем масштаб для отображения всего контента
  const scaleX = stageWidth.value / contentWidth
  const scaleY = stageHeight.value / contentHeight
  const newZoom = Math.min(scaleX, scaleY, 2) // Максимум 2x

  console.log('Масштаб:', newZoom, 'stageWidth:', stageWidth.value, 'stageHeight:', stageHeight.value)

  zoom.value = newZoom * 0.9 // Небольшой запас

  // Центрируем
  offset.value = {
    x: (stageWidth.value - (maxX + minX) * zoom.value) / 2,
    y: (stageHeight.value - (maxY + minY) * zoom.value) / 2
  }
  
  console.log('Offset:', offset.value)
}

const centerView = () => {
  if (workspaces.value.length === 0) return

  // Находим границы всех рабочих мест
  const minX = Math.min(...workspaces.value.map(ws => ws.x))
  const maxX = Math.max(...workspaces.value.map(ws => ws.x + ws.width))
  const minY = Math.min(...workspaces.value.map(ws => ws.y))
  const maxY = Math.max(...workspaces.value.map(ws => ws.y + ws.height))

  const contentWidth = maxX - minX + 200
  const contentHeight = maxY - minY + 200

  // Вычисляем масштаб для отображения всего контента
  const scaleX = stageWidth.value / contentWidth
  const scaleY = stageHeight.value / contentHeight
  const newZoom = Math.min(scaleX, scaleY, 2) // Максимум 2x

  zoom.value = newZoom * 0.9 // Небольшой запас

  // Центрируем
  offset.value = {
    x: (stageWidth.value - (maxX + minX) * zoom.value) / 2,
    y: (stageHeight.value - (maxY + minY) * zoom.value) / 2
  }
}

const zoomIn = () => {
  zoom.value = Math.min(zoom.value * 1.2, 5)
}

const zoomOut = () => {
  zoom.value = Math.max(zoom.value / 1.2, 0.2)
}

const resetView = () => {
  zoom.value = 1
  offset.value = { x: 50, y: 50 }
  centerView()
}

const handleWheel = (e) => {
  e.evt.preventDefault()

  const scaleBy = 1.1
  const stageRef = stage.value.getNode()
  const oldScale = zoom.value
  const pointer = stageRef.getPointerPosition()

  const mousePointTo = {
    x: (pointer.x - offset.value.x) / oldScale,
    y: (pointer.y - offset.value.y) / oldScale
  }

  const direction = e.evt.deltaY > 0 ? -1 : 1

  const newScale = direction > 0
    ? Math.min(oldScale * scaleBy, 5)
    : Math.max(oldScale / scaleBy, 0.2)

  zoom.value = newScale

  offset.value = {
    x: pointer.x - mousePointTo.x * newScale,
    y: pointer.y - mousePointTo.y * newScale
  }
}

const handleStageMouseDown = (e) => {
  // Если кликнули по пустому месту - снимаем выделение
  if (e.target === e.target.getStage()) {
    hoveredWorkspace.value = null
    tooltip.value.visible = false
  }
}

const handleWorkspaceMouseEnter = (workspace) => {
  hoveredWorkspace.value = workspace

  let text = workspace.name
  let subtext = ''

  if (workspace.status === 'available') {
    text = `${workspace.name} — свободно`
    subtext = 'Нажмите для бронирования'
  } else if (workspace.status === 'myBooking') {
    text = `${workspace.name} — ваше бронирование`
    subtext = 'Нажмите для отмены'
  } else if (workspace.status === 'booked') {
    text = `${workspace.name} — занято`
    subtext = `Забронировано: ${workspace.currentBooking?.account_first_name || 'Пользователь'}`
  } else {
    text = `${workspace.name} — недоступно`
    subtext = ''
  }

  tooltip.value = {
    ...tooltip.value,
    visible: true,
    x: workspace.x + workspace.width / 2,
    y: workspace.y,
    text,
    subtext
  }

  emit('workspace-hover', workspace)
}

const handleWorkspaceMouseLeave = () => {
  hoveredWorkspace.value = null
  tooltip.value.visible = false
  emit('workspace-hover', null)
}

const handleWorkspaceClick = (workspace) => {
  emit('workspace-click', workspace)
}

// Watchers
watch(() => props.roomId, loadRoomPlan, { immediate: true })
watch(() => props.selectedDate, loadRoomPlan)

onMounted(() => {
  nextTick(() => {
    // Предзагружаем иконку рабочего места
    loadSvgImage(icons.desktop)
    loadRoomPlan()
  })
})

// Экспортируем методы для внешнего использования
defineExpose({
  centerView,
  resetView
})
</script>

<style scoped>
.room-plan-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 500px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 249, 250, 0.98) 100%);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.15);
}

.room-plan-wrapper {
  width: 100%;
  height: 100%;
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
