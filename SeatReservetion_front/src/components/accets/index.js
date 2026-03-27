/**
 * SVG иконки для редактора помещений
 * Импорт как URL изображений (не raw строки!)
 */

// Импорт SVG файлов как URL
import conferenceRoomUrl from './conference-room.svg'
import hangerUrl from './hanger.svg'
import kitchenUrl from './kitchen-pack-knife.svg'
import ladderUrl from './ladder.svg'
import toiletManUrl from './toilet_man.svg'
import toiletWomanUrl from './toilet_woman.svg'

// Экспорт URL иконок
export const icons = {
  conferenceRoom: conferenceRoomUrl,
  hanger: hangerUrl,
  kitchen: kitchenUrl,
  ladder: ladderUrl,
  toiletMan: toiletManUrl,
  toiletWoman: toiletWomanUrl
}

// Функция для получения URL иконки по типу объекта
export const getIconUrl = (type) => {
  const iconMap = {
    'meeting_room': conferenceRoomUrl,
    'hanger': hangerUrl,
    'kitchen': kitchenUrl,
    'staircase': ladderUrl,
    'ladder': ladderUrl,
    'toilet_man': toiletManUrl,
    'toilet_woman': toiletWomanUrl,
    'restroom': hangerUrl,
    'toilet_female': toiletWomanUrl,
    'toilet_male': toiletManUrl
  }
  return iconMap[type] || null
}
