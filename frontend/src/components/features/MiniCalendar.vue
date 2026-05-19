<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

interface Props {
  selectedDate?: Date | null
  selectedRangeStart?: Date | null
  selectedRangeEnd?: Date | null
}

const props = withDefaults(defineProps<Props>(), {
  selectedDate: null,
  selectedRangeStart: null,
  selectedRangeEnd: null,
})

const emit = defineEmits<{
  'date-select': [date: Date]
}>()

const { locale } = useI18n()
const localeTag = computed(() => (locale.value === 'ru' ? 'ru-RU' : 'en-US'))
const currentMonth = ref(new Date(props.selectedDate || new Date()))

watch(
  () => props.selectedDate,
  (value) => {
    if (!value) return
    currentMonth.value = new Date(value)
  },
)

const monthYear = computed(() =>
  currentMonth.value.toLocaleDateString(localeTag.value, { month: 'long', year: 'numeric' }),
)
const dayNames = computed(() => {
  const monday = new Date(2026, 4, 18) // Monday
  return Array.from({ length: 7 }).map((_, index) => {
    const d = new Date(monday)
    d.setDate(monday.getDate() + index)
    return d.toLocaleDateString(localeTag.value, { weekday: 'short' })
  })
})

function prevMonth() {
  currentMonth.value = new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth() - 1, 1)
}

function nextMonth() {
  currentMonth.value = new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth() + 1, 1)
}

interface CalendarDay {
  date: Date
  isCurrentMonth: boolean
  isToday: boolean
  isInSelectedRange: boolean
}

const calendarDays = computed<CalendarDay[]>(() => {
  const year = currentMonth.value.getFullYear()
  const month = currentMonth.value.getMonth()
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)

  let firstDayOffset = firstDay.getDay() - 1
  if (firstDayOffset < 0) firstDayOffset = 6

  const gridStart = new Date(firstDay)
  gridStart.setDate(firstDay.getDate() - firstDayOffset)
  gridStart.setHours(0, 0, 0, 0)

  const lastDayOffset = (7 - lastDay.getDay()) % 7
  const gridEnd = new Date(lastDay)
  gridEnd.setDate(lastDay.getDate() + lastDayOffset)
  gridEnd.setHours(0, 0, 0, 0)

  const today = new Date()
  today.setHours(0, 0, 0, 0)

  const selectedRangeStart = props.selectedRangeStart ? new Date(props.selectedRangeStart) : null
  const selectedRangeEnd = props.selectedRangeEnd ? new Date(props.selectedRangeEnd) : null
  if (selectedRangeStart) selectedRangeStart.setHours(0, 0, 0, 0)
  if (selectedRangeEnd) selectedRangeEnd.setHours(0, 0, 0, 0)

  const days: CalendarDay[] = []
  for (let date = new Date(gridStart); date <= gridEnd; date.setDate(date.getDate() + 1)) {
    const dayDate = new Date(date)
    dayDate.setHours(0, 0, 0, 0)
    days.push({
      date: dayDate,
      isCurrentMonth: dayDate.getMonth() === month,
      isToday: dayDate.getTime() === today.getTime(),
      isInSelectedRange: Boolean(
        selectedRangeStart && selectedRangeEnd && dayDate >= selectedRangeStart && dayDate <= selectedRangeEnd,
      ),
    })
  }

  return days
})

function isRangeStart(index: number): boolean {
  if (!calendarDays.value[index]?.isInSelectedRange) return false
  return index === 0 || !calendarDays.value[index - 1].isInSelectedRange
}

function isRangeEnd(index: number): boolean {
  if (!calendarDays.value[index]?.isInSelectedRange) return false
  return index === calendarDays.value.length - 1 || !calendarDays.value[index + 1].isInSelectedRange
}

function handleDayClick(day: CalendarDay) {
  emit('date-select', day.date)
}
</script>

<template>
  <div class="mini-calendar">
    <div class="mini-calendar-nav">
      <button class="nav-btn" type="button" @click="prevMonth">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12">
          <polyline points="15,18 9,12 15,6" />
        </svg>
      </button>
      <span class="mini-calendar-title">{{ monthYear }}</span>
      <button class="nav-btn" type="button" @click="nextMonth">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12">
          <polyline points="9,6 15,12 9,18" />
        </svg>
      </button>
    </div>

    <div class="mini-calendar-day-names">
      <span v-for="dayName in dayNames" :key="dayName" class="day-name">{{ dayName }}</span>
    </div>

    <div class="mini-calendar-grid">
      <button
        v-for="(day, index) in calendarDays"
        :key="day.date.toISOString()"
        type="button"
        class="mini-calendar-day"
        :class="{
          'other-month': !day.isCurrentMonth,
          'is-today': day.isToday,
          'is-in-selected-range': day.isInSelectedRange,
          'range-start': isRangeStart(index),
          'range-end': isRangeEnd(index),
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
  border: 3px solid var(--border);
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
  border: 3px solid var(--border);
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
  gap: 0;
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
  gap: 0;
}

.mini-calendar-day {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: var(--fg);
  border-radius: 0;
  cursor: pointer;
  transition: background-color 0.15s;
  border: none;
  background: transparent;
  padding: 0;
}

.mini-calendar-day:hover {
  background: var(--surface);
}

.mini-calendar-day.is-in-selected-range {
  background: color-mix(in oklab, var(--accent) 24%, transparent);
}

.mini-calendar-day.range-start {
  border-top-left-radius: 999px;
  border-bottom-left-radius: 999px;
}

.mini-calendar-day.range-end {
  border-top-right-radius: 999px;
  border-bottom-right-radius: 999px;
}

.mini-calendar-day.is-today {
  color: var(--accent);
  font-weight: 700;
  background: color-mix(in oklab, var(--accent) 22%, transparent);
  box-shadow: inset 0 0 0 1.5px var(--accent);
  border-radius: 999px;
}

.mini-calendar-day.is-in-selected-range.is-today {
  color: var(--accent) !important;
  box-shadow: inset 0 0 0 1.5px var(--accent);
  border-radius: 999px;
}

.mini-calendar-day.other-month {
  opacity: 0.55;
}
</style>
