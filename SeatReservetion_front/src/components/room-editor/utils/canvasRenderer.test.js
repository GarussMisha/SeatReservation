/**
 * Тесты для утилиты CanvasRenderer
 */

import { describe, it, expect, vi } from 'vitest'
import {
  drawGrid,
  drawFieldBounds,
  drawWall,
  drawLineSegment,
  drawSelection,
  drawObjectSelection,
  loadSvgImage
} from './canvasRenderer'

describe('CanvasRenderer', () => {
  // Мок контекста canvas
  const createMockContext = () => ({
    strokeStyle: '',
    lineWidth: 0,
    lineCap: '',
    lineJoin: '',
    fillStyle: '',
    font: '',
    beginPath: vi.fn(),
    moveTo: vi.fn(),
    lineTo: vi.fn(),
    stroke: vi.fn(),
    fill: vi.fn(),
    arc: vi.fn(),
    fillRect: vi.fn(),
    strokeRect: vi.fn(),
    setLineDash: vi.fn(),
    fillText: vi.fn(),
    save: vi.fn(),
    restore: vi.fn(),
    translate: vi.fn(),
    rotate: vi.fn(),
    drawImage: vi.fn()
  })

  describe('drawGrid', () => {
    it('должен нарисовать сетку', () => {
      const ctx = createMockContext()
      const fieldWidth = 10
      const fieldHeight = 10
      const gridSize = 20

      drawGrid(ctx, fieldWidth, fieldHeight, gridSize)

      // Проверяем, что beginPath вызывался для линий сетки
      expect(ctx.beginPath).toHaveBeenCalled()
      expect(ctx.moveTo).toHaveBeenCalled()
      expect(ctx.lineTo).toHaveBeenCalled()
      expect(ctx.stroke).toHaveBeenCalled()
    })

    it('должен установить стили для сетки', () => {
      const ctx = createMockContext()

      drawGrid(ctx, 10, 10, 20)

      expect(ctx.strokeStyle).toBe('#e2e8f0')
      expect(ctx.lineWidth).toBe(1)
    })
  })

  describe('drawFieldBounds', () => {
    it('должен нарисовать границы поля', () => {
      const ctx = createMockContext()

      drawFieldBounds(ctx, 10, 10, 20)

      expect(ctx.strokeRect).toHaveBeenCalled()
      expect(ctx.fillText).toHaveBeenCalledTimes(2) // Подписи размеров
    })

    it('должен установить стили для границ', () => {
      const ctx = createMockContext()

      drawFieldBounds(ctx, 10, 10, 20)

      expect(ctx.strokeStyle).toBe('#94a3b8')
      expect(ctx.lineWidth).toBe(2)
    })
  })

  describe('drawWall', () => {
    it('должен нарисовать стену по точкам', () => {
      const ctx = createMockContext()
      const wall = {
        points: [
          { x: 0, y: 0 },
          { x: 100, y: 100 },
          { x: 200, y: 200 }
        ]
      }

      drawWall(ctx, wall)

      expect(ctx.beginPath).toHaveBeenCalled()
      expect(ctx.moveTo).toHaveBeenCalledWith(0, 0)
      expect(ctx.lineTo).toHaveBeenCalledWith(100, 100)
      expect(ctx.lineTo).toHaveBeenCalledWith(200, 200)
      expect(ctx.stroke).toHaveBeenCalled()
    })

    it('не должен рисовать стену без точек', () => {
      const ctx = createMockContext()
      const wall = { points: [] }

      drawWall(ctx, wall)

      expect(ctx.beginPath).not.toHaveBeenCalled()
    })

    it('должен установить стили для стены', () => {
      const ctx = createMockContext()
      const wall = { points: [{ x: 0, y: 0 }, { x: 100, y: 100 }] }

      drawWall(ctx, wall, '#ff0000', 5)

      expect(ctx.strokeStyle).toBe('#ff0000')
      expect(ctx.lineWidth).toBe(5)
    })
  })

  describe('drawLineSegment', () => {
    it('должен нарисовать сегмент линии', () => {
      const ctx = createMockContext()
      const start = { x: 0, y: 0 }
      const end = { x: 100, y: 100 }

      drawLineSegment(ctx, start, end, '#000000', 2)

      expect(ctx.beginPath).toHaveBeenCalled()
      expect(ctx.moveTo).toHaveBeenCalledWith(0, 0)
      expect(ctx.lineTo).toHaveBeenCalledWith(100, 100)
      expect(ctx.stroke).toHaveBeenCalled()
    })

    it('должен рисовать пунктирную линию для preview', () => {
      const ctx = createMockContext()

      drawLineSegment(ctx, { x: 0, y: 0 }, { x: 100, y: 100 }, '#000', 2, true)

      expect(ctx.setLineDash).toHaveBeenCalledWith([5, 5])
    })

    it('должен сбросить lineDash после рисования', () => {
      const ctx = createMockContext()

      drawLineSegment(ctx, { x: 0, y: 0 }, { x: 100, y: 100 }, '#000', 2, true)

      expect(ctx.setLineDash).toHaveBeenCalledWith([])
    })
  })

  describe('drawSelection', () => {
    it('должен нарисовать выделение для каждой точки', () => {
      const ctx = createMockContext()
      const wall = {
        points: [
          { x: 0, y: 0 },
          { x: 100, y: 100 }
        ]
      }

      drawSelection(ctx, wall)

      // Для каждой точки: arc, stroke, fill
      expect(ctx.arc).toHaveBeenCalledTimes(2)
      expect(ctx.stroke).toHaveBeenCalledTimes(2)
      expect(ctx.fill).toHaveBeenCalledTimes(2)
    })

    it('должен установить стили для выделения', () => {
      const ctx = createMockContext()
      const wall = { points: [{ x: 0, y: 0 }] }

      drawSelection(ctx, wall)

      expect(ctx.strokeStyle).toBe('#667eea')
      expect(ctx.lineWidth).toBe(2)
    })
  })

  describe('drawObjectSelection', () => {
    it('должен нарисовать прямоугольник выделения', () => {
      const ctx = createMockContext()
      const obj = {
        x: 100,
        y: 100,
        width: 100,
        height: 100
      }

      drawObjectSelection(ctx, obj)

      expect(ctx.strokeRect).toHaveBeenCalled()
      expect(ctx.fillRect).toHaveBeenCalledTimes(4) // 4 маркера по углам
    })

    it('должен использовать размеры по умолчанию', () => {
      const ctx = createMockContext()
      const obj = { x: 0, y: 0 }

      drawObjectSelection(ctx, obj)

      expect(ctx.strokeRect).toHaveBeenCalled()
    })
  })

  describe('loadSvgImage', () => {
    it('должен вернуть изображение из кэша', async () => {
      const imageCache = {}
      const mockImg = { src: '/test.svg' }
      imageCache['/test.svg'] = mockImg

      const result = await loadSvgImage('/test.svg', imageCache)

      expect(result).toBe(mockImg)
    })

    it('должен загрузить новое изображение', async () => {
      const imageCache = {}
      const originalImage = global.Image

      // Мок Image
      global.Image = vi.fn(() => ({
        src: '',
        onload: null,
        onerror: null
      }))

      const loadPromise = loadSvgImage('/new.svg', imageCache)

      // Симулируем загрузку
      const mockImg = global.Image.mock.results[0].value
      mockImg.onload()

      const result = await loadPromise

      expect(result).toBeDefined()
      expect(imageCache['/new.svg']).toBeDefined()

      // Восстанавливаем Image
      global.Image = originalImage
    })

    it('должен вернуть null при ошибке загрузки', async () => {
      const imageCache = {}
      const originalImage = global.Image

      global.Image = vi.fn(() => ({
        src: '',
        onload: null,
        onerror: null
      }))

      const loadPromise = loadSvgImage('/invalid.svg', imageCache)

      const mockImg = global.Image.mock.results[0].value
      mockImg.onerror()

      const result = await loadPromise

      expect(result).toBeNull()

      global.Image = originalImage
    })
  })
})
