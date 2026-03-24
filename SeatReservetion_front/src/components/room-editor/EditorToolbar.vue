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
      <div class="zoom-controls">
        <button @click="$emit('zoom-out')" class="toolbar-btn" title="Уменьшить">
          🔍-
        </button>
        <span class="zoom-level">{{ Math.round(zoom * 100) }}%</span>
        <button @click="$emit('zoom-in')" class="toolbar-btn" title="Увеличить">
          🔍+
        </button>
      </div>

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
      <button @click="$emit('save')" class="btn-save">
        💾 Сохранить
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  zoom: {
    type: Number,
    default: 1
  },
  canUndo: {
    type: Boolean,
    default: false
  },
  canRedo: {
    type: Boolean,
    default: false
  }
})

defineEmits(['zoom-in', 'zoom-out', 'undo', 'redo', 'save', 'cancel'])
</script>

<style scoped>
.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1.5rem;
  background: #ffffff;
  border-bottom: 1px solid #e0e0e0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  z-index: 100;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-back {
  padding: 0.5rem 1rem;
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.btn-back:hover {
  background: #e8e8e8;
}

.editor-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #333;
}

.toolbar-center {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.zoom-controls,
.history-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.toolbar-btn {
  padding: 0.5rem 0.75rem;
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.toolbar-btn:hover:not(:disabled) {
  background: #e8e8e8;
}

.toolbar-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.zoom-level {
  min-width: 50px;
  text-align: center;
  font-size: 0.9rem;
  font-weight: 500;
  color: #666;
}

.toolbar-right {
  display: flex;
  gap: 0.5rem;
}

.btn-save {
  padding: 0.5rem 1.5rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-save:hover {
  background: #45a049;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
}
</style>
