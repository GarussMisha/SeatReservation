/**
 * ObjectMover - утилита для перетаскивания объектов на холсте
 * Отвечает за логику перемещения объектов и точек стен
 */

/**
 * Начать перетаскивание объекта
 * @param {Object} object - перетаскиваемый объект
 * @param {Object} pos - позиция мыши
 * @returns {Object} данные для перетаскивания
 */
export const startDragging = (object, pos) => {
  if (!object) return null
  
  return {
    isDragging: true,
    dragStart: {
      x: pos.x - object.x,
      y: pos.y - object.y
    },
    draggedObject: object
  }
}

/**
 * Начать перетаскивание точки стены
 * @param {Object} wall - стена
 * @param {number} pointIndex - индекс точки
 * @returns {Object} данные для перетаскивания точки
 */
export const startDraggingWallPoint = (wall, pointIndex) => {
  if (!wall || !wall.points || pointIndex < 0 || pointIndex >= wall.points.length) {
    return null
  }
  
  return {
    isDraggingWallPoint: true,
    draggedPointIndex: pointIndex,
    draggedWall: wall
  }
}

/**
 * Обновить позицию перетаскиваемого объекта
 * @param {Object} pos - текущая позиция мыши
 * @param {Object} dragStart - начальная позиция перетаскивания
 * @param {Object} object - перетаскиваемый объект
 * @returns {Object} новые координаты
 */
export const updateDragPosition = (pos, dragStart, object) => {
  return {
    x: pos.x - dragStart.x,
    y: pos.y - dragStart.y
  }
}

/**
 * Обновить позицию точки стены
 * @param {Array} points - массив точек
 * @param {number} pointIndex - индекс точки
 * @param {Object} pos - новая позиция
 * @returns {Array} обновлённый массив точек
 */
export const updateWallPointPosition = (points, pointIndex, pos) => {
  if (!points || pointIndex < 0 || pointIndex >= points.length) {
    return points
  }
  
  const newPoints = [...points]
  newPoints[pointIndex] = { x: pos.x, y: pos.y }
  return newPoints
}

/**
 * Завершить перетаскивание
 * @returns {Object} сброшенное состояние
 */
export const stopDragging = () => {
  return {
    isDragging: false,
    dragStart: { x: 0, y: 0 },
    draggedObject: null
  }
}

/**
 * Завершить перетаскивание точки стены
 * @returns {Object} сброшенное состояние
 */
export const stopDraggingWallPoint = () => {
  return {
    isDraggingWallPoint: false,
    draggedPointIndex: -1,
    draggedWall: null
  }
}

/**
 * Найти объект в позиции мыши
 * @param {Object} pos - позиция мыши
 * @param {Array} objects - массив объектов
 * @param {Function} pointToLineDistance - функция расстояния от точки до линии
 * @returns {Object|null} найденный объект или null
 */
export const findObjectAtPosition = (pos, objects, pointToLineDistance) => {
  if (!objects || !pos) return null
  
  // Сначала ищем стены, перегородки и окна (по линиям)
  const allWalls = objects.filter(obj =>
    obj.object_type === 'wall' || obj.object_type === 'internal_wall' || obj.object_type === 'window'
  )

  for (let wall of allWalls) {
    if (!wall.points) continue

    for (let i = 0; i < wall.points.length - 1; i++) {
      const dist = pointToLineDistance(pos, wall.points[i], wall.points[i + 1])
      if (dist < 10) {
        return wall
      }
    }
  }

  // Если не нашли стены, ищем остальные объекты (по прямоугольнику)
  const otherObjects = objects.filter(obj =>
    !['wall', 'internal_wall', 'window'].includes(obj.object_type)
  )

  for (let obj of otherObjects) {
    const objWidth = obj.width || 100
    const objHeight = obj.height || 100
    
    const inX = pos.x >= obj.x - objWidth / 2 && pos.x <= obj.x + objWidth / 2
    const inY = pos.y >= obj.y - objHeight / 2 && pos.y <= obj.y + objHeight / 2
    
    if (inX && inY) {
      return obj
    }
  }

  return null
}

/**
 * Проверить, попадает ли клик в точку стены
 * @param {Object} pos - позиция мыши
 * @param {Object} wall - стена
 * @param {number} radius - радиус попадания
 * @returns {number|null} индекс точки или null
 */
export const findWallPointAtPosition = (pos, wall, radius = 10) => {
  if (!wall || !wall.points || !pos) return null
  
  for (let i = 0; i < wall.points.length; i++) {
    const point = wall.points[i]
    const dist = Math.sqrt((pos.x - point.x) ** 2 + (pos.y - point.y) ** 2)
    if (dist < radius) {
      return i
    }
  }
  
  return null
}

export default {
  startDragging,
  startDraggingWallPoint,
  updateDragPosition,
  updateWallPointPosition,
  stopDragging,
  stopDraggingWallPoint,
  findObjectAtPosition,
  findWallPointAtPosition
}
