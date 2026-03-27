/**
 * Тесты для roomEditor store
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useRoomEditorStore } from './roomEditor'

describe('roomEditor Store', () => {
  let store

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useRoomEditorStore()
  })

  describe('initial state', () => {
    it('должен иметь начальное состояние', () => {
      expect(store.currentRoom).toBeNull()
      expect(store.objects).toEqual([])
      expect(store.selectedObject).toBeNull()
      expect(store.currentTool).toBe('select')
      expect(store.history).toEqual([])
      expect(store.historyIndex).toBe(-1)
      expect(store.zoom).toBe(1)
      expect(store.offset).toBeNull()
      expect(store.gridSize).toBe(20)
      expect(store.showGrid).toBe(true)
      expect(store.fieldWidth).toBe(50)
      expect(store.fieldHeight).toBe(50)
    })
  })

  describe('setCurrentRoom', () => {
    it('должен установить текущее помещение', () => {
      const room = { id: 1, name: 'Test Room' }

      store.setCurrentRoom(room)

      expect(store.currentRoom).toEqual(room)
    })
  })

  describe('setTool', () => {
    it('должен установить инструмент', () => {
      store.setTool('wall')

      expect(store.currentTool).toBe('wall')
    })

    it('должен сбросить выделенный объект', () => {
      store.selectObject({ id: 1 })
      store.setTool('wall')

      expect(store.selectedObject).toBeNull()
    })
  })

  describe('addObject', () => {
    it('должен добавить объект', () => {
      const object = {
        id: 1,
        object_type: 'workspace',
        x: 100,
        y: 200
      }

      store.addObject(object)

      expect(store.objects).toHaveLength(1)
      expect(store.objects[0]).toEqual(expect.objectContaining({
        id: 1,
        object_type: 'workspace',
        x: 100,
        y: 200
      }))
    })

    it('должен добавить объект с значениями по умолчанию', () => {
      const object = {
        id: 1,
        object_type: 'printer'
      }

      store.addObject(object)

      expect(store.objects[0]).toEqual(expect.objectContaining({
        x: 0,
        y: 0,
        rotation: 0,
        width: 100,
        height: 50,
        is_active: true
      }))
    })

    it('должен добавить запись в историю', () => {
      store.addObject({ id: 1, object_type: 'workspace' })

      expect(store.history).toHaveLength(1)
      expect(store.historyIndex).toBe(0)
    })
  })

  describe('updateObject', () => {
    beforeEach(() => {
      store.addObject({ id: 1, object_type: 'workspace', x: 100, y: 100 })
    })

    it('должен обновить объект', () => {
      store.updateObject(1, { x: 200 })

      expect(store.objects[0].x).toBe(200)
    })

    it('не должен изменить несуществующий объект', () => {
      store.updateObject(999, { x: 200 })

      expect(store.objects[0].x).toBe(100)
    })

    it('должен добавить запись в историю', () => {
      store.updateObject(1, { x: 200 })

      expect(store.history).toHaveLength(2) // 1 от addObject + 1 от updateObject
    })
  })

  describe('deleteObject', () => {
    beforeEach(() => {
      store.addObject({ id: 1, object_type: 'workspace' })
    })

    it('должен удалить объект', () => {
      store.deleteObject(1)

      expect(store.objects).toHaveLength(0)
    })

    it('должен сбросить выделение если объект был выделен', () => {
      store.selectObject(store.objects[0])
      store.deleteObject(1)

      expect(store.selectedObject).toBeNull()
    })

    it('не должен удалить несуществующий объект', () => {
      store.deleteObject(999)

      expect(store.objects).toHaveLength(1)
    })
  })

  describe('selectObject', () => {
    it('должен выбрать объект', () => {
      const object = { id: 1, object_type: 'workspace' }

      store.selectObject(object)

      expect(store.selectedObject).toEqual(object)
    })

    it('должен снять выделение при null', () => {
      store.selectObject({ id: 1 })
      store.selectObject(null)

      expect(store.selectedObject).toBeNull()
    })
  })

  describe('setFieldWidth', () => {
    it('должен установить ширину поля', () => {
      store.setFieldWidth(100)

      expect(store.fieldWidth).toBe(100)
    })

    it('должен ограничить минимальную ширину', () => {
      store.setFieldWidth(10)

      expect(store.fieldWidth).toBe(50) // минимум
    })

    it('должен ограничить максимальную ширину', () => {
      store.setFieldWidth(1000)

      expect(store.fieldWidth).toBe(500) // максимум
    })
  })

  describe('setFieldHeight', () => {
    it('должен установить высоту поля', () => {
      store.setFieldHeight(100)

      expect(store.fieldHeight).toBe(100)
    })

    it('должен ограничить минимальную высоту', () => {
      store.setFieldHeight(10)

      expect(store.fieldHeight).toBe(50)
    })

    it('должен ограничить максимальную высоту', () => {
      store.setFieldHeight(1000)

      expect(store.fieldHeight).toBe(500)
    })
  })

  describe('setZoom', () => {
    it('должен установить масштаб', () => {
      store.setZoom(2)

      expect(store.zoom).toBe(2)
    })

    it('должен ограничить минимальный масштаб', () => {
      store.setZoom(0.1)

      expect(store.zoom).toBe(0.2)
    })

    it('должен ограничить максимальный масштаб', () => {
      store.setZoom(5)

      expect(store.zoom).toBe(3)
    })
  })

  describe('setOffset', () => {
    it('должен установить позицию', () => {
      const offset = { x: 100, y: 200 }

      store.setOffset(offset)

      expect(store.offset).toEqual({ x: 100, y: 200 })
    })
  })

  describe('clearEditor', () => {
    beforeEach(() => {
      store.addObject({ id: 1, object_type: 'workspace' })
      store.selectObject(store.objects[0])
      store.setTool('wall')
      store.setZoom(2)
    })

    it('должен очистить все объекты', () => {
      store.clearEditor()

      expect(store.objects).toHaveLength(0)
    })

    it('должен сбросить инструмент', () => {
      store.clearEditor()

      expect(store.currentTool).toBe('select')
    })

    it('должен сбросить выделение', () => {
      store.clearEditor()

      expect(store.selectedObject).toBeNull()
    })

    it('должен сбросить историю', () => {
      store.clearEditor()

      expect(store.history).toHaveLength(0)
      expect(store.historyIndex).toBe(-1)
    })

    it('должен сбросить масштаб', () => {
      store.clearEditor()

      expect(store.zoom).toBe(1)
    })

    it('не должен сбрасывать offset', () => {
      store.setOffset({ x: 100, y: 100 })
      store.clearEditor()

      expect(store.offset).toEqual({ x: 100, y: 100 })
    })

    it('должен сохранить currentRoom', () => {
      store.setCurrentRoom({ id: 1, name: 'Test' })
      store.clearEditor()

      expect(store.currentRoom).toEqual({ id: 1, name: 'Test' })
    })
  })

  describe('undo/redo', () => {
    beforeEach(() => {
      store.addObject({ id: 1, object_type: 'workspace', x: 100 })
      store.updateObject(1, { x: 200 })
      store.updateObject(1, { x: 300 })
    })

    it('должен отменить последнее действие', () => {
      store.undo()

      expect(store.objects[0].x).toBe(200)
    })

    it('должен вернуть canUndo в false после отмены к началу', () => {
      store.undo()
      store.undo()

      expect(store.canUndo).toBe(false)
    })

    it('должен повторить отменённое действие', () => {
      store.undo()
      store.redo()

      expect(store.objects[0].x).toBe(300)
    })

    it('должен вернуть canRedo в false после повтора к концу', () => {
      store.undo()
      store.redo()

      expect(store.canRedo).toBe(false)
    })
  })

  describe('loadObjects', () => {
    it('должен загрузить объекты', () => {
      const objects = [
        { id: 1, object_type: 'workspace', x: 100, y: 100 },
        { id: 2, object_type: 'printer', x: 200, y: 200 }
      ]

      store.loadObjects(objects)

      expect(store.objects).toHaveLength(2)
      expect(store.objects[0].id).toBe(1)
    })

    it('должен восстановить points для стен', () => {
      const objects = [
        {
          id: 1,
          object_type: 'wall',
          properties: {
            points: [
              { x: 0, y: 0 },
              { x: 100, y: 100 }
            ]
          }
        }
      ]

      store.loadObjects(objects)

      expect(store.objects[0].points).toEqual([
        { x: 0, y: 0 },
        { x: 100, y: 100 }
      ])
    })
  })

  describe('computed properties', () => {
    beforeEach(() => {
      store.addObject({ id: 1, object_type: 'workspace' })
      store.addObject({ id: 2, object_type: 'wall' })
      store.addObject({ id: 3, object_type: 'printer' })
    })

    it('должен вычислять canUndo', () => {
      expect(store.canUndo).toBe(true)
    })

    it('должен вычислять canRedo', () => {
      expect(store.canRedo).toBe(false)
    })
  })
})
