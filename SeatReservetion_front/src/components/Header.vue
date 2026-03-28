/**
 * Header - шапка приложения с заголовком страницы, кнопками действий и профилем пользователя.
 */
<template>
  <header class="app-header">
    <div class="header-content">
      <div class="header-left">
        <h1 class="header-title">{{ title }}</h1>
      </div>

      <div class="header-right">
        <!-- Кнопка админки (только для админов) -->
        <button
          v-if="authStore.isAdmin"
          @click="goToAdmin"
          class="header-action-btn admin-btn"
        >
          <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
          Админка
        </button>

        <div v-if="hasActions" class="header-actions">
          <button
            v-for="action in actions"
            :key="action.key"
            :class="['header-action-btn', action.className]"
            @click="action.onClick"
          >
            <svg v-if="action.icon === 'settings'" class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
            {{ action.text }}
          </button>
        </div>

        <!-- Уведомления (колокольчик) -->
        <NotificationsDropdown />

        <div class="user-section">
          <div v-if="authStore.user" class="user-avatar"
               :title="`${authStore.user.first_name || ''} ${authStore.user.last_name || ''}`.trim()"
               @click="goToProfile">
            {{ getInitials() }}
          </div>

          <button v-if="showLogout" @click="handleLogout" class="logout-btn">
            Выйти
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import NotificationsDropdown from './NotificationsDropdown.vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  userGreeting: {
    type: String,
    default: ''
  },
  actions: {
    type: Array,
    default: () => []
  },
  showLogout: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['logout'])

const authStore = useAuthStore()
const router = useRouter()

const hasActions = computed(() => {
  return props.actions && props.actions.length > 0
})

const getInitials = () => {
  if (!authStore.user) return 'U'
  const firstName = authStore.user.first_name || ''
  const lastName = authStore.user.last_name || ''
  return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase() || 'U'
}

const goToProfile = () => {
  router.push('/profile')
}

const goToAdmin = () => {
  router.push('/admin')
}

const handleLogout = () => {
  if (emit('logout')) {
    emit('logout')
  } else {
    authStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: var(--z-sticky);
  padding: var(--spacing-lg) 20px 0 20px;
  background: transparent;
  min-height: 80px;
  border-bottom: none;
}

.header-content {
  background: rgba(255, 255, 255, 0.15);
  padding: 1.2rem 2rem;
  box-shadow: var(--shadow-lg);
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: var(--radius-lg);
  max-width: 1400px;
  margin: 0 auto;
  backdrop-filter: var(--backdrop-filter);
  border: 1px solid rgba(129, 119, 119, 0.2);
  position: relative;
  z-index: 1;
}

.header-left {
  flex: 1;
}

.header-title {
  margin: 0;
  color: var(--text-white);
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  position: relative;
  z-index: 2;
}

/* Уведомления */
.notifications-dropdown-wrapper {
  display: flex;
  align-items: center;
}

.user-section {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-full);
  background: var(--primary-gradient);
  color: var(--text-white);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  box-shadow: var(--shadow-primary);
  transition: var(--transition-base);
  cursor: pointer;
}

.user-avatar:hover {
  transform: var(--hover-transform);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.header-actions {
  display: flex;
  gap: var(--spacing-lg);
  align-items: center;
  position: relative;
  z-index: 3;
}

.btn-icon {
  width: 18px;
  height: 18px;
  margin-right: 0.5rem;
  vertical-align: middle;
}

.header-action-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: var(--transition-base);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  box-shadow: var(--shadow-md);
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  position: relative;
  z-index: 4;
}

.header-action-btn.back-btn {
  background: var(--gradient-blue);
  color: var(--text-white);
}

.header-action-btn.back-btn:hover {
  background: var(--gradient-blue-hover);
  transform: var(--hover-transform);
  box-shadow: 0 8px 25px rgba(52, 152, 219, 0.4);
}

.header-action-btn.toggle-btn {
  background: var(--gradient-green);
  color: var(--text-white);
}

.header-action-btn.toggle-btn:hover {
  background: var(--gradient-green-hover);
  transform: var(--hover-transform);
  box-shadow: 0 8px 25px rgba(39, 174, 96, 0.4);
}

.header-action-btn.admin-btn {
  background: var(--gradient-purple);
  color: var(--text-white);
}

.header-action-btn.admin-btn:hover {
  background: var(--gradient-purple-hover);
  transform: var(--hover-transform);
  box-shadow: 0 8px 25px rgba(155, 89, 182, 0.4);
}

.logout-btn {
  padding: 0.5rem 1rem;
  background: var(--gradient-danger);
  color: var(--text-white);
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: var(--transition-base);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
}

.logout-btn:hover {
  background: var(--gradient-danger-hover);
  transform: var(--hover-transform);
  box-shadow: 0 8px 25px rgba(231, 76, 60, 0.4);
}

/* Адаптивность */
@media (max-width: 768px) {
  .app-header {
    padding: var(--spacing-sm) 10px 0 10px;
    min-height: 70px;
  }

  .header-content {
    padding: var(--spacing-lg);
    flex-direction: column;
    gap: var(--spacing-lg);
    text-align: center;
    border-radius: var(--radius-lg);
  }

  .header-right {
    flex-direction: column;
    gap: var(--spacing-lg);
    width: 100%;
  }

  .header-actions {
    flex-direction: column;
    width: 100%;
  }

  .header-action-btn {
    width: 100%;
    justify-content: center;
  }

  .user-section {
    flex-direction: column;
    gap: var(--spacing-xs);
  }

  .header-title {
    font-size: var(--font-size-xl);
  }
}

@media (max-width: 480px) {
  .app-header {
    padding: 0.6rem 8px 0 8px;
    min-height: 60px;
  }

  .header-content {
    padding: 0.8rem;
    border-radius: var(--radius-sm);
  }

  .header-title {
    font-size: var(--font-size-lg);
  }

  .user-greeting {
    font-size: var(--font-size-sm);
  }

  .header-action-btn,
  .logout-btn {
    padding: 0.6rem 1rem;
    font-size: var(--font-size-sm);
  }
  
  .btn-icon {
    width: 16px;
    height: 16px;
  }
}
</style>
