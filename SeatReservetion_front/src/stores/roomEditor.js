import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * Store для редактора помещений
 * Управляет состоянием визуального редактора плана помещения
 */
export const useRoomEditorStore = defineStore('roomEditor', () => {
  // === Состояние ===
  
  // Текущее помещение
  const currentRoom = ref(null)
  
  // Все объекты на плане
  const objects = ref([])
  
  // Выбранный объект
  const selectedObject = ref(null)
  
  // Активный инструмент
  const currentTool = ref('select') // select, wall, door, window, workspace, printer, kitchen, meeting_room
  
  // История изменений (для undo/redo)
  const history = ref([])
  const historyIndex = ref(-1)
  
  // Масштаб и позиционирование
  const zoom = ref(1)
  const offset = ref(null)

  // Размер сетки
  const gridSize = ref(20) // 1 клетка = 20px

  // Показывать сетку
  const showGrid = ref(true)

  // Размеры поля (в клетках сетки) - 50x50 квадратов
  const fieldWidth = ref(50) // 50 клеток = 25 метров (1 клетка = 0.5м)
  const fieldHeight = ref(50) // 50 клеток = 25 метров

  // Загрузка
  const isLoading = ref(false)
  const error = ref(null)
  
  // === Вычисляемые свойства ===
  
  const canUndo = computed(() => historyIndex.value > 0)
  const canRedo = computed(() => historyIndex.value < history.value.length - 1)
  
  const walls = computed(() => objects.value.filter(obj => obj.object_type === 'wall'))
  const doors = computed(() => objects.value.filter(obj => obj.object_type === 'door'))
  const windows = computed(() => objects.value.filter(obj => obj.object_type === 'window'))
  const workspaces = computed(() => objects.value.filter(obj => obj.object_type === 'workspace'))
  const otherObjects = computed(() => objects.value.filter(obj => 
    !['wall', 'door', 'window', 'workspace'].includes(obj.object_type)
  ))
  
  // === Методы ===
  
  /**
   * Установить текущее помещение
   */
  const setCurrentRoom = (room) => {
    currentRoom.value = room
  }
  
  /**
   * Загрузить объекты плана
   */
  const loadObjects = (loadedObjects) => {
    console.log('Загруженные объекты с сервера:', loadedObjects)
    
    // Восстанавливаем points из properties для стен, перегородок и окон
    const restoredObjects = (loadedObjects || []).map(obj => {
      if (obj.object_type && ['wall', 'internal_wall', 'window'].includes(obj.object_type)) {
        if (obj.properties && obj.properties.points) {
          console.log('Восстанавливаем points для объекта:', obj.object_type, obj.properties.points)
          return {
            ...obj,
            points: obj.properties.points
          }
        } else {
          console.log('Нет points для объекта:', obj.object_type, obj)
        }
      }
      return obj
    })
    
    console.log('Восстановленные объекты:', restoredObjects)
    objects.value = restoredObjects
    addToHistory()
  }
  
  /**
   * Добавить объект
   */
  const addObject = (object) => {
    const newObject = {
      id: object.id || Date.now(),
      room_id: object.room_id || currentRoom.value?.id,
      object_type: object.object_type,
      x: object.x || 0,
      y: object.y || 0,
      rotation: object.rotation || 0,
      width: object.width || 100,
      height: object.height || 50,
      name: object.name || '',
      description: object.description || '',
      is_active: object.is_active !== undefined ? object.is_active : true,
      properties: object.properties || {},
      ...object
    }

    console.log('Store: добавление объекта', newObject)
    objects.value.push(newObject)
    addToHistory()
    console.log('Store: всего объектов', objects.value.length)
    return newObject
  }
  
  /**
   * Обновить объект
   */
  const updateObject = (objectId, updates) => {
    const index = objects.value.findIndex(obj => obj.id === objectId)
    if (index !== -1) {
      objects.value[index] = { ...objects.value[index], ...updates }
      addToHistory()
    }
  }
  
  /**
   * Удалить объект
   */
  const deleteObject = (objectId) => {
    const index = objects.value.findIndex(obj => obj.id === objectId)
    if (index !== -1) {
      objects.value.splice(index, 1)
      if (selectedObject.value?.id === objectId) {
        selectedObject.value = null
      }
      addToHistory()
    }
  }
  
  /**
   * Выбрать объект
   */
  const selectObject = (object) => {
    selectedObject.value = object
  }
  
  /**
   * Установить инструмент
   */
  const setTool = (tool) => {
    currentTool.value = tool
    selectedObject.value = null
  }
  
  /**
   * Добавить в историю
   */
  const addToHistory = () => {
    // Удаляем все записи после текущей позиции (если были undo)
    if (historyIndex.value < history.value.length - 1) {
      history.value = history.value.slice(0, historyIndex.value + 1)
    }
    
    // Добавляем текущее состояние
    history.value.push(JSON.parse(JSON.stringify(objects.value)))
    historyIndex.value = history.value.length - 1
    
    // Ограничиваем размер истории
    if (history.value.length > 50) {
      history.value.shift()
      historyIndex.value--
    }
  }
  
  /**
   * Отменить действие (undo)
   */
  const undo = () => {
    if (canUndo.value) {
      historyIndex.value--
      objects.value = JSON.parse(JSON.stringify(history.value[historyIndex.value]))
    }
  }
  
  /**
   * Повторить действие (redo)
   */
  const redo = () => {
    if (canRedo.value) {
      historyIndex.value++
      objects.value = JSON.parse(JSON.stringify(history.value[historyIndex.value]))
    }
  }
  
  /**
   * Установить масштаб
   */
  const setZoom = (newZoom) => {
    // Ограничиваем масштаб от 0.2 до 3
    zoom.value = Math.max(0.2, Math.min(3, newZoom))
  }
  
  /**
   * Установить позицию
   */
  const setOffset = (newOffset) => {
    offset.value = newOffset
  }
  
  /**
   * Очистить редактор (удалить все объекты)
   */
  const clearEditor = () => {
    objects.value = []
    selectedObject.value = null
    currentTool.value = 'select'
    history.value = []
    historyIndex.value = -1
    zoom.value = 1
    // offset не сбрасываем, чтобы не было ошибок при отрисовке
    error.value = null
    // currentRoom сохраняем
  }
  
  /**
   * Экспорт объектов в JSON
   */
  const exportToJSON = () => {
    return JSON.stringify(objects.value, null, 2)
  }
  
  /**
   * Импорт объектов из JSON
   */
  const importFromJSON = (jsonString) => {
    try {
      const imported = JSON.parse(jsonString)
      objects.value = imported
      addToHistory()
      return true
    } catch (error) {
      console.error('Ошибка импорта JSON:', error)
      return false
    }
  }

  /**
   * Установить ширину поля
   */
  const setFieldWidth = (width) => {
    fieldWidth.value = Math.max(50, Math.min(500, width)) // от 50 до 500 клеток
  }

  /**
   * Установить высоту поля
   */
  const setFieldHeight = (height) => {
    fieldHeight.value = Math.max(50, Math.min(500, height)) // от 50 до 500 клеток
  }

  return {
    // Состояние
    currentRoom,
    objects,
    selectedObject,
    currentTool,
    history,
    historyIndex,
    zoom,
    offset,
    gridSize,
    showGrid,
    fieldWidth,
    fieldHeight,
    isLoading,
    error,

    // Вычисляемые свойства
    canUndo,
    canRedo,
    walls,
    doors,
    windows,
    workspaces,
    otherObjects,

    // Методы
    setCurrentRoom,
    loadObjects,
    addObject,
    updateObject,
    deleteObject,
    selectObject,
    setTool,
    addToHistory,
    undo,
    redo,
    setZoom,
    setOffset,
    clearEditor,
    exportToJSON,
    importFromJSON,
    setFieldWidth,
    setFieldHeight
  }
})
