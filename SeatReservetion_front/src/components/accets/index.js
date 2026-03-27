/**
 * SVG иконки для редактора помещений
 * Импорт оригинальных SVG файлов из папки accets
 * Все иконки приводятся к viewBox="0 0 100 100"
 */

// Импорт SVG файлов как строк
import conferenceRoomSvg from './conference-room.svg?raw'
import hangerSvg from './hanger.svg?raw'
import kitchenSvg from './kitchen-pack-knife.svg?raw'
import ladderSvg from './ladder.svg?raw'
import toiletManSvg from './toilet_man.svg?raw'
import toiletWomanSvg from './toilet_woman.svg?raw'

// Функция для нормализации SVG к viewBox="0 0 100 100"
const normalizeSvg = (svgString) => {
  // Заменяем viewBox на 0 0 100 100 и экранируем закрывающие теги
  return svgString
    .replace(/viewBox="[^"]*"/, 'viewBox="0 0 100 100"')
    .replace(/width="[^"]*"/, 'width="100"')
    .replace(/height="[^"]*"/, 'height="100"')
    .replace(/<\/svg>/g, '<\\/svg>') // Экранируем закрывающий тег
}

// Нормализованные SVG
export const conferenceRoom = normalizeSvg(conferenceRoomSvg)
export const hanger = normalizeSvg(hangerSvg)
export const kitchen = normalizeSvg(kitchenSvg)
export const ladder = normalizeSvg(ladderSvg)
export const toiletMan = normalizeSvg(toiletManSvg)
export const toiletWoman = normalizeSvg(toiletWomanSvg)

// Стрелка и текст - простые SVG (с экранированием)
export const arrow = `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><line x1="10" y1="50" x2="70" y2="50" stroke="currentColor" stroke-width="8" stroke-linecap="round"/><polyline points="55,35 75,50 55,65" fill="none" stroke="currentColor" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/><\/svg>`

export const text = `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><rect x="20" y="15" width="60" height="70" rx="5" fill="none" stroke="currentColor" stroke-width="6"/><line x1="30" y1="35" x2="70" y2="35" stroke="currentColor" stroke-width="4"/><line x1="30" y1="50" x2="70" y2="50" stroke="currentColor" stroke-width="4"/><line x1="30" y1="65" x2="60" y2="65" stroke="currentColor" stroke-width="4"/><\/svg>`

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
