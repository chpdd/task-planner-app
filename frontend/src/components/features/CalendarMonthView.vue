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
  monthData: CalendarDayData[]
}

defineProps<Props>()

const emit = defineEmits<{
  workHoursChange: [dayId: number, hours: number]
  executionClick: [execution: ExecutionWithTask]
}>()

const dayNames = [
  'calendar.dayNames.mon',
  'calendar.dayNames.tue',
  'calendar.dayNames.wed',
  'calendar.dayNames.thu',
  'calendar.dayNames.fri',
  'calendar.dayNames.sat',
  'calendar.dayNames.sun',
]

function isToday(date: Date): boolean {
  const today = new Date()
  return date.getDate() === today.getDate() &&
    date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear()
}

function dayLabel(date: Date): string {
  const sundayFirst = [
    'calendar.dayNames.sun',
    'calendar.dayNames.mon',
    'calendar.dayNames.tue',
    'calendar.dayNames.wed',
    'calendar.dayNames.thu',
    'calendar.dayNames.fri',
    'calendar.dayNames.sat',
  ]
  return t(sundayFirst[date.getDay()])
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
</script>

<template>
  <div class="calendar-month-view">
    <div class="dow-headers">
      <div
        v-for="name in dayNames"
        :key="name"
        class="dow"
      >
        {{ t(name) }}
      </div>
    </div>

    <div class="calendar-grid">
      <div
        v-for="(dayData, index) in monthData"
        :key="index"
        class="day"
        :class="{
          'other-month': false,
          today: isToday(dayData.date),
        }"
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
        @drop="handleDrop($event, dayData)"
      >
        <div class="day-head">
          <div class="day-badge">
            <span class="day-dow">{{ dayLabel(dayData.date) }}</span>
            <span class="day-num">{{ dayData.date.getDate() }}</span>
          </div>
          <input
            v-if="dayData.day"
            type="number"
            class="hours-input"
            :value="dayData.day.work_hours"
            min="0"
            max="24"
            step="0.5"
            :placeholder="t('tasks.hoursShort')"
            @input="handleHoursInput($event, dayData.day.id)"
          >
        </div>

        <div class="day-tasks">
          <div
            v-for="execution in dayData.executions"
            :key="execution.id"
            class="drop month-card"
            :class="{ 'is-done': execution.is_done }"
            :style="{
              '--task-interest': getExecutionColor(execution),
              '--task-importance': getExecutionSecondaryColor(execution),
            }"
            @click="handleExecutionClick(execution)"
          >
            <span class="task-name">{{ execution.task?.name || 'Unknown Task' }}</span>
            <span
              v-if="execution.is_done"
              class="done-badge"
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

          <div
            v-if="dayData.executions.length === 0"
            class="drop-placeholder"
          >
            &nbsp;
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.calendar-month-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--surface);
  border-radius: var(--radius);
  overflow: hidden;
}

.dow-headers {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background: var(--bg);
  border-bottom: 3px solid var(--border);
}

.dow {
  padding: 12px 8px;
  text-align: center;
  font-size: 11px;
  font-weight: 600;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-right: 3px solid var(--border);
}

.dow:last-child {
  border-right: none;
}

.calendar-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  grid-template-rows: repeat(6, 1fr);
  gap: 1px;
  background: var(--border);
  overflow-y: auto;
}

.day {
  display: flex;
  flex-direction: column;
  min-height: 132px;
  background: var(--surface);
  padding: 6px;
  transition: background-color 0.15s;
}

.day.other-month {
  background: var(--bg);
  opacity: 0.5;
}

.day.today {
  background: oklch(0.25 0.005 285 / 0.5);
}

.day.drag-over {
  background: oklch(0.70 0.15 240 / 0.1);
}

.day-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 4px;
  min-height: 54px;
}

.day-badge {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
}

.day-dow {
  font-size: 16px;
  line-height: 1;
  font-weight: 600;
  color: var(--muted);
}

.day-num {
  font-size: 28px;
  line-height: 1;
  font-weight: 700;
  color: var(--fg);
}

.day.today .day-num {
  color: var(--accent);
}

.hours-input {
  width: 36px;
  padding: 2px 4px;
  font-size: 10px;
  text-align: center;
  background: var(--bg);
  border: 3px solid var(--border);
  border-radius: 4px;
  color: var(--muted);
  font-family: inherit;
}

.hours-input:focus {
  outline: none;
  border-color: var(--accent);
  color: var(--fg);
}

.hours-input::placeholder {
  color: var(--muted);
  opacity: 0.5;
}

.day-tasks {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.drop {
  padding: 4px 6px;
  font-size: 10px;
  font-weight: 500;
  line-height: 1.3;
  color: var(--bg);
  background: linear-gradient(135deg, var(--task-interest), var(--task-importance));
  border-radius: 3px;
  cursor: grab;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: transform 0.15s, opacity 0.15s;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 4px;
}

.drop:hover {
  transform: scale(1.02);
  opacity: 0.9;
}

.drop:active {
  cursor: grabbing;
}

.drop.is-done {
  opacity: 0.6;
  text-decoration: line-through;
}

.task-name {
  overflow: hidden;
  text-overflow: ellipsis;
}

.done-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: var(--bg);
}

.drop-placeholder {
  flex: 1;
  min-height: 20px;
}
</style>
