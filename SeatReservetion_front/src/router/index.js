import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('../views/Dashboard.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/profile',
      name: 'Profile',
      component: () => import('../views/Profile.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/profile/notifications',
      name: 'NotificationSettings',
      component: () => import('../views/NotificationSettings.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin',
      name: 'AdminPanel',
      component: () => import('../views/AdminPanel.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/room-editor/:roomId',
      name: 'RoomEditor',
      component: () => import('../components/room-editor/RoomEditor.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/notifications',
      name: 'Notifications',
      component: () => import('../views/Notifications.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('../views/NotFound.vue')
    }
  ],
})

// Навигационные гварды
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Проверяем аутентификацию для защищенных маршрутов
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // Если не авторизован, проверяем токен в localStorage
    if (!authStore.isAuthenticated) {
      await authStore.checkAuth()
    }
    
    if (!authStore.isAuthenticated) {
      next('/login')
      return
    }
  }

  // Проверяем права администратора для админских маршрутов
  if (to.matched.some(record => record.meta.requiresAdmin)) {
    if (!authStore.isAdmin) {
      // Проверяем пользователя для получения актуальных данных
      if (authStore.user && !authStore.user.is_admin) {
        next('/dashboard')
        return
      }
      // Если данные пользователя устарели, обновляем их
      if (!authStore.user) {
        await authStore.refreshUserData()
        if (!authStore.isAdmin) {
          next('/dashboard')
          return
        }
      }
    }
  }

  // Проверяем, требуется ли гостевая страница (только для неавторизованных)
  if (to.matched.some(record => record.meta.requiresGuest)) {
    // Если не авторизован, проверяем токен в localStorage
    if (!authStore.isAuthenticated) {
      await authStore.checkAuth()
    }
    
    if (authStore.isAuthenticated) {
      next('/dashboard')
      return
    }
  }

  next()
})

export default router
