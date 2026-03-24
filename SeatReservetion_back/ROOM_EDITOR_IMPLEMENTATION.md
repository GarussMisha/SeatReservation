# 🏗️ Визуальный редактор помещений

## 📊 Статус реализации

### ✅ Завершено

#### Backend (ШАГИ 1-2)
- ✅ Модели данных для объектов помещения
  - `RoomObject` - базовая модель для всех объектов
  - `WorkspaceOnPlan` - рабочие места на плане
  - `Wall` - стены
  - `Door` - двери
  - `Window` - окна
- ✅ API endpoints для управления объектами
  - CRUD для RoomObject
  - Специализированные endpoints для стен, дверей, окон
  - Endpoints для сохранения/загрузки плана помещения

#### API Endpoints

**Получение объектов:**
```
GET /api/v1/rooms/{room_id}/objects - получить все объекты помещения
GET /api/v1/rooms/objects/{object_id} - получить объект по ID
GET /api/v1/rooms/{room_id}/plan - получить весь план помещения
```

**Создание объектов:**
```
POST /api/v1/rooms/{room_id}/objects - создать объект
POST /api/v1/rooms/walls - создать стену
POST /api/v1/rooms/doors - создать дверь
POST /api/v1/rooms/windows - создать окно
POST /api/v1/rooms/workspaces-on-plan - создать рабочее место на плане
POST /api/v1/rooms/{room_id}/plan - сохранить весь план
```

**Обновление/Удаление:**
```
PUT /api/v1/rooms/objects/{object_id} - обновить объект
PUT /api/v1/rooms/workspaces-on-plan/{wp_id} - обновить рабочее место
DELETE /api/v1/rooms/objects/{object_id} - удалить объект
```

### 🚧 В процессе

#### Frontend (ШАГИ 3-13)
- ⏳ Установка зависимостей (vue-konva, konva)
- ⏳ Store для редактора помещений
- ⏳ Компоненты редактора

---

## 📋 Структура моделей данных

```
Room
├── workspaces (Workspace)
└── room_objects (RoomObject)
    ├── workspace_data (WorkspaceOnPlan)
    ├── wall_data (Wall)
    ├── door_data (Door)
    └── window_data (Window)
```

---

## 🎯 Типы объектов

Поддерживаемые типы объектов (`object_type`):
- `wall` - стена
- `door` - дверь
- `window` - окно
- `workspace` - рабочее место
- `printer` - принтер
- `kitchen` - кухня
- `meeting_room` - переговорная
- `staircase` - лестница
- `restroom` - комната отдыха

---

## 📝 Пример данных объекта

```json
{
  "id": 1,
  "room_id": 1,
  "object_type": "workspace",
  "x": 100.0,
  "y": 200.0,
  "rotation": 0,
  "width": 100.0,
  "height": 50.0,
  "name": "Рабочее место 1",
  "description": "Описание",
  "is_active": true,
  "properties": {
    "has_monitor": true,
    "has_chair": true
  },
  "created_at": "2026-03-24T12:00:00",
  "updated_at": "2026-03-24T12:00:00"
}
```

---

## 🔧 Следующие шаги

1. Установка vue-konva и konva
2. Создание store для редактора
3. Создание базовых компонентов редактора

---

**Дата создания:** 24 марта 2026 г.
**Последнее обновление:** 24 марта 2026 г.
