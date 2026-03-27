/**
 * CanvasRenderer - утилита для отрисовки объектов на холсте
 * Отвечает за визуализацию стен, объектов и выделения
 */

/**
 * Отрисовать сетку
 * @param {CanvasRenderingContext2D} ctx - контекст canvas
 * @param {number} fieldWidth - ширина поля в клетках
 * @param {number} fieldHeight - высота поля в клетках
 * @param {number} gridSize - размер клетки в пикселях
 */
export const drawGrid = (ctx, fieldWidth, fieldHeight, gridSize) => {
  ctx.strokeStyle = '#e2e8f0'
  ctx.lineWidth = 1

  const fieldWidthPx = fieldWidth * gridSize
  const fieldHeightPx = fieldHeight * gridSize

  // Вертикальные линии
  for (let x = 0; x <= fieldWidthPx; x += gridSize) {
    ctx.beginPath()
    ctx.moveTo(x, 0)
    ctx.lineTo(x, fieldHeightPx)
    ctx.stroke()
  }

  // Горизонтальные линии
  for (let y = 0; y <= fieldHeightPx; y += gridSize) {
    ctx.beginPath()
    ctx.moveTo(0, y)
    ctx.lineTo(fieldWidthPx, y)
    ctx.stroke()
  }
}

/**
 * Отрисовать границы поля
 * @param {CanvasRenderingContext2D} ctx - контекст canvas
 * @param {number} fieldWidth - ширина поля в клетках
 * @param {number} fieldHeight - высота поля в клетках
 * @param {number} gridSize - размер клетки в пикселях
 */
export const drawFieldBounds = (ctx, fieldWidth, fieldHeight, gridSize) => {
  const fieldWidthPx = fieldWidth * gridSize
  const fieldHeightPx = fieldHeight * gridSize

  ctx.strokeStyle = '#94a3b8'
  ctx.lineWidth = 2
  ctx.strokeRect(0, 0, fieldWidthPx, fieldHeightPx)

  // Подписи размеров
  ctx.fillStyle = '#64748b'
  ctx.font = '12px Arial'
  ctx.fillText(`${fieldWidth} кл. (${fieldWidth * 0.5}м)`, 5, 15)
  ctx.fillText(`${fieldHeight} кл. (${fieldHeight * 0.5}м)`, 0, 30)
}

/**
 * Отрисовать стену по точкам
 * @param {CanvasRenderingContext2D} ctx - контекст canvas
 * @param {Object} wall - объект стены
 * @param {string} color - цвет линии
 * @param {number} width - толщина линии
 */
export const drawWall = (ctx, wall, color = '#1e293b', width = 8) => {
  if (!wall.points || wall.points.length < 2) return

  ctx.strokeStyle = color
  ctx.lineWidth = width
  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'

  ctx.beginPath()
  ctx.moveTo(wall.points[0].x, wall.points[0].y)

  for (let i = 1; i < wall.points.length; i++) {
    ctx.lineTo(wall.points[i].x, wall.points[i].y)
  }

  ctx.stroke()
}

/**
 * Отрисовать сегмент линии
 * @param {CanvasRenderingContext2D} ctx - контекст canvas
 * @param {Object} start - начальная точка
 * @param {Object} end - конечная точка
 * @param {string} color - цвет линии
 * @param {number} width - толщина линии
 * @param {boolean} isPreview - это предпросмотр (пунктир)
 */
export const drawLineSegment = (ctx, start, end, color, width, isPreview = false) => {
  ctx.strokeStyle = color
  ctx.lineWidth = width
  ctx.lineCap = 'round'

  if (isPreview) {
    ctx.setLineDash([5, 5])
  } else {
    ctx.setLineDash([])
  }

  ctx.beginPath()
  ctx.moveTo(start.x, start.y)
  ctx.lineTo(end.x, end.y)
  ctx.stroke()

  ctx.setLineDash([])
}

/**
 * Отрисовать выделение стены
 * @param {CanvasRenderingContext2D} ctx - контекст canvas
 * @param {Object} wall - объект стены
 */
export const drawSelection = (ctx, wall) => {
  ctx.strokeStyle = '#667eea'
  ctx.lineWidth = 2
  ctx.setLineDash([5, 5])

  wall.points.forEach(point => {
    ctx.beginPath()
    ctx.arc(point.x, point.y, 8, 0, Math.PI * 2)
    ctx.stroke()

    // Закрашиваем точки для лучшей видимости
    ctx.fillStyle = '#667eea'
    ctx.fill()
  })

  ctx.setLineDash([])
}

/**
 * Отрисовать выделение объекта (прямоугольник)
 * @param {CanvasRenderingContext2D} ctx - контекст canvas
 * @param {Object} obj - объект
 */
export const drawObjectSelection = (ctx, obj) => {
  const objWidth = obj.width || 100
  const objHeight = obj.height || 100

  ctx.strokeStyle = '#667eea'
  ctx.lineWidth = 2
  ctx.setLineDash([5, 5])
  ctx.strokeRect(obj.x - objWidth / 2, obj.y - objHeight / 2, objWidth, objHeight)
  ctx.setLineDash([])

  // Рисуем маркеры по углам
  ctx.fillStyle = '#667eea'
  const markerSize = 6
  ctx.fillRect(obj.x - objWidth / 2 - markerSize / 2, obj.y - objHeight / 2 - markerSize / 2, markerSize, markerSize)
  ctx.fillRect(obj.x + objWidth / 2 - markerSize / 2, obj.y - objHeight / 2 - markerSize / 2, markerSize, markerSize)
  ctx.fillRect(obj.x - objWidth / 2 - markerSize / 2, obj.y + objHeight / 2 - markerSize / 2, markerSize, markerSize)
  ctx.fillRect(obj.x + objWidth / 2 - markerSize / 2, obj.y + objHeight / 2 - markerSize / 2, markerSize, markerSize)
}

/**
 * Загрузить SVG изображение
 * @param {string} src - путь к изображению
 * @param {Object} imageCache - кэш изображений
 * @returns {Promise<HTMLImageElement|null>}
 */
export const loadSvgImage = async (src, imageCache) => {
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

/**
 * Отрисовать объект (мебель, оборудование)
 * @param {CanvasRenderingContext2D} ctx - контекст canvas
 * @param {Object} obj - объект
 * @param {Object} iconMap - маппинг иконок
 * @param {Object} imageCache - кэш изображений
 */
export const drawObject = async (ctx, obj, iconMap, imageCache, gridSize) => {
  const iconSrc = iconMap[obj.object_type]

  ctx.save()
  ctx.translate(obj.x, obj.y)
  ctx.rotate((obj.rotation || 0) * Math.PI / 180)

  const objWidth = obj.width || 100
  const objHeight = obj.height || 100

  if (iconSrc) {
    const img = await loadSvgImage(iconSrc, imageCache)
    if (img) {
      ctx.drawImage(img, -objWidth / 2, -objHeight / 2, objWidth, objHeight)
    } else {
      drawPlaceholderRect(ctx, objWidth, objHeight)
    }
  } else {
    drawPlaceholderRect(ctx, objWidth, objHeight)
  }

  ctx.restore()
}

/**
 * Отрисовать прямоугольник-заглушку
 * @param {CanvasRenderingContext2D} ctx - контекст canvas
 * @param {number} width - ширина
 * @param {number} height - высота
 */
const drawPlaceholderRect = (ctx, width, height) => {
  ctx.fillStyle = 'rgba(102, 126, 234, 0.2)'
  ctx.strokeStyle = '#667eea'
  ctx.lineWidth = 2
  ctx.fillRect(-width / 2, -height / 2, width, height)
  ctx.strokeRect(-width / 2, -height / 2, width, height)
}

export default {
  drawGrid,
  drawFieldBounds,
  drawWall,
  drawLineSegment,
  drawSelection,
  drawObjectSelection,
  loadSvgImage,
  drawObject
}
