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
          <span class="tool-icon">🍳</span>
          <span class="tool-label">Кухня</span>
        </button>

        <button
          @click="$emit('select-tool', 'meeting_room')"
          :class="['tool-btn', { active: currentTool === 'meeting_room' }]"
          title="Переговорная"
        >
          <span class="tool-icon">💬</span>
          <span class="tool-label">Переговорка</span>
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
          title="Комната отдыха"
        >
          <span class="tool-icon">🛋️</span>
          <span class="tool-label">Отдых</span>
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
    </div>
  </div>
</template>

<script setup>
defineProps({
  currentTool: {
    type: String,
    default: 'select'
  }
})

defineEmits(['select-tool'])
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
