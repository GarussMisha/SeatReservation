/**
 * EditorToolbar - верхняя панель инструментов редактора
 */
<template>
  <div class="editor-toolbar">
    <div class="toolbar-left">
      <button @click="$emit('cancel')" class="btn-back">
        ← Назад
      </button>
      <h2 class="editor-title">Редактор помещения</h2>
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
      <button @click="$emit('clear')" class="btn-clear" title="Очистить весь план">
        🗑️ Очистить
      </button>
      <button @click="$emit('save')" class="btn-save">
        💾 Сохранить
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  canUndo: {
    type: Boolean,
    default: false
  },
  canRedo: {
    type: Boolean,
    default: false
  }
})

defineEmits(['undo', 'redo', 'save', 'cancel', 'clear'])
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
  font-size: 1.25rem;
  font-weight: 700;
  color: #1f2937;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
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
