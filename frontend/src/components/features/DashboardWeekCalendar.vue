<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Task } from '@/domain/Task'

const { t } = useI18n()

interface DayData {
  date: Date
  tasks: Task[]
  workHours: number
}

// Week data logic
const weekData = computed<DayData[]>(() => {
  const today = new Date()
  const dayOfWeek = today.getDay() - 1
  const monday = new Date(today)
  monday.setDate(today.getDate() - (dayOfWeek >= 0 ? dayOfWeek : 6))

  const days: DayData[] = []
  for (let i = 0; i < 7; i++) {
    const date = new Date(monday)
    date.setDate(monday.getDate() + i)
    days.push({
      date,
      tasks: [],
      workHours: 0,
    })
  }
  return days
})

// Week number logic
const weekNumber = computed(() => {
  const today = new Date()
  const start = new Date(today.getFullYear(), 0, 1)
  const diff = today.getTime() - start.getTime()
  const oneWeek = 604800000
  return Math.ceil((diff + start.getDay() * 86400000) / oneWeek)
})

// Day name helper
function getDayName(date: Date): string {
  const days = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']
  return days[date.getDay()]
}
</script>

<template>
  <div class="week-calendar">
    <div class="week-header">
      <span class="week-label">{{ t('calendar.week') }} {{ weekNumber }}</span>
    </div>
    <div class="week-grid">
      <div v-for="day in weekData" :key="day.date.toISOString()" class="week-day">
        <div class="week-day-header">
          <span class="week-day-name">{{ getDayName(day.date) }}</span>
          <span class="week-day-num">{{ day.date.getDate() }}</span>
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
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  margin: 20px;
  max-height: calc(100vh - 140px);
}

.week-header {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  background: var(--bg);
}

.week-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--fg);
}

.week-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  background: var(--border);
  overflow: auto;
}

.week-day {
  background: var(--surface);
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-height: 200px;
}

.week-day-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.week-day-name {
  font-size: 10px;
  color: var(--muted);
  text-transform: uppercase;
}

.week-day-num {
  font-size: 14px;
  font-weight: 600;
  color: var(--fg);
}

.week-day-tasks {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
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
</style>
