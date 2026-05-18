import { ref, computed } from 'vue'
import { CALENDAR_CONFIG } from '@/config/constants'

export interface DayData {
  date: Date
  tasks: any[]
  workHours: number
}

export function useCalendarGrid() {
  const currentDate = ref(new Date())

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ]

  const dayNames = [
    { short: 'Пн', full: 'monday' },
    { short: 'Вт', full: 'tuesday' },
    { short: 'Ср', full: 'wednesday' },
    { short: 'Чт', full: 'thursday' },
    { short: 'Пт', full: 'friday' },
    { short: 'Сб', full: 'saturday' },
    { short: 'Вс', full: 'sunday' },
  ]

  const monthYear = computed(() => {
    const month = monthNames[currentDate.value.getMonth()]
    const year = currentDate.value.getFullYear()
    return `${month} ${year}`
  })

  function prevMonth() {
    currentDate.value = new Date(
      currentDate.value.getFullYear(),
      currentDate.value.getMonth() - 1,
      1
    )
  }

  function nextMonth() {
    currentDate.value = new Date(
      currentDate.value.getFullYear(),
      currentDate.value.getMonth() + 1,
      1
    )
  }

  function goToday() {
    currentDate.value = new Date()
  }

  function isToday(date: Date): boolean {
    const today = new Date()
    return (
      date.getDate() === today.getDate() &&
      date.getMonth() === today.getMonth() &&
      date.getFullYear() === today.getFullYear()
    )
  }

  const monthData = computed<DayData[]>(() => {
    const year = currentDate.value.getFullYear()
    const month = currentDate.value.getMonth()

    const firstDay = new Date(year, month, 1)
    const lastDay = new Date(year, month + 1, 0)

    let firstDayOffset = firstDay.getDay() - 1
    if (firstDayOffset < 0) firstDayOffset = 6

    const days: DayData[] = []

    const prevMonthDate = new Date(year, month, 0)
    for (let i = firstDayOffset - 1; i >= 0; i--) {
      days.push({
        date: new Date(prevMonthDate.getFullYear(), prevMonthDate.getMonth(), prevMonthDate.getDate() - i),
        tasks: [],
        workHours: CALENDAR_CONFIG.DEFAULT_WORK_HOURS,
      })
    }

    for (let d = 1; d <= lastDay.getDate(); d++) {
      days.push({
        date: new Date(year, month, d),
        tasks: [],
        workHours: CALENDAR_CONFIG.DEFAULT_WORK_HOURS,
      })
    }

    const remainingDays = CALENDAR_CONFIG.GRID_CELLS_COUNT - days.length
    for (let d = 1; d <= remainingDays; d++) {
      days.push({
        date: new Date(year, month + 1, d),
        tasks: [],
        workHours: CALENDAR_CONFIG.DEFAULT_WORK_HOURS,
      })
    }

    return days
  })

  return {
    currentDate,
    monthYear,
    dayNames,
    monthData,
    prevMonth,
    nextMonth,
    goToday,
    isToday
  }
}
