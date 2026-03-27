/**
 * ObjectPalette - левая панель с инструментами и объектами
 */
<template>
  <div class="object-palette">
    <div class="palette-section">
      <h3 class="palette-title">Инструменты</h3>
      
      <div class="tools-grid">
        <button
          @click="$emit('select-tool', 'select')"
          :class="['tool-btn', { active: currentTool === 'select' }]"
          title="Выделение"
        >
          <span class="tool-icon">🖱️</span>
          <span class="tool-label">Выбор</span>
        </button>

        <button
          @click="$emit('select-tool', 'wall')"
          :class="['tool-btn', { active: currentTool === 'wall' }]"
          title="Стена"
        >
          <span class="tool-icon">🧱</span>
          <span class="tool-label">Стена</span>
        </button>

        <button
          @click="$emit('select-tool', 'door')"
          :class="['tool-btn', { active: currentTool === 'door' }]"
          title="Дверь"
        >
          <span class="tool-icon">🚪</span>
          <span class="tool-label">Дверь</span>
        </button>

        <button
          @click="$emit('select-tool', 'window')"
          :class="['tool-btn', { active: currentTool === 'window' }]"
          title="Окно"
        >
          <span class="tool-icon">🪟</span>
          <span class="tool-label">Окно</span>
        </button>
      </div>
    </div>

    <div class="palette-divider"></div>

    <div class="palette-section">
      <h3 class="palette-title">Объекты</h3>

      <div class="tools-grid">
        <button
          @click="$emit('select-tool', 'workspace')"
          :class="['tool-btn', { active: currentTool === 'workspace' }]"
          title="Рабочее место"
        >
          <span class="tool-icon">🪑</span>
          <span class="tool-label">Место</span>
        </button>

        <button
          @click="$emit('select-tool', 'printer')"
          :class="['tool-btn', { active: currentTool === 'printer' }]"
          title="Принтер"
        >
          <span class="tool-icon">🖨️</span>
          <span class="tool-label">Принтер</span>
        </button>

        <button
          @click="$emit('select-tool', 'kitchen')"
          :class="['tool-btn', { active: currentTool === 'kitchen' }]"
          title="Кухня"
        >
          <span class="tool-icon">☕</span>
          <span class="tool-label">Кухня</span>
        </button>

        <button
          @click="$emit('select-tool', 'staircase')"
          :class="['tool-btn', { active: currentTool === 'staircase' }]"
          title="Лестница"
        >
          <span class="tool-icon">🪜</span>
          <span class="tool-label">Лестница</span>
        </button>

        <button
          @click="$emit('select-tool', 'restroom')"
          :class="['tool-btn', { active: currentTool === 'restroom' }]"
          title="Раздевалка"
        >
          <span class="tool-icon">👔</span>
          <span class="tool-label">Раздевалка</span>
        </button>

        <button
          @click="$emit('select-tool', 'toilet_female')"
          :class="['tool-btn', { active: currentTool === 'toilet_female' }]"
          title="Женский туалет"
        >
          <span class="tool-icon">♀️</span>
          <span class="tool-label">Женский</span>
        </button>

        <button
          @click="$emit('select-tool', 'toilet_male')"
          :class="['tool-btn', { active: currentTool === 'toilet_male' }]"
          title="Мужской туалет"
        >
          <span class="tool-icon">♂️</span>
          <span class="tool-label">Мужской</span>
        </button>

        <button
          @click="$emit('select-tool', 'meeting_room')"
          :class="['tool-btn', { active: currentTool === 'meeting_room' }]"
          title="Переговорная"
        >
          <span class="tool-icon">💬</span>
          <span class="tool-label">Переговорка</span>
        </button>
      </div>
    </div>

    <div class="palette-divider"></div>

    <div class="palette-section">
      <h3 class="palette-title">Настройки</h3>

      <label class="checkbox-label">
        <input type="checkbox" checked />
        <span>Показывать сетку</span>
      </label>

      <div class="field-size-settings">
        <h4 class="settings-subtitle">Размеры поля</h4>
        
        <div class="size-input-group">
          <label for="field-width">Ширина:</label>
          <input
            id="field-width"
            type="number"
            :value="props.fieldWidth"
            @input="handleWidthInput"
            min="50"
            max="500"
            class="size-input"
          />
          <span class="size-unit">клеток</span>
          <span class="size-meters">({{ widthInMeters }}м)</span>
        </div>

        <div class="size-input-group">
          <label for="field-height">Высота:</label>
          <input
            id="field-height"
            type="number"
            :value="props.fieldHeight"
            @input="handleHeightInput"
            min="50"
            max="500"
            class="size-input"
          />
          <span class="size-unit">клеток</span>
          <span class="size-meters">({{ heightInMeters }}м)</span>
        </div>

        <p class="size-hint">1 клетка = 0.5 метра (мин: 50, макс: 500)</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { icons } from '@/components/accets/index.js'

const props = defineProps({
  currentTool: {
    type: String,
    default: 'select'
  },
  fieldWidth: {
    type: Number,
    default: 200
  },
  fieldHeight: {
    type: Number,
    default: 100
  }
})

const emit = defineEmits(['select-tool', 'update-field-size'])

// Вычисляемые значения в метрах
const widthInMeters = computed(() => (props.fieldWidth * 0.5).toFixed(1))
const heightInMeters = computed(() => (props.fieldHeight * 0.5).toFixed(1))

// Функция для получения SVG иконки
const getToolIcon = (toolName) => {
  const iconMap = {
    select: null,
    wall: '🧱',
    door: '🚪',
    window: '🪟',
    workspace: '🪑',
    printer: '🖨️',
    kitchen: icons.kitchen,
    meeting_room: icons.conferenceRoom,
    staircase: icons.ladder,
    ladder: icons.ladder,
    restroom: icons.toiletMan,
    toilet_man: icons.toiletMan,
    toilet_woman: icons.toiletWoman,
    arrow: icons.arrow,
    text: icons.text
  }
  return iconMap[toolName] || null
}

// Обработчики для ограничения ввода
const handleWidthInput = (event) => {
  let value = parseInt(event.target.value)
  // Ограничиваем от 50 до 500
  value = Math.max(50, Math.min(500, value))
  emit('update-field-size', 'width', value)
}

const handleHeightInput = (event) => {
  let value = parseInt(event.target.value)
  // Ограничиваем от 50 до 500
  value = Math.max(50, Math.min(500, value))
  emit('update-field-size', 'height', value)
}
</script>

<style scoped>
.object-palette {
  width: 180px;
  background: #ffffff;
  border-right: 1px solid #e0e0e0;
  padding: 1rem;
  overflow-y: auto;
}

.palette-section {
  margin-bottom: 1rem;
}

.palette-title {
  margin: 0 0 0.75rem 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
}

.tool-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  padding: 0.75rem 0.5rem;
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.tool-btn:hover {
  background: #e8e8e8;
  border-color: #d0d0d0;
}

.tool-btn.active {
  background: #e3f2fd;
  border-color: #2196F3;
  color: #1976D2;
}

.tool-icon {
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tool-icon.svg-icon {
  width: 1.5rem;
  height: 1.5rem;
}

.tool-icon.svg-icon :deep(svg) {
  width: 100%;
  height: 100%;
}

.tool-label {
  font-size: 0.75rem;
  font-weight: 500;
}

.palette-divider {
  height: 1px;
  background: #e0e0e0;
  margin: 1rem 0;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  cursor: pointer;
}

.field-size-settings {
  margin-top: 1rem;
}

.settings-subtitle {
  margin: 0 0 0.75rem 0;
  font-size: 0.8rem;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.size-input-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.size-input-group label {
  font-size: 0.85rem;
  color: #666;
  min-width: 60px;
}

.size-input {
  width: 60px;
  padding: 0.25rem 0.5rem;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 0.9rem;
  text-align: center;
  transition: border-color 0.2s;
}

.size-input:focus {
  outline: none;
  border-color: #2196F3;
}

.size-input:invalid {
  border-color: #f44336;
  background-color: #ffebee;
}

.size-unit,
.size-meters {
  font-size: 0.8rem;
  color: #999;
}

.size-meters {
  color: #4CAF50;
  font-weight: 500;
}

.size-hint {
  margin: 0.5rem 0 0 0;
  font-size: 0.75rem;
  color: #999;
  font-style: italic;
}

/* Scrollbar */
.object-palette::-webkit-scrollbar {
  width: 6px;
}

.object-palette::-webkit-scrollbar-track {
  background: #f5f5f5;
}

.object-palette::-webkit-scrollbar-thumb {
  background: #d0d0d0;
  border-radius: 3px;
}

.object-palette::-webkit-scrollbar-thumb:hover {
  background: #b0b0b0;
}
</style>
