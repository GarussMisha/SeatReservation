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
        <div v-if="hasActions" class="header-actions">
          <button
            v-for="action in actions"
            :key="action.key"
            :class="['header-action-btn', action.className]"
            @click="action.onClick"
          >
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
  z-index: 1000;
  padding: 1rem 20px 0 20px;
  background: transparent;
  min-height: 80px;
  border-bottom: none;
}

.header-content {
  background: rgba(255, 255, 255, 0.15);
  padding: 1.2rem 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 12px;
  max-width: 1400px;
  margin: 0 auto;
  backdrop-filter: blur(20px) saturate(1.8);
  border: 1px solid rgba(129, 119, 119, 0.2);
  background: linear-gradient(135deg,
    rgba(179, 49, 157, 0.2) 0%,
    rgba(154, 3, 214, 0.1) 100%);
}

.header-left {
  flex: 1;
}

.header-title {
  margin: 0;
  color: #ffffff;
  font-size: 1.5rem;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

/* Уведомления */
.notifications-dropdown-wrapper {
  display: flex;
  align-items: center;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
  cursor: pointer;
}

.user-avatar:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.header-action-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  white-space: nowrap;
}

.header-action-btn.back-btn {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: white;
}

.header-action-btn.back-btn:hover {
  background: linear-gradient(135deg, #5dade2 0%, #3498db 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(52, 152, 219, 0.4);
}

.header-action-btn.toggle-btn {
  background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
  color: white;
}

.header-action-btn.toggle-btn:hover {
  background: linear-gradient(135deg, #58d68d 0%, #27ae60 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(39, 174, 96, 0.4);
}

.logout-btn {
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
}

.logout-btn:hover {
  background: linear-gradient(135deg, #ec7063 0%, #e74c3c 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(231, 76, 60, 0.4);
}

/* Адаптивность */
@media (max-width: 768px) {
  .app-header {
    padding: 0.8rem 10px 0 10px;
    min-height: 70px;
  }
  
  .header-content {
    padding: 1rem;
    flex-direction: column;
    gap: 1rem;
    text-align: center;
    border-radius: 12px;
  }
  
  .header-right {
    flex-direction: column;
    gap: 1rem;
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
    gap: 0.5rem;
  }
  
  .header-title {
    font-size: 1.2rem;
  }
}

@media (max-width: 480px) {
  .app-header {
    padding: 0.6rem 8px 0 8px;
    min-height: 60px;
  }
  
  .header-content {
    padding: 0.8rem;
    border-radius: 8px;
  }
  
  .header-title {
    font-size: 1rem;
  }
  
  .user-greeting {
    font-size: 0.85rem;
  }
  
  .header-action-btn,
  .logout-btn {
    padding: 0.6rem 1rem;
    font-size: 0.8rem;
  }
}
</style>
