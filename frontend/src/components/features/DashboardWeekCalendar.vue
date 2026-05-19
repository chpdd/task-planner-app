<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Task } from '@/domain/Task'
import { useUiStore } from '@/stores/uiStore'
import CalendarViewSwitch from '@/components/features/CalendarViewSwitch.vue'

const { t, locale } = useI18n()
const uiStore = useUiStore()
const localeTag = computed(() => (locale.value === 'ru' ? 'ru-RU' : 'en-US'))

const props = defineProps<{
  focusDate: Date
  periodLabel: string
}>()

const emit = defineEmits<{
  'prev-period': []
  'next-period': []
}>()

interface DayData {
  date: Date
  tasks: Task[]
  workHours: number
}

function startOfWeek(base: Date): Date {
  const d = new Date(base)
  const dayOfWeek = d.getDay()
  const mondayOffset = (dayOfWeek + 6) % 7
  d.setDate(d.getDate() - mondayOffset)
  d.setHours(0, 0, 0, 0)
  return d
}

const calendarData = computed<DayData[]>(() => {
  const focus = new Date(props.focusDate)
  focus.setHours(0, 0, 0, 0)
  const days: DayData[] = []

  if (uiStore.calendarView === 'month') {
    const monthStart = new Date(focus.getFullYear(), focus.getMonth(), 1)
    const monthEnd = new Date(focus.getFullYear(), focus.getMonth() + 1, 0)
    const gridStart = startOfWeek(monthStart)
    const monthEndOffset = (7 - monthEnd.getDay()) % 7
    const gridEnd = new Date(monthEnd)
    gridEnd.setDate(monthEnd.getDate() + monthEndOffset)

    for (let d = new Date(gridStart); d <= gridEnd; d.setDate(d.getDate() + 1)) {
      days.push({ date: new Date(d), tasks: [], workHours: 0 })
    }
    return days
  }

  let start = new Date(focus)
  let count = 1
  if (uiStore.calendarView === 'week' || uiStore.calendarView === 'work_week') {
    start = startOfWeek(focus)
    count = uiStore.calendarView === 'work_week' ? 5 : 7
  } else if (uiStore.calendarView === 'three_days') {
    count = 3
  }

  for (let i = 0; i < count; i++) {
    const d = new Date(start)
    d.setDate(start.getDate() + i)
    days.push({ date: d, tasks: [], workHours: 0 })
  }

  return days
})

function getDayName(date: Date): string {
  return date.toLocaleDateString(localeTag.value, { weekday: 'short' })
}
</script>

<template>
  <div class="week-calendar">
    <div class="week-header">
      <div class="period-nav">
        <button class="period-btn" type="button" @click="emit('prev-period')">←</button>
        <span class="period-label">{{ periodLabel }}</span>
        <button class="period-btn" type="button" @click="emit('next-period')">→</button>
      </div>
      <CalendarViewSwitch
        :model-value="uiStore.calendarView"
        :list-mode="uiStore.calendarListMode"
        @update:model-value="(v) => (uiStore.calendarView = v)"
        @update:list-mode="(v) => (uiStore.calendarListMode = v)"
      />
    </div>

    <div v-if="uiStore.calendarListMode" class="list-mode-empty">
      <span>{{ t('calendar.noTasks') }}</span>
    </div>
    <div
      v-else
      class="week-grid"
      :class="{ 'month-grid': uiStore.calendarView === 'month' }"
      :style="{ gridTemplateColumns: uiStore.calendarView === 'month' ? 'repeat(7, 1fr)' : `repeat(${calendarData.length || 1}, 1fr)` }"
    >
      <div v-for="day in calendarData" :key="day.date.toISOString()" class="week-day">
        <div class="week-day-header" :class="{ 'month-day-header': uiStore.calendarView === 'month' }">
          <span v-if="uiStore.calendarView !== 'month'" class="week-day-name">{{ getDayName(day.date) }}</span>
          <span class="week-day-num" :class="{ 'month-day-num': uiStore.calendarView === 'month' }">{{ day.date.getDate() }}</span>
        </div>
        <div class="week-day-tasks">
          <div v-for="task in day.tasks" :key="task.id" class="week-task">
            {{ task.name }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.week-calendar {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--surface);
  border: 3px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  margin: 20px;
  max-height: calc(100vh - 140px);
}

.week-header {
  padding: 10px 12px;
  border-bottom: 3px solid var(--border);
  background: var(--bg);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.period-nav {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.period-btn {
  width: 30px;
  height: 30px;
  border: 3px solid var(--border);
  border-radius: 6px;
  background: var(--surface);
  color: var(--fg);
  cursor: pointer;
}

.period-label {
  min-width: 190px;
  text-align: center;
  font-size: 12px;
  color: var(--muted);
  font-weight: 600;
}

.week-grid {
  flex: 1;
  display: grid;
  gap: 1px;
  background: var(--border);
  overflow: auto;
}

.month-grid .week-day {
  min-height: 140px;
}

.week-day {
  background: var(--surface);
  display: flex;
  flex-direction: column;
  min-height: 200px;
}

.week-day-header {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  min-height: 74px;
  padding: 10px 12px 8px;
  border-bottom: 3px solid var(--border);
  background: var(--bg);
  gap: 4px;
}

.month-day-header {
  min-height: 36px;
  padding: 6px 8px;
  gap: 0;
}

.week-day-name {
  font-size: 15px;
  line-height: 1;
  font-weight: 500;
  color: var(--muted);
}

.week-day-num {
  font-size: 15px;
  line-height: 1;
  font-weight: 600;
  color: var(--fg);
}

.month-day-num {
  font-size: 12px;
  color: var(--muted);
}

.week-day-tasks {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 8px;
}

.week-task {
  padding: 4px 8px;
  background: var(--accent);
  color: var(--bg);
  border-radius: 4px;
  font-size: 11px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.list-mode-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--muted);
  font-size: 14px;
}
</style>
