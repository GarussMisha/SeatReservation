/**
 * Utility функции для debounce и throttle
 * Помогают оптимизировать часто вызываемые функции
 */

/**
 * Debounce - откладывает вызов функции до тех пор,
 * пока не пройдет заданное время с последнего вызова
 *
 * @param {Function} func - Функция для debounce
 * @param {number} wait - Время ожидания в миллисекундах
 * @param {boolean} immediate - Вызывать немедленно при первом вызове
 * @returns {Function} Debounced функция
 */
export function debounce(func, wait, immediate = false) {
  let timeout

  return function executedFunction(...args) {
    const context = this

    const later = () => {
      timeout = null
      if (!immediate) {
        func.apply(context, args)
      }
    }

    const callNow = immediate && !timeout
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)

    if (callNow) {
      func.apply(context, args)
    }
  }
}

/**
 * Throttle - ограничивает вызов функции до одного раза
 * в заданный промежуток времени
 *
 * @param {Function} func - Функция для throttle
 * @param {number} limit - Ограничение в миллисекундах
 * @returns {Function} Throttled функция
 */
export function throttle(func, limit) {
  let inThrottle
  let lastResult

  return function(...args) {
    const context = this

    if (!inThrottle) {
      lastResult = func.apply(context, args)
      inThrottle = true
      setTimeout(() => {
        inThrottle = false
      }, limit)
    }

    return lastResult
  }
}

/**
 * Создает debounced функцию для поиска
 * Специализированная версия для search input
 *
 * @param {Function} searchFunction - Функция поиска
 * @param {number} delay - Задержка в миллисекундах (по умолчанию 300)
 * @returns {Function} Debounced функция поиска
 */
export function createSearchDebounce(searchFunction, delay = 300) {
  return debounce((searchTerm) => {
    if (searchTerm && searchTerm.trim().length > 0) {
      searchFunction(searchTerm.trim())
    } else {
      searchFunction('')
    }
  }, delay)
}

// Экспорт по умолчанию
export default {
  debounce,
  throttle,
  createSearchDebounce
}
