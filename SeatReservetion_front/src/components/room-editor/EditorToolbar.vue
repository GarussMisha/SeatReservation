/**
 * EditorToolbar - верхняя панель инструментов редактора
 */
<template>
  <div class="editor-toolbar">
    <div class="toolbar-left">
      <button @click="$emit('cancel')" class="btn-back">
        ← Назад
      </button>
      <div class="room-info">
        <h2 class="editor-title">Редактор помещения</h2>
        <span v-if="workspaceCount > 0" class="workspace-count">
          <svg class="workspace-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
          </svg>
          {{ workspaceCount }} {{ declension(workspaceCount, ['рабочее место', 'рабочих места', 'рабочих мест']) }}
        </span>
      </div>
    </div>

    <div class="toolbar-center">
      <div class="history-controls">
        <button
          @click="$emit('undo')"
          :disabled="!canUndo"
          class="toolbar-btn"
          title="Отменить (Ctrl+Z)"
        >
          ↶
        </button>
        <button
          @click="$emit('redo')"
          :disabled="!canRedo"
          class="toolbar-btn"
          title="Повторить (Ctrl+Y)"
        >
          ↷
        </button>
      </div>
    </div>

    <div class="toolbar-right">
      <button @click="handleClear" class="btn-clear" title="Очистить весь план">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
        </svg>
        Очистить
      </button>
      <button @click="handleSave" class="btn-save" :disabled="isSaving">
        <svg class="save-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"/>
        </svg>
        {{ isSaving ? 'Сохранение...' : 'Сохранить' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  canUndo: {
    type: Boolean,
    default: false
  },
  canRedo: {
    type: Boolean,
    default: false
  },
  objects: {
    type: Array,
    default: () => []
  },
  isSaving: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['undo', 'redo', 'save', 'cancel', 'clear'])

// Подсчитываем количество рабочих мест
const workspaceCount = computed(() => {
  return props.objects.filter(obj => obj.object_type === 'workspace').length
})

// Склонение слов
const declension = (number, words) => {
  const cases = [2, 0, 1, 1, 1, 2]
  const index = (number % 100 < 4 || number % 100 > 20) ? cases[number % 10] : 2
  return words[index]
}

// Обработчик сохранения
const handleSave = () => {
  if (workspaceCount.value === 0) {
    const confirmed = confirm('На плане нет рабочих мест. Вы уверены, что хотите сохранить пустой план?')
    if (!confirmed) return
  }
  
  emit('save')
}

// Обработчик очистки
const handleClear = () => {
  if (workspaceCount.value === 0) {
    const confirmed = confirm('Вы уверены, что хотите очистить план помещения? Все объекты будут удалены.')
    if (!confirmed) return
  } else {
    const confirmed = confirm(`Вы уверены, что хотите очистить план помещения? Будет удалено ${workspaceCount.value} ${declension(workspaceCount.value, ['рабочее место', 'рабочих места', 'рабочих мест'])}. Это действие нельзя отменить.`)
    if (!confirmed) return
  }
  
  emit('clear')
}
</script>

<style scoped>
.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 249, 250, 0.98) 100%);
  border-bottom: 1px solid rgba(102, 126, 234, 0.2);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
  z-index: 100;
  backdrop-filter: blur(10px);
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.room-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.workspace-count {
  font-size: 0.9rem;
  color: #667eea;
  font-weight: 500;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  padding: 0.25rem 0.75rem;
  border-radius: 8px;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.btn-back {
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  color: #667eea;
  transition: all 0.3s ease;
}

.btn-back:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
  border-color: rgba(102, 126, 234, 0.5);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}

.editor-title {
  margin: 0;
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.workspace-icon-svg,
.save-icon-svg {
  width: 18px;
  height: 18px;
  vertical-align: middle;
  margin-right: 6px;
}

.toolbar-btn svg {
  width: 20px;
  height: 20px;
}

.btn-clear svg,
.btn-save svg {
  width: 18px;
  height: 18px;
  vertical-align: middle;
  margin-right: 6px;
}

.toolbar-center {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.history-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.toolbar-btn {
  padding: 0.5rem 0.75rem;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.1rem;
  transition: all 0.3s ease;
  color: #667eea;
}

.toolbar-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
  border-color: rgba(102, 126, 234, 0.4);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
  transform: translateY(-1px);
}

.toolbar-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.toolbar-right {
  display: flex;
  gap: 0.5rem;
}

.btn-save {
  padding: 0.5rem 1.5rem;
  background: linear-gradient(135deg, #28a745 0%, #218838 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
}

.btn-save:hover {
  background: linear-gradient(135deg, #34ce57 0%, #28a745 100%);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.4);
  transform: translateY(-2px);
}

.btn-clear {
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(220, 53, 69, 0.3);
}

.btn-clear:hover {
  background: linear-gradient(135deg, #e74a3b 0%, #d32f2f 100%);
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.4);
  transform: translateY(-2px);
}
</style>
