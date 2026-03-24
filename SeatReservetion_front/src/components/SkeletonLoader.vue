/**
 * SkeletonLoader - компонент для отображения скелетона во время загрузки
 * Используется для улучшения UX, показывая пользователю анимацию загрузки
 */
<template>
  <div :class="['skeleton-wrapper', variant]">
    <!-- Текстовый скелетон -->
    <template v-if="variant === 'text'">
      <div
        v-for="i in count"
        :key="i"
        :class="['skeleton', 'skeleton-text', { animated }]"
        :style="{ width: getWidth(i), height: height }"
      ></div>
    </template>

    <!-- Карточка скелетон -->
    <template v-else-if="variant === 'card'">
      <div :class="['skeleton-card', { animated }]">
        <div
          v-if="showImage"
          :class="['skeleton', 'skeleton-image']"
          :style="{ height: imageHeight }"
        ></div>
        <div class="skeleton-card-content">
          <div
            :class="['skeleton', 'skeleton-title']"
            :style="{ width: titleWidth, height }"
          ></div>
          <div
            v-for="i in lines"
            :key="i"
            :class="['skeleton', 'skeleton-text']"
            :style="{ width: getLineWidth(i), height }"
          ></div>
        </div>
      </div>
    </template>

    <!-- Таблица скелетон -->
    <template v-else-if="variant === 'table'">
      <div :class="['skeleton-table', { animated }]">
        <div v-for="i in rows" :key="i" class="skeleton-table-row">
          <div
            v-for="col in columns"
            :key="col"
            :class="['skeleton', 'skeleton-cell']"
            :style="{ width: getColumnWidth(col), height }"
          ></div>
        </div>
      </div>
    </template>

    <!-- Круглый аватар скелетон -->
    <template v-else-if="variant === 'avatar'">
      <div
        :class="['skeleton', 'skeleton-avatar', { animated }]"
        :style="{ width: size, height: size }"
      ></div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'text',
    validator: (value) => ['text', 'card', 'table', 'avatar'].includes(value)
  },
  count: {
    type: Number,
    default: 3
  },
  lines: {
    type: Number,
    default: 2
  },
  rows: {
    type: Number,
    default: 5
  },
  columns: {
    type: Number,
    default: 4
  },
  height: {
    type: String,
    default: '1rem'
  },
  size: {
    type: String,
    default: '3rem'
  },
  imageHeight: {
    type: String,
    default: '12rem'
  },
  titleWidth: {
    type: String,
    default: '60%'
  },
  showImage: {
    type: Boolean,
    default: true
  },
  animated: {
    type: Boolean,
    default: true
  }
})

const getWidth = (index) => {
  if (index === props.count) return '70%'
  return '100%'
}

const getLineWidth = (index) => {
  if (index === props.lines) return '50%'
  return '100%'
}

const getColumnWidth = (index) => {
  if (index === 1) return '150px'
  return '100px'
}
</script>

<style scoped>
.skeleton-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.skeleton {
  background: #e5e7eb;
  border-radius: 0.25rem;
}

.skeleton.animated {
  background: linear-gradient(
    90deg,
    #e5e7eb 0%,
    #f3f4f6 50%,
    #e5e7eb 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* Text variant */
.skeleton-text {
  margin-bottom: 0.5rem;
}

.skeleton-text:last-child {
  margin-bottom: 0;
}

/* Card variant */
.skeleton-card {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.skeleton-card.animated {
  background: linear-gradient(
    90deg,
    #f9fafb 0%,
    #f3f4f6 50%,
    #f9fafb 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skeleton-image {
  width: 100%;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.skeleton-card-content {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.skeleton-title {
  background: #d1d5db;
  border-radius: 0.25rem;
}

/* Table variant */
.skeleton-table {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.skeleton-table-row {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.skeleton-cell {
  height: 2rem;
  border-radius: 0.25rem;
}

.skeleton-cell:first-child {
  background: #d1d5db;
}

/* Avatar variant */
.skeleton-avatar {
  border-radius: 50%;
}
</style>
