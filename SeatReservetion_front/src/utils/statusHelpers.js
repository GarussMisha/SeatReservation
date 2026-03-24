/**
 * Utility для работы со статусами
 * Предоставляет конфигурацию статусов и вспомогательные функции
 */

/**
 * Конфигурация статусов для различных сущностей
 */
export const statusConfig = {
  // Статусы пользователей (Account)
  account: {
    active: { label: 'Активный', class: 'success', color: '#22c55e' },
    inactive: { label: 'Неактивный', class: 'secondary', color: '#6b7280' },
    blocked: { label: 'Заблокированный', class: 'danger', color: '#ef4444' },
    on_leave: { label: 'В отпуске', class: 'warning', color: '#f59e0b' },
    sick: { label: 'На больничном', class: 'info', color: '#3b82f6' },
    terminated: { label: 'Уволенный', class: 'danger', color: '#dc2626' }
  },

  // Статусы помещений (Room)
  room: {
    available: { label: 'Доступно', class: 'success', color: '#22c55e' },
    maintenance: { label: 'На обслуживании', class: 'warning', color: '#f59e0b' },
    unavailable: { label: 'Недоступно', class: 'danger', color: '#ef4444' }
  },

  // Статусы рабочих мест (Workspace)
  workspace: {
    free: { label: 'Свободно', class: 'success', color: '#22c55e' },
    occupied: { label: 'Занято', class: 'info', color: '#3b82f6' },
    inactive: { label: 'Не активно', class: 'secondary', color: '#6b7280' }
  },

  // Статусы бронирований (Booking)
  booking: {
    pending: { label: 'Ожидает подтверждения', class: 'warning', color: '#f59e0b' },
    confirmed: { label: 'Подтверждено', class: 'success', color: '#22c55e' },
    cancelled: { label: 'Отменено', class: 'danger', color: '#ef4444' },
    completed: { label: 'Завершено', class: 'secondary', color: '#6b7280' }
  },

  // Статусы уведомлений (Notification)
  notification: {
    pending: { label: 'Ожидает отправки', class: 'warning', color: '#f59e0b' },
    sent: { label: 'Отправлено', class: 'success', color: '#22c55e' },
    failed: { label: 'Ошибка отправки', class: 'danger', color: '#ef4444' },
    cancelled: { label: 'Отменено', class: 'secondary', color: '#6b7280' }
  }
}

/**
 * Получить отображаемое имя статуса
 * @param {string} statusName - Название статуса
 * @param {string} entityType - Тип сущности (account, room, workspace, booking, notification)
 * @returns {string} Отображаемое имя статуса или статус по умолчанию
 */
export function getStatusDisplayName(statusName, entityType = null) {
  if (!statusName) return 'Неизвестно'

  // Если указан тип сущности, ищем в соответствующей конфигурации
  if (entityType && statusConfig[entityType]) {
    const config = statusConfig[entityType][statusName.toLowerCase()]
    return config?.label || statusName
  }

  // Ищем во всех конфигурациях
  for (const entityConfig of Object.values(statusConfig)) {
    const config = entityConfig[statusName.toLowerCase()]
    if (config) {
      return config.label
    }
  }

  // Возвращаем исходное название если не найдено
  return statusName
}

/**
 * Получить CSS класс для статуса
 * @param {string} statusName - Название статуса
 * @param {string} entityType - Тип сущности
 * @returns {string} CSS класс
 */
export function getStatusClass(statusName, entityType = null) {
  if (!statusName) return 'default'

  // Если указан тип сущности, ищем в соответствующей конфигурации
  if (entityType && statusConfig[entityType]) {
    const config = statusConfig[entityType][statusName.toLowerCase()]
    return config?.class || 'default'
  }

  // Ищем во всех конфигурациях
  for (const entityConfig of Object.values(statusConfig)) {
    const config = entityConfig[statusName.toLowerCase()]
    if (config) {
      return config.class
    }
  }

  return 'default'
}

/**
 * Получить цвет для статуса
 * @param {string} statusName - Название статуса
 * @param {string} entityType - Тип сущности
 * @returns {string} HEX цвет
 */
export function getStatusColor(statusName, entityType = null) {
  if (!statusName) return '#6b7280'

  // Если указан тип сущности, ищем в соответствующей конфигурации
  if (entityType && statusConfig[entityType]) {
    const config = statusConfig[entityType][statusName.toLowerCase()]
    return config?.color || '#6b7280'
  }

  // Ищем во всех конфигурациях
  for (const entityConfig of Object.values(statusConfig)) {
    const config = entityConfig[statusName.toLowerCase()]
    if (config) {
      return config.color
    }
  }

  return '#6b7280'
}

/**
 * Получить полную конфигурацию статуса
 * @param {string} statusName - Название статуса
 * @param {string} entityType - Тип сущности
 * @returns {Object} Конфигурация статуса
 */
export function getStatusConfig(statusName, entityType = null) {
  const defaultConfig = {
    label: statusName || 'Неизвестно',
    class: 'default',
    color: '#6b7280'
  }

  if (!statusName) return defaultConfig

  // Если указан тип сущности, ищем в соответствующей конфигурации
  if (entityType && statusConfig[entityType]) {
    return statusConfig[entityType][statusName.toLowerCase()] || defaultConfig
  }

  // Ищем во всех конфигурациях
  for (const entityConfig of Object.values(statusConfig)) {
    const config = entityConfig[statusName.toLowerCase()]
    if (config) {
      return config
    }
  }

  return defaultConfig
}

/**
 * Проверить является ли статус активным
 * @param {string} statusName - Название статуса
 * @param {string} entityType - Тип сущности
 * @returns {boolean} true если статус активный
 */
export function isActiveStatus(statusName, entityType = null) {
  const config = getStatusConfig(statusName, entityType)
  return config.class === 'success'
}

/**
 * Проверить является ли статус неактивным/отключенным
 * @param {string} statusName - Название статуса
 * @param {string} entityType - Тип сущности
 * @returns {boolean} true если статус неактивный
 */
export function isInactiveStatus(statusName, entityType = null) {
  const config = getStatusConfig(statusName, entityType)
  return config.class === 'secondary' || config.class === 'danger'
}

// Экспорт по умолчанию
export default {
  statusConfig,
  getStatusDisplayName,
  getStatusClass,
  getStatusColor,
  getStatusConfig,
  isActiveStatus,
  isInactiveStatus
}
