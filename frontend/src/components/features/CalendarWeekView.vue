<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { Day, TaskExecution } from '@/types/api'
import { Task } from '@/domain/Task'

const { t } = useI18n()

// Extended execution with task info
interface ExecutionWithTask extends TaskExecution {
  task?: Task
}

interface CalendarDayData {
  date: Date
  day: Day
  executions: ExecutionWithTask[]
}

interface Props {
  weekData: CalendarDayData[]
}

defineProps<Props>()

const emit = defineEmits<{
  workHoursChange: [dayId: number, hours: number]
  executionClick: [execution: ExecutionWithTask]
}>()

const dayNamesShort = [
  'calendar.dayNames.sun',
  'calendar.dayNames.mon',
  'calendar.dayNames.tue',
  'calendar.dayNames.wed',
  'calendar.dayNames.thu',
  'calendar.dayNames.fri',
  'calendar.dayNames.sat',
]

function dayLabel(date: Date): string {
  return t(dayNamesShort[date.getDay()])
}

function isToday(date: Date): boolean {
  const today = new Date()
  return date.getDate() === today.getDate() &&
    date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear()
}

function handleDragOver(event: DragEvent) {
  event.preventDefault()
  const target = event.currentTarget as HTMLElement
  target.classList.add('drag-over')
}

function handleDragLeave(event: DragEvent) {
  const target = event.currentTarget as HTMLElement
  target.classList.remove('drag-over')
}

function handleDrop(event: DragEvent, _dayData: CalendarDayData) {
  event.preventDefault()
  const target = event.currentTarget as HTMLElement
  target.classList.remove('drag-over')
  // TODO: Handle task drop from sidebar
}

function handleHoursInput(event: Event, dayId: number) {
  const input = event.target as HTMLInputElement
  const hours = parseFloat(input.value) || 0
  emit('workHoursChange', dayId, hours)
}

function handleExecutionClick(execution: ExecutionWithTask) {
  emit('executionClick', execution)
}

function getExecutionColor(execution: ExecutionWithTask): string {
  if (execution.task) {
    const hue = 145 // Green
    const chroma = (execution.task.interest - 1) * (0.35 / 9)
    return `oklch(0.65 ${chroma} ${hue})`
  }
  return 'var(--surface)'
}

function getExecutionSecondaryColor(execution: ExecutionWithTask): string {
  if (execution.task) {
    const hue = 28 // Red
    const chroma = (execution.task.importance - 1) * (0.35 / 9)
    return `oklch(0.65 ${chroma} ${hue})`
  }
  return 'var(--border)'
}

function getCardHeight(execution: ExecutionWithTask): number {
  return Math.max(30, execution.doing_hours * 20)
}
</script>

<template>
  <div class="calendar-week-view">
    <div class="week-view-head">
      <div
        v-for="(dayData, index) in weekData"
        :key="index"
        class="week-day-header"
        :class="{ today: isToday(dayData.date) }"
      >
        <span class="dow-label">{{ dayLabel(dayData.date) }}</span>
        <span class="date-num">{{ dayData.date.getDate() }}</span>
        <input
          v-if="dayData.day"
          type="number"
          class="hours-input-header"
          :value="dayData.day.work_hours"
          min="0"
          max="24"
          step="0.5"
          :placeholder="t('tasks.hoursShort')"
          @input="handleHoursInput($event, dayData.day.id)"
        >
      </div>
    </div>

    <div class="week-view-grid">
      <div
        v-for="(dayData, index) in weekData"
        :key="index"
        class="week-col"
        :class="{ today: isToday(dayData.date) }"
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
        @drop="handleDrop($event, dayData)"
      >
        <div class="col-tasks">
          <div
            v-for="execution in dayData.executions"
            :key="execution.id"
            class="week-card"
            :class="{ 'is-done': execution.is_done }"
            :style="{
              '--task-interest': getExecutionColor(execution),
              '--task-importance': getExecutionSecondaryColor(execution),
              '--card-height': `${getCardHeight(execution)}px`,
            }"
            @click="handleExecutionClick(execution)"
          >
            <div class="week-card-header">
              <span class="week-card-name">{{ execution.task?.name || 'Unknown Task' }}</span>
              <span
                v-if="execution.is_done"
                class="done-indicator"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="10"
                  height="10"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="3"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <polyline points="20,6 9,17 4,12" />
                </svg>
              </span>
            </div>
            <span class="week-card-hours">{{ execution.doing_hours }}{{ t('tasks.hoursShort') }}</span>
          </div>

          <div
            v-if="dayData.executions.length === 0"
            class="empty-slot"
          >
            <span>{{ t('calendar.dropTask') }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.calendar-week-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--surface);
  border: 3px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
}

.week-view-head {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  border-bottom: 3px solid var(--border);
  background: var(--bg);
}

.week-day-header {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 12px 8px;
  border-right: 3px solid var(--border);
  min-height: 94px;
  gap: 6px;
}

.week-day-header:last-child {
  border-right: none;
}

.week-day-header.today {
  background: oklch(0.25 0.005 285 / 0.5);
}

.dow-label {
  font-size: 20px;
  line-height: 1;
  font-weight: 600;
  color: var(--muted);
}

.week-day-header.today .dow-label {
  color: var(--accent);
}

.date-num {
  font-size: 36px;
  line-height: 1;
  font-weight: 700;
  color: var(--fg);
}

.week-day-header.today .date-num {
  color: var(--accent);
}

.hours-input-header {
  width: 48px;
  padding: 2px 4px;
  font-size: 10px;
  text-align: center;
  background: var(--surface);
  border: 3px solid var(--border);
  border-radius: 4px;
  color: var(--muted);
  font-family: inherit;
}

.hours-input-header:focus {
  outline: none;
  border-color: var(--accent);
  color: var(--fg);
}

.week-view-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  overflow-y: auto;
}

.week-col {
  display: flex;
  flex-direction: column;
  border-right: 3px solid var(--border);
  min-width: 120px;
  transition: background-color 0.15s;
}

.week-col:last-child {
  border-right: none;
}

.week-col.today {
  background: oklch(0.25 0.005 285 / 0.3);
}

.week-col.drag-over {
  background: oklch(0.70 0.15 240 / 0.1);
}

.col-tasks {
  flex: 1;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.empty-slot {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 80px;
  border: 2px dashed var(--border);
  border-radius: var(--radius);
  color: var(--muted);
  font-size: 12px;
  opacity: 0.6;
}

.week-card {
  min-height: var(--card-height, 30px);
  padding: 8px 10px;
  background: linear-gradient(135deg, var(--task-interest), var(--task-importance));
  border-radius: calc(var(--radius) - 2px);
  cursor: grab;
  transition: transform 0.15s, box-shadow 0.15s, opacity 0.15s;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.week-card:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.week-card:active {
  cursor: grabbing;
  opacity: 0.8;
}

.week-card.is-done {
  opacity: 0.6;
}

.week-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 4px;
}

.week-card-name {
  font-size: 11px;
  font-weight: 500;
  color: var(--bg);
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.week-card.is-done .week-card-name {
  text-decoration: line-through;
}

.done-indicator {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: var(--bg);
}

.week-card-hours {
  font-size: 10px;
  color: var(--bg);
  opacity: 0.8;
}
</style>
