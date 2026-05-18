<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  selectedDate?: Date | null
}

const props = withDefaults(defineProps<Props>(), {
  selectedDate: null,
})

const emit = defineEmits<{
  'date-select': [date: Date]
}>()

// Day names in Russian (starting from Monday)
const dayNames = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

// Internal state: current month being displayed
const currentMonth = ref(new Date(props.selectedDate || new Date()))

// Month name in Russian
const monthNames = [
  'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
  'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
]

const monthYear = computed(() => {
  return `${monthNames[currentMonth.value.getMonth()]} ${currentMonth.value.getFullYear()}`
})

// Navigation
function prevMonth() {
  currentMonth.value = new Date(
    currentMonth.value.getFullYear(),
    currentMonth.value.getMonth() - 1,
    1
  )
}

function nextMonth() {
  currentMonth.value = new Date(
    currentMonth.value.getFullYear(),
    currentMonth.value.getMonth() + 1,
    1
  )
}

// Generate calendar days
interface CalendarDay {
  date: Date
  isCurrentMonth: boolean
  isToday: boolean
  isSelected: boolean
}

const calendarDays = computed<CalendarDay[]>(() => {
  const year = currentMonth.value.getFullYear()
  const month = currentMonth.value.getMonth()
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)

  // Calculate offset to start from Monday (0 = Monday, 6 = Sunday)
  let firstDayOffset = firstDay.getDay() - 1
  if (firstDayOffset < 0) firstDayOffset = 6

  const days: CalendarDay[] = []
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  const selected = props.selectedDate
    ? new Date(props.selectedDate)
    : null
  if (selected) {
    selected.setHours(0, 0, 0, 0)
  }

  // Previous month days
  const prevMonth = new Date(year, month, 0)
  for (let i = firstDayOffset - 1; i >= 0; i--) {
    const date = new Date(prevMonth.getFullYear(), prevMonth.getMonth(), prevMonth.getDate() - i)
    date.setHours(0, 0, 0, 0)
    days.push({
      date,
      isCurrentMonth: false,
      isToday: date.getTime() === today.getTime(),
      isSelected: selected ? date.getTime() === selected.getTime() : false,
    })
  }

  // Current month days
  for (let d = 1; d <= lastDay.getDate(); d++) {
    const date = new Date(year, month, d)
    date.setHours(0, 0, 0, 0)
    days.push({
      date,
      isCurrentMonth: true,
      isToday: date.getTime() === today.getTime(),
      isSelected: selected ? date.getTime() === selected.getTime() : false,
    })
  }

  // Next month days to complete 6 weeks (42 cells)
  const remainingDays = 42 - days.length
  for (let d = 1; d <= remainingDays; d++) {
    const date = new Date(year, month + 1, d)
    date.setHours(0, 0, 0, 0)
    days.push({
      date,
      isCurrentMonth: false,
      isToday: date.getTime() === today.getTime(),
      isSelected: selected ? date.getTime() === selected.getTime() : false,
    })
  }

  return days
})

// Handle day click
function handleDayClick(day: CalendarDay) {
  emit('date-select', day.date)
}
</script>

<template>
  <div class="mini-calendar">
    <!-- Navigation header -->
    <div class="mini-calendar-nav">
      <button
        class="nav-btn"
        type="button"
        @click="prevMonth"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12">
          <polyline points="15,18 9,12 15,6" />
        </svg>
      </button>
      <span class="mini-calendar-title">{{ monthYear }}</span>
      <button
        class="nav-btn"
        type="button"
        @click="nextMonth"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12">
          <polyline points="9,6 15,12 9,18" />
        </svg>
      </button>
    </div>

    <!-- Day names -->
    <div class="mini-calendar-day-names">
      <span
        v-for="dayName in dayNames"
        :key="dayName"
        class="day-name"
      >
        {{ dayName }}
      </span>
    </div>

    <!-- Calendar grid -->
    <div class="mini-calendar-grid">
      <button
        v-for="day in calendarDays"
        :key="day.date.toISOString()"
        type="button"
        class="mini-calendar-day"
        :class="{
          'other-month': !day.isCurrentMonth,
          'is-today': day.isToday,
          'is-selected': day.isSelected,
        }"
        @click="handleDayClick(day)"
      >
        {{ day.date.getDate() }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.mini-calendar {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 12px;
}

.mini-calendar-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.nav-btn {
  width: 24px;
  height: 24px;
  border: 1px solid var(--border);
  border-radius: 4px;
  background: var(--surface);
  color: var(--muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.15s, color 0.15s;
  padding: 0;
}

.nav-btn:hover {
  background: var(--surface-hover);
  color: var(--fg);
}

.mini-calendar-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--fg);
}

.mini-calendar-day-names {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
  margin-bottom: 4px;
}

.day-name {
  text-align: center;
  font-size: 9px;
  font-weight: 500;
  color: var(--muted);
  padding: 2px 0;
}

.mini-calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
}

.mini-calendar-day {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: var(--fg);
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.15s;
  border: none;
  background: transparent;
  padding: 0;
}

.mini-calendar-day:hover {
  background: var(--surface);
}

.mini-calendar-day.is-today {
  background: var(--accent);
  color: var(--bg);
  font-weight: 600;
}

.mini-calendar-day.is-selected:not(.is-today) {
  background: var(--surface-hover);
  outline: 1px solid var(--accent);
}

.mini-calendar-day.other-month {
  color: var(--muted);
  opacity: 0.5;
}
</style>
