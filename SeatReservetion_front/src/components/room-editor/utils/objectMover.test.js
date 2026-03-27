/**
 * Тесты для утилиты ObjectMover
 */

import { describe, it, expect } from 'vitest'
import {
  startDragging,
  startDraggingWallPoint,
  updateDragPosition,
  updateWallPointPosition,
  stopDragging,
  stopDraggingWallPoint,
  findObjectAtPosition,
  findWallPointAtPosition
} from './objectMover'

// Мок функции расстояния
const mockPointToLineDistance = (point, lineStart, lineEnd) => {
  return 5 // Возвращаем меньше 10 для теста попадания
}

describe('ObjectMover', () => {
  describe('startDragging', () => {
    it('должен вернуть данные для перетаскивания', () => {
      const object = { id: 1, x: 100, y: 200, object_type: 'workspace' }
      const pos = { x: 150, y: 250 }

      const result = startDragging(object, pos)

      expect(result).toEqual({
        isDragging: true,
        dragStart: {
          x: 50, // 150 - 100
          y: 50  // 250 - 200
        },
        draggedObject: object
      })
    })

    it('должен вернуть null для null объекта', () => {
      const result = startDragging(null, { x: 0, y: 0 })
      expect(result).toBeNull()
    })
  })

  describe('startDraggingWallPoint', () => {
    it('должен вернуть данные для перетаскивания точки стены', () => {
      const wall = {
        id: 1,
        object_type: 'wall',
        points: [
          { x: 0, y: 0 },
          { x: 100, y: 100 },
          { x: 200, y: 200 }
        ]
      }

      const result = startDraggingWallPoint(wall, 1)

      expect(result).toEqual({
        isDraggingWallPoint: true,
        draggedPointIndex: 1,
        draggedWall: wall
      })
    })

    it('должен вернуть null для стены без points', () => {
      const wall = { id: 1, object_type: 'wall' }
      const result = startDraggingWallPoint(wall, 0)
      expect(result).toBeNull()
    })

    it('должен вернуть null для некорректного индекса', () => {
      const wall = {
        id: 1,
        object_type: 'wall',
        points: [{ x: 0, y: 0 }]
      }

      const result = startDraggingWallPoint(wall, 5)
      expect(result).toBeNull()
    })
  })

  describe('updateDragPosition', () => {
    it('должен вычислить новую позицию', () => {
      const pos = { x: 300, y: 400 }
      const dragStart = { x: 50, y: 50 }
      const object = { x: 100, y: 200 }

      const result = updateDragPosition(pos, dragStart, object)

      expect(result).toEqual({
        x: 250, // 300 - 50
        y: 350  // 400 - 50
      })
    })
  })

  describe('updateWallPointPosition', () => {
    it('должен обновить позицию точки', () => {
      const points = [
        { x: 0, y: 0 },
        { x: 100, y: 100 },
        { x: 200, y: 200 }
      ]
      const newPos = { x: 150, y: 150 }

      const result = updateWallPointPosition(points, 1, newPos)

      expect(result).toHaveLength(3)
      expect(result[1]).toEqual({ x: 150, y: 150 })
      expect(result[0]).toEqual({ x: 0, y: 0 }) // Первая точка не изменилась
    })

    it('не должен изменять оригинальный массив', () => {
      const points = [{ x: 0, y: 0 }]
      const newPos = { x: 100, y: 100 }

      updateWallPointPosition(points, 0, newPos)

      expect(points[0]).toEqual({ x: 0, y: 0 })
    })
  })

  describe('stopDragging', () => {
    it('должен сбросить состояние перетаскивания', () => {
      const result = stopDragging()

      expect(result).toEqual({
        isDragging: false,
        dragStart: { x: 0, y: 0 },
        draggedObject: null
      })
    })
  })

  describe('stopDraggingWallPoint', () => {
    it('должен сбросить состояние перетаскивания точки', () => {
      const result = stopDraggingWallPoint()

      expect(result).toEqual({
        isDraggingWallPoint: false,
        draggedPointIndex: -1,
        draggedWall: null
      })
    })
  })

  describe('findObjectAtPosition', () => {
    const objects = [
      {
        id: 1,
        object_type: 'wall',
        points: [
          { x: 0, y: 0 },
          { x: 100, y: 100 }
        ]
      },
      {
        id: 2,
        object_type: 'workspace',
        x: 200,
        y: 200,
        width: 100,
        height: 100
      }
    ]

    it('должен найти стену по линии', () => {
      const pos = { x: 50, y: 50 } // На линии стены

      const result = findObjectAtPosition(pos, objects, mockPointToLineDistance)

      expect(result).toEqual(objects[0])
    })

    it('должен найти объект по прямоугольнику', () => {
      const pos = { x: 220, y: 220 } // Внутри workspace (200±50)

      // Возвращаем большое расстояние для стен
      const longDistance = () => 100

      const result = findObjectAtPosition(pos, objects, longDistance)

      expect(result).toEqual(objects[1])
    })

    it('должен вернуть null если ничего не найдено', () => {
      const pos = { x: 1000, y: 1000 }
      const longDistance = () => 100

      const result = findObjectAtPosition(pos, objects, longDistance)

      expect(result).toBeNull()
    })

    it('должен обработать пустой массив объектов', () => {
      const pos = { x: 0, y: 0 }

      const result = findObjectAtPosition(pos, [], mockPointToLineDistance)

      expect(result).toBeNull()
    })

    it('должен обработать null pos', () => {
      const result = findObjectAtPosition(null, objects, mockPointToLineDistance)
      expect(result).toBeNull()
    })
  })

  describe('findWallPointAtPosition', () => {
    const wall = {
      id: 1,
      object_type: 'wall',
      points: [
        { x: 0, y: 0 },
        { x: 100, y: 100 },
        { x: 200, y: 200 }
      ]
    }

    it('должен найти точку в радиусе', () => {
      const pos = { x: 5, y: 5 } // В радиусе 10 от первой точки

      const result = findWallPointAtPosition(pos, wall, 10)

      expect(result).toBe(0)
    })

    it('должен вернуть null если точка вне радиуса', () => {
      const pos = { x: 50, y: 50 } // Между точками

      const result = findWallPointAtPosition(pos, wall, 10)

      expect(result).toBeNull()
    })

    it('должен обработать null wall', () => {
      const result = findWallPointAtPosition({ x: 0, y: 0 }, null, 10)
      expect(result).toBeNull()
    })

    it('должен обработать стену без points', () => {
      const wallWithoutPoints = { id: 1, object_type: 'wall' }
      const result = findWallPointAtPosition({ x: 0, y: 0 }, wallWithoutPoints, 10)
      expect(result).toBeNull()
    })
  })
})
