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
          @click="$emit('select-tool', 'internal_wall')"
          :class="['tool-btn', { active: currentTool === 'internal_wall' }]"
          title="Перегородка"
        >
          <span class="tool-icon">📏</span>
          <span class="tool-label">Перегородка</span>
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
          <img :src="icons.desktop" class="tool-icon svg-icon" alt="Рабочее место" />
          <span class="tool-label">Место</span>
        </button>

        <button
          @click="$emit('select-tool', 'printer')"
          :class="['tool-btn', { active: currentTool === 'printer' }]"
          title="Принтер"
        >
          <img :src="icons.printer" class="tool-icon svg-icon" alt="Принтер" />
          <span class="tool-label">Принтер</span>
        </button>

        <button
          @click="$emit('select-tool', 'kitchen')"
          :class="['tool-btn', { active: currentTool === 'kitchen' }]"
          title="Кухня"
        >
          <img :src="icons.kitchen" class="tool-icon svg-icon" alt="Кухня" />
          <span class="tool-label">Кухня</span>
        </button>

        <button
          @click="$emit('select-tool', 'staircase')"
          :class="['tool-btn', { active: currentTool === 'staircase' }]"
          title="Лестница"
        >
          <img :src="icons.ladder" class="tool-icon svg-icon" alt="Лестница" />
          <span class="tool-label">Лестница</span>
        </button>

        <button
          @click="$emit('select-tool', 'restroom')"
          :class="['tool-btn', { active: currentTool === 'restroom' }]"
          title="Раздевалка"
        >
          <img :src="icons.hanger" class="tool-icon svg-icon" alt="Раздевалка" />
          <span class="tool-label">Раздевалка</span>
        </button>

        <button
          @click="$emit('select-tool', 'toilet_female')"
          :class="['tool-btn', { active: currentTool === 'toilet_female' }]"
          title="Женский туалет"
        >
          <img :src="icons.toiletWoman" class="tool-icon svg-icon" alt="Женский" />
          <span class="tool-label">Женский</span>
        </button>

        <button
          @click="$emit('select-tool', 'toilet_male')"
          :class="['tool-btn', { active: currentTool === 'toilet_male' }]"
          title="Мужской туалет"
        >
          <img :src="icons.toiletMan" class="tool-icon svg-icon" alt="Мужской" />
          <span class="tool-label">Мужской</span>
        </button>

        <button
          @click="$emit('select-tool', 'meeting_room')"
          :class="['tool-btn', { active: currentTool === 'meeting_room' }]"
          title="Переговорная"
        >
          <img :src="icons.conferenceRoom" class="tool-icon svg-icon" alt="Переговорная" />
          <span class="tool-label">Переговорка</span>
        </button>
      </div>
    </div>

    <div class="palette-divider"></div>

    <div class="palette-section">
      <h3 class="palette-title">Настройки</h3>

      <label class="checkbox-label">
        <input 
          v-model="snapToGridEnabled"
          type="checkbox"
          @change="$emit('toggle-snap', snapToGridEnabled)"
        />
        <span>Привязка к сетке</span>
      </label>

      <label class="checkbox-label">
        <input 
          type="checkbox" 
          :checked="showGrid"
          @change="$emit('toggle-grid', $event.target.checked)"
        />
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

    <!-- Подсказки для рисования стен (внизу панели) -->
    <div class="palette-divider"></div>

    <!-- Подсказка перед началом рисования -->
    <div v-if="!isDrawing && (currentTool === 'wall' || currentTool === 'internal_wall')" class="drawing-hint info">
      <div class="hint-content">
        <svg class="hint-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122"/>
        </svg>
        <div class="hint-text">
          <p><strong>Кликните</strong> для начала рисования</p>
          <p><strong>ПКМ</strong> для завершения линии</p>
        </div>
      </div>
    </div>

    <!-- Подсказка при рисовании -->
    <div v-if="isDrawing" class="drawing-hint">
      <div class="hint-content">
        <svg class="hint-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
        </svg>
        <div class="hint-text">
          <p><strong>Длина:</strong> {{ currentLineLength }} м</p>
          <p><strong>ПКМ</strong> для завершения</p>
          <p><strong>ESC</strong> для отмены</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
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
  },
  isDrawing: {
    type: Boolean,
    default: false
  },
  currentLineLength: {
    type: [String, Number],
    default: '0'
  },
  showGrid: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['select-tool', 'update-field-size', 'toggle-snap', 'toggle-grid'])

// Состояние привязки к сетке
const snapToGridEnabled = ref(true)

// Вычисляемые значения в метрах
const widthInMeters = computed(() => (props.fieldWidth * 0.5).toFixed(1))
const heightInMeters = computed(() => (props.fieldHeight * 0.5).toFixed(1))

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
  width: 220px;
  min-width: 220px;
  background: #ffffff;
  border-right: 1px solid #e0e0e0;
  padding: 1rem;
  overflow-y: auto;
  flex-shrink: 0;
}

/* Подсказка при рисовании */
.drawing-hint {
  margin-top: 1rem;
  background: rgba(255, 243, 199, 0.95);
  border: 2px solid #f59e0b;
  padding: 16px 20px;
  border-radius: 8px;
  pointer-events: none;
  z-index: 10;
  width: 100%;
  box-sizing: border-box;
}

.drawing-hint.info {
  background: rgba(227, 242, 253, 0.95);
  border-color: #2196F3;
}

.drawing-hint.info .hint-text strong {
  color: #1976D2;
}

.hint-content {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  width: 100%;
}

.hint-icon-svg {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
  color: var(--primary-start);
}

.hint-text {
  text-align: left;
  flex: 1;
  min-width: 0;
}

.hint-text p {
  font-size: 0.85rem;
  color: #475569;
  margin: 4px 0;
  line-height: 1.3;
  word-wrap: break-word;
}

.hint-text strong {
  color: #f59e0b;
  font-weight: 600;
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
  width: 2rem;
  height: 2rem;
  object-fit: contain;
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
