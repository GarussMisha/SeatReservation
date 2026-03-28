<template>
  <div class="admin-panel">
    <Header
      title="Админ-панель"
      :userGreeting="`Добро пожаловать, ${authStore.userName || 'Администратор'}`"
      :actions="headerActions"
      showLogout
      @logout="handleLogout"
    />

    <div class="admin-content">
      <nav class="admin-nav">
        <ul>
          <li :class="{ active: currentView === 'overview' }">
            <button @click="currentView = 'overview'">
              <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
              </svg>
              Обзор
            </button>
          </li>
          <li :class="{ active: currentView === 'users' }">
            <button @click="currentView = 'users'">
              <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/>
              </svg>
              Пользователи
            </button>
          </li>
          <li :class="{ active: currentView === 'rooms' }">
            <button @click="currentView = 'rooms'">
              <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
              </svg>
              Помещения
            </button>
          </li>
          <li :class="{ active: currentView === 'workspaces' }">
            <button @click="currentView = 'workspaces'">
              <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
              </svg>
              Рабочие места
            </button>
          </li>
        </ul>
      </nav>

      <main class="admin-main">
        <!-- Обзор -->
        <div v-if="currentView === 'overview'" class="overview-section">
          <h2>Обзор системы</h2>
          <div class="stats-grid">
            <div class="stat-card">
              <h3>{{ stats.totalUsers }}</h3>
              <p>Пользователей</p>
            </div>
            <div class="stat-card">
              <h3>{{ stats.totalVenues }}</h3>
              <p>Помещений</p>
            </div>
            <div class="stat-card">
              <h3>{{ stats.totalSeats }}</h3>
              <p>Мест</p>
            </div>
            <div class="stat-card">
              <h3>{{ stats.totalEvents }}</h3>
              <p>Событий</p>
            </div>
          </div>
        </div>

        <!-- Управление пользователями -->
        <div v-if="currentView === 'users'" class="users-section">
          <div class="section-header">
            <h2>Управление пользователями</h2>
            <div class="header-buttons">
              <button @click="refreshUsers" class="refresh-btn">
                <svg class="btn-icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                </svg>
                Обновить
              </button>
              <button @click="showUserModal = true" class="add-btn">
                <svg class="btn-icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
                </svg>
                Добавить
              </button>
            </div>
          </div>
          
          <div class="table-container">
            <table class="admin-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Логин</th>
                  <th>Имя сотрудника</th>
                  <th>Email</th>
                  <th>Статус</th>
                  <th>Администратор</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in paginatedUsers" :key="user.id">
                  <td>{{ user.id }}</td>
                  <td>{{ user.login }}</td>
                  <td>{{ getUserName(user) }}</td>
                  <td>{{ user.email }}</td>
                  <td>
                    <span class="badge" :class="getStatusBadgeClass(user.status_name)">
                      {{ user.status_name || 'Неизвестно' }}
                    </span>
                  </td>
                  <td>
                    <span class="badge" :class="user.is_admin ? 'warning' : 'secondary'">
                      {{ user.is_admin ? 'Да' : 'Нет' }}
                    </span>
                  </td>
                  <td>
                    <button @click="editUser(user)" class="action-btn edit" title="Редактировать">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                      </svg>
                    </button>
                    <button @click="showDeleteConfirm('user', user.id, user.login)" class="action-btn delete" title="Удалить">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                      </svg>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
            
            <!-- Пагинация -->
            <div v-if="users.length > pageSize" class="pagination">
              <button 
                @click="currentPageUsers--" 
                :disabled="currentPageUsers === 1"
                class="pagination-btn"
              >
                ← Назад
              </button>
              <span class="pagination-info">
                Страница {{ currentPageUsers }} из {{ Math.ceil(users.length / pageSize) }}
              </span>
              <button 
                @click="currentPageUsers++" 
                :disabled="currentPageUsers === Math.ceil(users.length / pageSize)"
                class="pagination-btn"
              >
                Вперед →
              </button>
            </div>
          </div>
        </div>

        <!-- Управление помещениями -->
        <div v-if="currentView === 'rooms'" class="rooms-section">
          <div class="section-header">
            <h2>Управление помещениями</h2>
            <div class="header-buttons">
              <button @click="refreshRooms" class="refresh-btn">
                <svg class="btn-icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                </svg>
                Обновить
              </button>
              <button @click="showRoomModal = true" class="add-btn">
                <svg class="btn-icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
                </svg>
                Добавить
              </button>
            </div>
          </div>
          
          <div class="table-container">
            <table class="admin-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Название</th>
                  <th>Адрес</th>
                  <th>Описание</th>
                  <th>Рабочих мест</th>
                  <th>Статус</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="room in rooms" :key="room.id">
                  <td>{{ room.id }}</td>
                  <td>{{ room.name }}</td>
                  <td>{{ room.address }}</td>
                  <td>{{ room.description || '-' }}</td>
                  <td>
                    <span class="badge badge-info">{{ getWorkspaceCount(room.id) }}</span>
                  </td>
                  <td>
                    <span class="badge" :class="getStatusBadgeClass(room.status_name)">
                      {{ room.status_name || 'Неизвестно' }}
                    </span>
                  </td>
                  <td>
                    <button @click="openRoomEditor(room)" class="action-btn plan" title="Редактировать план">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/>
                      </svg>
                    </button>
                    <button @click="editRoom(room)" class="action-btn edit" title="Редактировать">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                      </svg>
                    </button>
                    <button @click="showDeleteConfirm('room', room.id, room.name)" class="action-btn delete" title="Удалить">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                      </svg>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Управление рабочими местами -->
        <div v-if="currentView === 'workspaces'" class="workspaces-section">
          <div class="section-header">
            <h2>Управление рабочими местами</h2>
            <div class="header-buttons">
              <button @click="refreshWorkspaces" class="refresh-btn">
                <svg class="btn-icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                </svg>
                Обновить
              </button>
            </div>
          </div>

          <!-- Подсказка что рабочие места создаются через план помещения -->
          <div class="info-banner">
            <svg class="info-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <p class="info-text">
              <strong>Рабочие места создаются через план помещения.</strong>
              Перейдите в редактор помещения и добавьте рабочие места на план.
            </p>
          </div>
          
          <!-- Фильтр по помещениям -->
          <div class="filter-section">
            <label for="roomFilter">Фильтр по помещению:</label>
            <select
              id="roomFilter"
              v-model="roomFilter"
              @change="filterWorkspaces"
            >
              <option value="all">Все помещения</option>
              <option
                v-for="room in rooms"
                :key="room.id"
                :value="room.id"
              >
                {{ room.name }} ({{ room.address }})
              </option>
            </select>
          </div>
          
          <div class="table-container">
            <table class="admin-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Название</th>
                  <th>Помещение</th>
                  <th>Адрес помещения</th>
                  <th>Статус</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="workspace in filteredWorkspaces" :key="workspace.id">
                  <td>{{ workspace.id }}</td>
                  <td>{{ workspace.name }}</td>
                  <td>{{ getRoomName(workspace.room_id) }}</td>
                  <td>{{ getRoomAddress(workspace.room_id) }}</td>
                  <td>
                    <span class="badge" :class="getWorkspaceStatusClass(workspace)">
                      {{ getWorkspaceStatusName(workspace) }}
                    </span>
                  </td>
                  <td>
                    <button @click="editWorkspace(workspace)" class="action-btn edit" title="Редактировать">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                      </svg>
                    </button>
                    <button @click="showDeleteConfirm('workspace', workspace.id, workspace.name)" class="action-btn delete" title="Удалить">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                      </svg>
                    </button>
                  </td>
                </tr>
                <tr v-if="filteredWorkspaces.length === 0">
                  <td colspan="6" style="text-align: center; color: #666; padding: 2rem;">
                    {{ roomFilter === 'all' ? 'Рабочие места не найдены' : 'В выбранном помещении нет рабочих мест' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </main>
    </div>

    <!-- Модальные окна -->
    <RoomModal
      v-if="showRoomModal"
      :room="selectedRoom"
      :statuses="statuses"
      @close="closeRoomModal"
      @save="saveRoom"
    />

    <UserModal
      v-if="showUserModal"
      :user="selectedUser"
      @close="closeUserModal"
      @save="saveUser"
    />

    <!-- Модальное окно подтверждения удаления -->
    <ConfirmModal
      v-if="showConfirmModal"
      :show="showConfirmModal"
      :title="confirmModalData.title"
      :message="confirmModalData.message"
      :confirm-text="confirmModalData.confirmText"
      :cancel-text="confirmModalData.cancelText"
      :confirm-type="confirmModalData.confirmType"
      @confirm="handleConfirmDelete"
      @cancel="closeConfirmModal"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import { accountsAPI, roomsAPI, workspacesAPI, statusesAPI } from '../services/api'
import { useNotificationStore } from '../stores/notifications'
import { getStatusConfig } from '../utils/statusHelpers'

import Header from '../components/Header.vue'
import RoomModal from '../components/admin/RoomModal.vue'
import UserModal from '../components/admin/UserModal.vue'
import ConfirmModal from '../components/ConfirmModal.vue'

const authStore = useAuthStore()
const router = useRouter()
const notificationStore = useNotificationStore()
const accountsApi = accountsAPI
const roomsApi = roomsAPI
const workspacesApi = workspacesAPI
const statusesApi = statusesAPI

const currentView = ref('overview')
const users = ref([])
const rooms = ref([])
const workspaces = ref([])
const statuses = ref([])
const showRoomModal = ref(false)
const showUserModal = ref(false)
const selectedRoom = ref(null)
const selectedUser = ref(null)
const selectedWorkspace = ref(null)
const roomFilter = ref('all')

// Переменные для пагинации
const currentPageUsers = ref(1)
const currentPageRooms = ref(1)
const currentPageWorkspaces = ref(1)
const pageSize = ref(20)

const showConfirmModal = ref(false)
const confirmModalData = ref({
  title: 'Подтверждение действия',
  message: '',
  confirmText: 'Подтвердить',
  cancelText: 'Отмена',
  confirmType: 'danger',
  itemType: '',
  itemId: null,
  itemName: ''
})

// Вычисляемые свойства
const filteredWorkspaces = computed(() => {
  if (roomFilter.value === 'all') {
    return workspaces.value
  }
  return workspaces.value.filter(workspace => workspace.room_id === parseInt(roomFilter.value))
})

// Пагинация для пользователей
const paginatedUsers = computed(() => {
  const start = (currentPageUsers.value - 1) * pageSize.value
  const end = start + pageSize.value
  return users.value.slice(start, end)
})

// Пагинация для помещений
const paginatedRooms = computed(() => {
  const start = (currentPageRooms.value - 1) * pageSize.value
  const end = start + pageSize.value
  return rooms.value.slice(start, end)
})

// Пагинация для рабочих мест
const paginatedWorkspaces = computed(() => {
  const start = (currentPageWorkspaces.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredWorkspaces.value.slice(start, end)
})

// Действия для header
const headerActions = computed(() => [
  {
    key: 'back',
    text: '← Назад к дашборду',
    className: 'back-btn',
    onClick: goToDashboard
  }
])

// Статистика
const stats = computed(() => ({
  totalUsers: users.value.length,
  totalVenues: rooms.value.length,
  totalSeats: workspaces.value.length,
  totalEvents: 0 
}))

// Метод фильтрации
const filterWorkspaces = () => {
  console.log('Фильтр изменен на:', roomFilter.value)
}

const getUserName = (user) => {
  if (!user) return 'Неизвестно'
  const firstName = user.first_name || ''
  const lastName = user.last_name || ''
  return `${lastName} ${firstName}`.trim() || 'Без имени'
}

const getRoomName = (roomId) => {
  const room = rooms.value.find(r => r.id === roomId)
  return room ? room.name : 'Неизвестно'
}

const getRoomAddress = (roomId) => {
  const room = rooms.value.find(r => r.id === roomId)
  return room ? room.address : 'Неизвестно'
}

const getWorkspaceCount = (roomId) => {
  return workspaces.value.filter(w => w.room_id === roomId).length
}

const getStatusBadgeClass = (statusName) => {
  if (!statusName) return 'secondary'
  const config = getStatusConfig(statusName)
  return `badge-${config.class}`
}

// Новые функции для рабочих мест с поддержкой status_id
const getWorkspaceStatusClass = (workspace) => {
  // Если есть status_id, используем его
  if (workspace.status_id) {
    const config = getStatusConfig(workspace.status_name, 'workspace')
    return `badge-${config.class}`
  }
  // Fallback на старый is_active
  return workspace.is_active ? 'badge-success' : 'badge-warning'
}

const getWorkspaceStatusName = (workspace) => {
  // Если есть status_id, используем его
  if (workspace.status_id && workspace.status_name) {
    return getStatusConfig(workspace.status_name, 'workspace').label
  }
  // Fallback на старый is_active
  return workspace.is_active ? 'Активно' : 'Неактивно'
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

const goToDashboard = () => {
  router.push('/dashboard')
}

const refreshUsers = async () => {
  try {
    currentPageUsers.value = 1 // Сброс на первую страницу
    users.value = await accountsApi.getAccounts()
  } catch (error) {
    console.error('Ошибка загрузки пользователей:', error)
    notificationStore.error('Не удалось загрузить список пользователей', 'Ошибка загрузки')
  }
}

const refreshRooms = async () => {
  try {
    currentPageRooms.value = 1 // Сброс на первую страницу
    rooms.value = await roomsApi.getRooms()
  } catch (error) {
    console.error('Ошибка загрузки помещений:', error)
    notificationStore.error('Не удалось загрузить список помещений', 'Ошибка загрузки')
  }
}

const refreshWorkspaces = async () => {
  try {
    currentPageWorkspaces.value = 1 // Сброс на первую страницу
    workspaces.value = await workspacesApi.getWorkspaces()
  } catch (error) {
    console.error('Ошибка загрузки рабочих мест:', error)
    notificationStore.error('Не удалось загрузить список рабочих мест', 'Ошибка загрузки')
  }
}

const loadStatuses = async () => {
  try {
    statuses.value = await statusesApi.getStatuses()
  } catch (error) {
    console.error('Ошибка загрузки статусов:', error)
    // Fallback на значения по умолчанию
    statuses.value = [
      { id: 1, name: 'Активно' },
      { id: 2, name: 'Неактивно' }
    ]
  }
}

const editUser = (user) => {
  selectedUser.value = { ...user }
  showUserModal.value = true
}

const editRoom = (room) => {
  selectedRoom.value = { ...room }
  showRoomModal.value = true
}

const openRoomEditor = (room) => {
  router.push(`/room-editor/${room.id}`)
}

// Показать модальное окно подтверждения удаления
const showDeleteConfirm = (itemType, itemId, itemName) => {
  const types = {
    user: {
      title: 'Удаление пользователя',
      message: `Вы уверены, что хотите удалить пользователя "${itemName}"? Это действие нельзя отменить.`,
      confirmText: 'Удалить',
      confirmType: 'danger'
    },
    room: {
      title: 'Удаление помещения',
      message: `Вы уверены, что хотите удалить помещение "${itemName}"? Это действие нельзя отменить.`,
      confirmText: 'Удалить',
      confirmType: 'danger'
    },
    workspace: {
      title: 'Удаление рабочего места',
      message: `Вы уверены, что хотите удалить рабочее место "${itemName}"? Это действие нельзя отменить.`,
      confirmText: 'Удалить',
      confirmType: 'danger'
    }
  }

  const typeData = types[itemType]
  if (typeData) {
    confirmModalData.value = {
      ...typeData,
      itemType,
      itemId,
      itemName,
      cancelText: 'Отмена'
    }
    showConfirmModal.value = true
  }
}

const closeConfirmModal = () => {
  showConfirmModal.value = false
  confirmModalData.value = {
    title: 'Подтверждение действия',
    message: '',
    confirmText: 'Подтвердить',
    cancelText: 'Отмена',
    confirmType: 'danger',
    itemType: '',
    itemId: null,
    itemName: ''
  }
}

const handleConfirmDelete = async () => {
  const { itemType, itemId } = confirmModalData.value
  
  try {
    switch (itemType) {
      case 'user':
        await accountsApi.deleteAccount(itemId)
        await refreshUsers()
        notificationStore.success('Пользователь успешно удален из системы', 'Удаление выполнено')
        break
      case 'room':
        await roomsApi.deleteRoom(itemId)
        await refreshRooms()
        notificationStore.success('Помещение успешно удалено', 'Удаление выполнено')
        break
      case 'workspace':
        await workspacesApi.deleteWorkspace(itemId)
        await refreshWorkspaces()
        notificationStore.success('Рабочее место успешно удалено', 'Удаление выполнено')
        break
    }
  } catch (error) {
    console.error(`Ошибка удаления ${itemType}:`, error)
    
    let errorMessage = `Ошибка удаления ${itemType === 'user' ? 'пользователя' : itemType === 'room' ? 'помещения' : 'рабочего места'}`
    
    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail
    } else if (error.message) {
      errorMessage = error.message
    }
    
    notificationStore.error(errorMessage, 'Ошибка')
  } finally {
    closeConfirmModal()
  }
}

// Модальные окна
const closeUserModal = () => {
  showUserModal.value = false
  selectedUser.value = null
}

const closeRoomModal = () => {
  showRoomModal.value = false
  selectedRoom.value = null
}

const saveUser = async (userData) => {
  try {
    if (selectedUser.value) {
      await accountsApi.updateAccount(selectedUser.value.id, userData)
    } else {
      await accountsApi.createAccount(userData)
    }
    
    await refreshUsers()
    closeUserModal()
    notificationStore.success('Данные пользователя успешно обновлены', 'Сохранение выполнено')
  } catch (error) {
    console.error('Ошибка сохранения пользователя:', error)
    notificationStore.error('Не удалось сохранить данные пользователя', 'Ошибка сохранения')
  }
}

const saveRoom = async (roomData) => {
  try {
    if (selectedRoom.value) {
      await roomsApi.updateRoom(selectedRoom.value.id, roomData)
    } else {
      await roomsApi.createRoom(roomData)
    }
    
    await refreshRooms()
    closeRoomModal()
    notificationStore.success('Информация о помещении успешно обновлена', 'Сохранение выполнено')
  } catch (error) {
    console.error('Ошибка сохранения помещения:', error)
    notificationStore.error('Не удалось сохранить данные помещения', 'Ошибка сохранения')
  }
}

// Инициализация
onMounted(async () => {
  // Проверяем права администратора
  if (!authStore.isAdmin) {
    notificationStore.warning('Доступ запрещен. Требуются права администратора.', 'Предупреждение')
    router.push('/dashboard')
    return
  }

  // Загружаем все данные
  await Promise.all([
    refreshUsers(),
    refreshRooms(),
    refreshWorkspaces(),
    loadStatuses()
  ])
})
</script>

<style scoped>
.admin-panel {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  padding-top: 100px;
}

.admin-content {
  display: flex;
  gap: 2rem;
  min-height: calc(100vh - 180px);
  position: relative;
  z-index: 10;
  padding: 1rem 1rem 1rem 0;
}

.admin-nav {
  width: 280px;
  flex-shrink: 0;
  align-self: stretch;
  background: var(--bg-white);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-lg);
  border-radius: var(--radius-3xl);
  border: 1px solid rgba(0, 0, 0, 0.1);
  margin: var(--spacing-lg) 0;
}

.admin-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.admin-nav li {
  margin: 0;
}

.admin-nav button {
  width: 100%;
  padding: var(--spacing-lg);
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
  transition: var(--transition-base);
  font-size: var(--font-size-base);
  color: var(--text-muted);
  position: relative;
  overflow: hidden;
  border-radius: var(--radius-lg);
  margin-bottom: var(--spacing-xs);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.nav-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.admin-nav button:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  color: #333;
  transform: translateX(5px);
}

.admin-nav li.active button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  border-radius: 12px;
}

.admin-nav li.active button::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: white;
}

.admin-main {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header-buttons {
  display: flex;
  gap: 1rem;
}

.info-banner {
  padding: 1rem 1.5rem;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  border-left: 4px solid #667eea;
  background-color: #ffffffb6;
  border-radius: 8px;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.info-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.info-text {
  margin: 0;
  font-size: 0.95rem;
  color: #333;
  line-height: 1.6;
}

.info-text strong {
  color: #667eea;
  font-weight: 600;
}

.btn-icon-sm {
  width: 16px;
  height: 16px;
  margin-right: 0.5rem;
  vertical-align: middle;
}

.info-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  color: var(--primary-start);
}

.refresh-btn {
  padding: 0.75rem 1.5rem;
  background: var(--gradient-gray);
  color: var(--text-white);
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: var(--transition-base);
  font-weight: var(--font-weight-medium);
  box-shadow: 0 4px 12px rgba(108, 117, 125, 0.3);
  display: inline-flex;
  align-items: center;
}

.refresh-btn:hover {
  transform: var(--hover-transform);
  box-shadow: 0 6px 20px rgba(108, 117, 125, 0.4);
  background: linear-gradient(135deg, #7c8691 0%, #6c757d 100%);
}

.add-btn {
  padding: 0.75rem 1.5rem;
  background: var(--gradient-success);
  color: var(--text-white);
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: var(--transition-base);
  font-weight: var(--font-weight-medium);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
  display: inline-flex;
  align-items: center;
}

.add-btn:hover {
  transform: var(--hover-transform);
  box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4);
  background: var(--gradient-success-hover);
}


.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  background-color: rgba(255, 255, 255, 0.98);
}

.stat-card h3 {
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  color: #1f2937;
  font-weight: 700;
}

.stat-card p {
  margin: 0;
  color: #6b7280;
  font-size: 1rem;
  font-weight: 500;
}

.table-container {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
}

.admin-table th,
.admin-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid rgba(222, 226, 230, 0.3);
}

.admin-table th {
  background: rgba(248, 249, 250, 0.8);
  font-weight: 600;
  color: #495057;
  backdrop-filter: blur(5px);
}

.admin-table tbody tr:hover {
  background: rgba(248, 249, 250, 0.5);
  backdrop-filter: blur(5px);
}

.badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
}

.badge.success {
  background: rgba(212, 237, 218, 0.8);
  color: #155724;
  backdrop-filter: blur(5px);
}

.badge.danger {
  background: rgba(248, 215, 218, 0.8);
  color: #721c24;
  backdrop-filter: blur(5px);
}

.badge.warning {
  background: rgba(255, 243, 205, 0.8);
  color: #856404;
  backdrop-filter: blur(5px);
}

.badge.secondary {
  background: rgba(226, 227, 229, 0.8);
  color: #383d41;
  backdrop-filter: blur(5px);
}

.badge-info {
  background: rgba(209, 236, 241, 0.8);
  color: #0c5460;
  backdrop-filter: blur(5px);
}

.action-btn {
  padding: 0.5rem 0.75rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  margin-right: 0.5rem;
  font-size: 0.875rem;
  transition: all 0.3s;
  font-weight: 500;
}

.action-btn.edit {
  background: linear-gradient(135deg, #ffc107 0%, #e0a800 100%);
  color: #212529;
  box-shadow: 0 2px 8px rgba(255, 193, 7, 0.3);
}

.action-btn.edit:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 193, 7, 0.4);
}

.action-btn.delete {
  background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(220, 53, 69, 0.3);
}

.action-btn.delete:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.4);
}

.action-btn.plan {
  background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(23, 162, 184, 0.3);
}

.action-btn.plan:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(23, 162, 184, 0.4);
}

.filter-section {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 1.5rem;
  border-radius: 12px;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.filter-section label {
  font-weight: 600;
  color: #495057;
  font-size: 0.95rem;
}

.filter-section select {
  padding: 0.75rem;
  border: 2px solid rgba(222, 226, 230, 0.5);
  border-radius: 8px;
  min-width: 200px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(5px);
  font-size: 0.9rem;
  transition: all 0.3s;
}

.filter-section select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

@media (max-width: 1024px) {
  .admin-content {
    flex-direction: column;
  }

  .admin-nav {
    width: 100%;
    height: auto;
    padding: 2rem 0;
    position: relative;
    transform: none;
    z-index: 100;
    background: rgba(255, 255, 255, 0.98);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    box-shadow: 
      0 25px 50px -12px rgba(0, 0, 0, 0.25),
      0 0 0 1px rgba(255, 255, 255, 0.1);
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  }

  .admin-nav ul {
    display: flex;
    flex-direction: row;
    justify-content: space-around;
    gap: 1rem;
    padding: 0 2rem;
  }

  .admin-nav button {
    padding: 1rem 1.5rem;
    font-size: 0.9rem;
    text-align: center;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .admin-nav button:hover {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
    border-color: rgba(102, 126, 234, 0.3);
  }

  .admin-nav li.active button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    box-shadow: 
      0 8px 25px rgba(102, 126, 234, 0.4),
      0 0 0 1px rgba(255, 255, 255, 0.1);
    transform: translateY(-1px);
  }

  .admin-nav li.active button::before {
    display: none;
  }

  .admin-nav li.active button::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 30px;
    height: 3px;
    background: rgba(255, 255, 255, 0.8);
    border-radius: 2px;
  }


  .admin-main {
    padding: 1rem;
    margin-top: 20px;
  }

  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
  }

  .table-container {
    overflow-x: auto;
  }

  .admin-table {
    min-width: 600px;
  }

  .section-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .header-buttons {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .admin-main {
    padding: 0.5rem;
    margin-top: 20px;
  }

  .stat-card {
    padding: 1rem;
  }

  .stat-card h3 {
    font-size: 1.5rem;
  }

  .filter-section {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }

  .filter-section select {
    min-width: auto;
    width: 100%;
  }

  .admin-table th,
  .admin-table td {
    padding: 0.5rem;
    font-size: 0.875rem;
  }

}

@media (max-width: 480px) {

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .admin-nav ul {
    flex-direction: column;
  }

  .admin-nav button {
    font-size: 0.875rem;
    padding: 0.75rem 1.5rem;
  }
}

/* Пагинация */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  margin-top: 1rem;
  border-top: 1px solid #e0e0e0;
}

.pagination-btn {
  padding: 0.5rem 1rem;
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.pagination-btn:hover:not(:disabled) {
  background: #e8e8e8;
  border-color: #d0d0d0;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  font-size: 0.9rem;
  color: #666;
  font-weight: 500;
}
</style>