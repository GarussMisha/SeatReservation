# Code Review - Frontend Редактор Помещений

## Архитектура и зависимости

### Структура компонентов:
```
RoomEditor.vue (главный компонент)
├── EditorToolbar.vue (верхняя панель)
├── ObjectPalette.vue (левая панель - инструменты)
├── WallDrawingCanvas.vue (холст для рисования)
└── PropertiesPanel.vue (правая панель - свойства)

Stores:
└── roomEditor.js (Pinia store)

Services:
└── roomObjects.js (API сервис)
```

---

## Критические проблемы

### 1. ❌ RoomEditor.vue - Утечка памяти при unmounted

**Файл:** `src/components/room-editor/RoomEditor.vue:298`

**Проблема:**
```javascript
onUnmounted(() => {
  editorStore.clearEditor()
})
```

При размонтировании компонента полностью очищается store, что приводит к потере всех несохранённых данных.

**Решение:**
```javascript
// Удалить onUnmounted или сохранять состояние
onUnmounted(() => {
  // Только если нужно сохранить данные перед уходом
  // или просто убрать очистку
})
```

---

### 2. ❌ WallDrawingCanvas.vue - Дублирование кода в handleMouseDown

**Файл:** `src/components/room-editor/WallDrawingCanvas.vue:571-643`

**Проблема:** Логика поиска объектов дублируется в `handleMouseDown` и была в удалённой функции `selectWall`.

**Решение:** Вынести в отдельную функцию `findObjectAtPosition(pos)`:
```javascript
const findObjectAtPosition = (pos) => {
  // Сначала ищем стены по линиям
  const allWalls = store.objects.filter(obj =>
    obj.object_type === 'wall' || obj.object_type === 'internal_wall' || obj.object_type === 'window'
  )
  
  for (let wall of allWalls) {
    if (!wall.points) continue
    for (let i = 0; i < wall.points.length - 1; i++) {
      const dist = pointToLineDistance(pos, wall.points[i], wall.points[i + 1])
      if (dist < 10) return wall
    }
  }
  
  // Затем ищем остальные объекты по прямоугольнику
  const otherObjects = store.objects.filter(obj =>
    !['wall', 'internal_wall', 'window'].includes(obj.object_type)
  )
  
  for (let obj of otherObjects) {
    const objWidth = obj.width || 100
    const objHeight = obj.height || 100
    const inX = pos.x >= obj.x - objWidth / 2 && pos.x <= obj.x + objWidth / 2
    const inY = pos.y >= obj.y - objHeight / 2 && pos.y <= obj.y + objHeight / 2
    if (inX && inY) return obj
  }
  
  return null
}
```

---

### 3. ❌ WallDrawingCanvas.vue - Отсутствие debounce для перетаскивания

**Файл:** `src/components/room-editor/WallDrawingCanvas.vue:778-786`

**Проблема:** При перетаскивании объекта `store.updateObject()` вызывается на каждое движение мыши, что создаёт огромную нагрузку.

**Решение:** Добавить throttle/debounce:
```javascript
import { throttle } from 'lodash'

const throttledUpdateObject = throttle((objectId, updates) => {
  store.updateObject(objectId, updates)
}, 100)

// В handleMouseMove:
throttledUpdateObject(selectedWall.value.id, { x: newX, y: newY })
```

---

### 4. ❌ WallDrawingCanvas.vue - Не обрабатывается случай когда canvas.value = null

**Файл:** `src/components/room-editor/WallDrawingCanvas.vue:225-264`

**Проблема:** В `getFieldMousePos` и `getMousePos` есть проверка `if (!canvas.value)`, но она возвращает `{x: 0, y: 0}`, что может привести к некорректному поведению.

**Решение:** Возвращать `null` и проверять в вызывающих функциях:
```javascript
const getFieldMousePos = (e) => {
  if (!canvas.value) return null
  // ... остальной код
}
```

---

### 5. ❌ ObjectPalette.vue - Не используется showGrid

**Файл:** `src/components/room-editor/ObjectPalette.vue:143`

**Проблема:** Чекбокс "Показывать сетку" есть, но он не связан с состоянием и не отправляет событие:
```vue
<label class="checkbox-label">
  <input type="checkbox" checked />
  <span>Показывать сетку</span>
</label>
```

**Решение:**
```vue
<label class="checkbox-label">
  <input 
    type="checkbox" 
    :checked="showGrid"
    @change="$emit('toggle-grid', $event.target.checked)"
  />
  <span>Показывать сетку</span>
</label>
```

И добавить prop и emit:
```javascript
const props = defineProps({
  // ...
  showGrid: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['select-tool', 'update-field-size', 'toggle-snap', 'toggle-grid'])
```

---

## Проблемы производительности

### 6. ⚠️ WallDrawingCanvas.vue - Отрисовка на каждый mousemove

**Файл:** `src/components/room-editor/WallDrawingCanvas.vue:800`

**Проблема:** `await draw()` вызывается на каждое движение мыши при рисовании.

**Решение:** Использовать `requestAnimationFrame`:
```javascript
let animationFrameId = null

const scheduleDraw = () => {
  if (animationFrameId) return
  animationFrameId = requestAnimationFrame(async () => {
    await draw()
    animationFrameId = null
  })
}

// В handleMouseMove:
if (isDrawing.value) {
  scheduleDraw()
}
```

---

### 7. ⚠️ WallDrawingCanvas.vue - Нет очистки кэша изображений

**Файл:** `src/components/room-editor/WallDrawingCanvas.vue:72`

**Проблема:** `imageCache` растёт бесконечно.

**Решение:** Добавить очистку при unmounted:
```javascript
onUnmounted(() => {
  // Очистка кэша
  Object.values(imageCache).forEach(img => {
    if (img.src) img.src = ''
  })
  imageCache = {}
})
```

---

### 8. ⚠️ RoomEditor.vue - Лишние setTimeout для отрисовки

**Файл:** `src/components/room-editor/RoomEditor.vue:121-132, 253-262`

**Проблема:** Два разных `setTimeout` для перерисовки после загрузки/добавления объектов.

**Решение:** Создать единый метод `requestRedraw()`:
```javascript
const requestRedraw = () => {
  setTimeout(() => {
    const canvas = document.querySelector('.wall-canvas')
    if (canvas && canvas._konva) {
      canvas._konva.batchDraw()
    }
  }, 100)
}
```

---

## Проблемы с безопасностью

### 9. 🔒 PropertiesPanel.vue - Нет валидации ввода

**Файл:** `src/components/room-editor/PropertiesPanel.vue:55-57`

**Проблема:** Поле масштаба не имеет ограничений:
```vue
<input
  v-model.number="localScale"
  type="number"
  @change="updateScale(localScale)"
/>
```

**Решение:** Добавить min/max и валидацию:
```vue
<input
  v-model.number="localScale"
  type="number"
  min="10"
  max="500"
  @change="updateScale(localScale)"
/>
```

```javascript
const updateScale = (scalePercent) => {
  if (!props.selectedObject) return
  
  // Ограничиваем от 10% до 500%
  const clampedScale = Math.max(10, Math.min(500, scalePercent))
  const newSize = Math.round(clampedScale / 100 * 100)
  
  emit('update', props.selectedObject.id, {
    width: newSize,
    height: newSize
  })
}
```

---

## Лишний код

### 10. 🗑️ RoomEditor.vue - Дублирующиеся методы

**Файл:** `src/components/room-editor/RoomEditor.vue:154-167`

**Проблема:** Методы `handleSetOffset` и `handleSetZoom` не используются:
```javascript
const handleSetOffset = (newOffset) => {
  editorStore.setOffset(newOffset || { x: 0, y: 0 })
}

const handleSetZoom = (newZoom) => {
  editorStore.setZoom(newZoom)
}
```

**Решение:** Удалить эти методы.

---

### 11. 🗑️ roomEditor.js - Неиспользуемые computed свойства

**Файл:** `src/stores/roomEditor.js:49-57`

**Проблема:** Вычисляемые свойства не используются в компонентах:
```javascript
const walls = computed(() => objects.value.filter(obj => obj.object_type === 'wall'))
const doors = computed(() => objects.value.filter(obj => obj.object_type === 'door'))
const windows = computed(() => objects.value.filter(obj => obj.object_type === 'window'))
const workspaces = computed(() => objects.value.filter(obj => obj.object_type === 'workspace'))
const otherObjects = computed(() => objects.value.filter(obj =>
  !['wall', 'door', 'window', 'workspace'].includes(obj.object_type)
))
```

**Решение:** Удалить или использовать в компонентах.

---

### 12. 🗑️ roomEditor.js - Неиспользуемые методы экспорта/импорта

**Файл:** `src/stores/roomEditor.js:237-251`

**Проблема:** Методы `exportToJSON` и `importFromJSON` не используются.

**Решение:** Удалить или добавить функционал экспорта/импорта в UI.

---

## Проблемы архитектуры

### 13. 🏗️ WallDrawingCanvas.vue - Смешение логики отрисовки и бизнес-логики

**Проблема:** Компонент отвечает и за отрисовку, и за обработку событий мыши, и за перетаскивание объектов.

**Решение:** Разделить на:
- `WallDrawingCanvas.vue` - только отрисовка
- `CanvasInteractions.js` - обработка событий мыши
- `ObjectMover.js` - логика перетаскивания

---

### 14. 🏗️ ObjectPalette.vue - Хардкод иконок

**Файл:** `src/components/room-editor/ObjectPalette.vue:253-268`

**Проблема:** Функция `getToolIcon` дублирует маппинг который уже есть в template.

**Решение:** Удалить функцию, использовать напрямую из `icons`.

---

## Улучшения UX

### 15. ✨ PropertiesPanel.vue - Нет подтверждения удаления

**Проблема:** Кнопка удаления объекта не запрашивает подтверждение.

**Решение:**
```javascript
const handleDelete = () => {
  if (confirm('Вы уверены, что хотите удалить этот объект?')) {
    emit('delete', props.selectedObject.id)
  }
}
```

---

### 16. ✨ WallDrawingCanvas.vue - Нет визуальной обратной связи при перетаскивании точки стены

**Проблема:** Не видно, какая точка перетаскивается.

**Решение:** Добавить подсветку активной точки в `drawSelection`:
```javascript
const drawSelection = (wall) => {
  const c = ctx.value
  wall.points.forEach((point, idx) => {
    c.beginPath()
    const isHovered = idx === draggedPointIndex.value && isDraggingWallPoint.value
    c.arc(point.x, point.y, isHovered ? 10 : 8, 0, Math.PI * 2)
    c.fillStyle = isHovered ? '#4CAF50' : '#667eea'
    c.fill()
    c.strokeStyle = '#667eea'
    c.stroke()
  })
}
```

---

### 17. ✨ ObjectPalette.vue - Нет горячих клавиш для инструментов

**Решение:** Добавить обработку клавиш:
```javascript
const handleKeyDown = (e) => {
  const keyMap = {
    '1': 'select',
    '2': 'wall',
    '3': 'internal_wall',
    '4': 'window',
    '5': 'workspace',
    '6': 'printer'
  }
  
  if (keyMap[e.key]) {
    emit('select-tool', keyMap[e.key])
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown)
})
```

---

## Итоговый список изменений

### Критические (❌):
1. Удалить `onUnmounted` из RoomEditor.vue
2. Вынести `findObjectAtPosition` в отдельную функцию
3. Добавить throttle для `updateObject` при перетаскивании
4. Исправить обработку `canvas.value = null`
5. Исправить чекбокс "Показывать сетку"

### Производительность (⚠️):
6. Использовать `requestAnimationFrame` для отрисовки
7. Добавить очистку кэша изображений
8. Создать единый метод `requestRedraw()`

### Безопасность (🔒):
9. Добавить валидацию поля масштаба

### Лишний код (🗑️):
10. Удалить `handleSetOffset` и `handleSetZoom`
11. Удалить неиспользуемые computed свойства
12. Удалить `exportToJSON` и `importFromJSON`

### Улучшения (✨):
15. Добавить подтверждение удаления
16. Подсветка активной точки стены
17. Горячие клавиши для инструментов

---

## Оценка качества кода

| Критерий | Оценка | Комментарий |
|----------|--------|-------------|
| Читаемость | 7/10 | Хорошая структура, но есть дублирование |
| Производительность | 5/10 | Много вызовов draw(), нет throttle |
| Безопасность | 6/10 | Нет валидации ввода |
| Архитектура | 6/10 | Смешение ответственности |
| Тестируемость | 4/10 | Нет тестов, сильная связанность |
| **Общая** | **5.7/10** | Требует рефакторинга |
