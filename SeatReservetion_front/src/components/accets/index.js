/**
 * SVG иконки для редактора помещений
 * Нормализованы к viewBox="0 0 100 100"
 * Основаны на файлах из папки accets
 */

// Конференц-зал / Переговорная
export const conferenceRoom = `
  <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <path d="M35 25 L35 35 L25 35 L25 45 L35 45 L35 55 L25 55 L25 65 L35 65 L35 75 L45 75 L45 65 L55 65 L55 75 L65 75 L65 65 L75 65 L75 55 L65 55 L65 45 L75 45 L75 35 L65 35 L65 25 L55 25 L55 35 L45 35 L45 25 Z M40 40 L60 40 L60 60 L40 60 Z" fill="currentColor"/>
  </svg>
`

// Вешалка / Гардероб
export const hanger = `
  <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <path d="M50 15 L60 25 L85 25 L85 35 L65 35 L65 85 L55 85 L55 35 L45 35 L45 85 L35 85 L35 35 L15 35 L15 25 L40 25 Z" fill="currentColor"/>
  </svg>
`

// Кухня
export const kitchen = `
  <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <rect x="15" y="20" width="20" height="60" fill="currentColor"/>
    <rect x="40" y="20" width="20" height="60" fill="currentColor"/>
    <rect x="65" y="20" width="20" height="60" fill="currentColor"/>
  </svg>
`

// Лестница
export const ladder = `
  <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <rect x="20" y="15" width="15" height="70" fill="currentColor"/>
    <rect x="65" y="15" width="15" height="70" fill="currentColor"/>
    <rect x="20" y="25" width="60" height="8" fill="currentColor"/>
    <rect x="20" y="40" width="60" height="8" fill="currentColor"/>
    <rect x="20" y="55" width="60" height="8" fill="currentColor"/>
    <rect x="20" y="70" width="60" height="8" fill="currentColor"/>
  </svg>
`

// Туалет мужской
export const toiletMan = `
  <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <circle cx="50" cy="20" r="12" fill="currentColor"/>
    <rect x="35" y="35" width="30" height="35" rx="5" fill="currentColor"/>
    <line x1="50" y1="70" x2="50" y2="90" stroke="currentColor" stroke-width="8"/>
    <line x1="35" y1="55" x2="20" y2="65" stroke="currentColor" stroke-width="6"/>
    <line x1="65" y1="55" x2="80" y2="65" stroke="currentColor" stroke-width="6"/>
  </svg>
`

// Туалет женский
export const toiletWoman = `
  <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <circle cx="50" cy="18" r="12" fill="currentColor"/>
    <path d="M50 32 L50 55 L35 75 L35 90 L45 90 L45 75 L50 65 L55 75 L55 90 L65 90 L65 75 L50 55 Z" fill="currentColor"/>
    <path d="M30 40 L20 55 M70 40 L80 55" stroke="currentColor" stroke-width="6" stroke-linecap="round"/>
  </svg>
`

// Стрелка
export const arrow = `
  <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <line x1="10" y1="50" x2="70" y2="50" stroke="currentColor" stroke-width="8" stroke-linecap="round"/>
    <polyline points="55,35 75,50 55,65" fill="none" stroke="currentColor" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
`

// Текст (иконка документа)
export const text = `
  <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <rect x="20" y="15" width="60" height="70" rx="5" fill="none" stroke="currentColor" stroke-width="6"/>
    <line x1="30" y1="35" x2="70" y2="35" stroke="currentColor" stroke-width="4"/>
    <line x1="30" y1="50" x2="70" y2="50" stroke="currentColor" stroke-width="4"/>
    <line x1="30" y1="65" x2="60" y2="65" stroke="currentColor" stroke-width="4"/>
  </svg>
`

// Экспорт всех иконок
export const icons = {
  conferenceRoom,
  hanger,
  kitchen,
  ladder,
  toiletMan,
  toiletWoman,
  arrow,
  text
}

// Функция для получения SVG строки по типу объекта
export const getIconSvg = (type) => {
  const iconMap = {
    'meeting_room': conferenceRoom,
    'hanger': hanger,
    'kitchen': kitchen,
    'staircase': ladder,
    'ladder': ladder,
    'toilet_man': toiletMan,
    'toilet_woman': toiletWoman,
    'restroom': toiletMan,
    'arrow': arrow,
    'text': text
  }
  return iconMap[type] || null
}
