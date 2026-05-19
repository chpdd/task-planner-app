<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Day, TaskExecution, UpdateExecutionData } from '@/types/api'
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
  dayData: CalendarDayData | undefined
}

const props = defineProps<Props>()

const emit = defineEmits<{
  workHoursChange: [dayId: number, hours: number]
  executionUpdate: [executionId: number, data: UpdateExecutionData]
  executionClick: [execution: ExecutionWithTask]
}>()

// Track editing hours state
const editingHoursId = ref<number | null>(null)
const editingHoursValue = ref<number>(0)

const dayNamesShort = [
  'calendar.dayNames.sun',
  'calendar.dayNames.mon',
  'calendar.dayNames.tue',
  'calendar.dayNames.wed',
  'calendar.dayNames.thu',
  'calendar.dayNames.fri',
  'calendar.dayNames.sat',
]

function getDayLabel(): string {
  if (!props.dayData) return ''
  return t(dayNamesShort[props.dayData.date.getDay()])
}

function getTotalHours(): number {
  if (!props.dayData) return 0
  return props.dayData.executions.reduce((sum, exec) => sum + exec.doing_hours, 0)
}

function handleWorkHoursInput(event: Event) {
  if (!props.dayData?.day) return
  const input = event.target as HTMLInputElement
  const hours = parseFloat(input.value) || 0
  emit('workHoursChange', props.dayData.day.id, hours)
}

function handleDoneToggle(execution: ExecutionWithTask) {
  emit('executionUpdate', execution.id, { is_done: !execution.is_done })
}

function startEditingHours(execution: ExecutionWithTask) {
  editingHoursId.value = execution.id
  editingHoursValue.value = execution.doing_hours
}

function finishEditingHours(execution: ExecutionWithTask) {
  if (editingHoursValue.value !== execution.doing_hours) {
    emit('executionUpdate', execution.id, { doing_hours: editingHoursValue.value })
  }
  editingHoursId.value = null
}

function cancelEditingHours() {
  editingHoursId.value = null
}

function handleHoursKeydown(event: KeyboardEvent, execution: ExecutionWithTask) {
  if (event.key === 'Enter') {
    finishEditingHours(execution)
  } else if (event.key === 'Escape') {
    cancelEditingHours()
  }
}

function handleExecutionClick(execution: ExecutionWithTask) {
  emit('executionClick', execution)
}

function getInterestColor(interest: number): string {
  const hue = 145 // Green
  const chroma = (interest - 1) * (0.35 / 9)
  return `oklch(0.65 ${chroma} ${hue})`
}

function getImportanceColor(importance: number): string {
  const hue = 28 // Red
  const chroma = (importance - 1) * (0.35 / 9)
  return `oklch(0.65 ${chroma} ${hue})`
}
</script>

<template>
  <div class="calendar-day-view">
    <!-- Day header -->
    <div class="day-view-head">
      <div class="head-left">
        <div class="date-badge">
          <span class="day-name">{{ getDayLabel() }}</span>
          <span class="day-date">{{ dayData?.date.getDate() || '' }}</span>
        </div>
      </div>
      <div class="head-right">
        <input
          v-if="dayData?.day"
          type="number"
          class="work-hours-input"
          :value="dayData.day.work_hours"
          min="0"
          max="24"
          step="0.5"
          :placeholder="t('calendar.workHours')"
          @change="handleWorkHoursInput"
        >
        <span class="day-hours">{{ t('tasks.hoursTotal', { hours: getTotalHours() }) }}</span>
      </div>
    </div>

    <!-- Tasks list -->
    <div class="day-view-body">
      <div
        v-if="!dayData || dayData.executions.length === 0"
        class="empty-state"
      >
        <span>{{ t('tasks.empty') }}</span>
      </div>

      <div
        v-for="execution in dayData?.executions"
        :key="execution.id"
        class="execution-card"
        :class="{ 'is-done': execution.is_done }"
        :style="{
          '--task-interest': execution.task ? getInterestColor(execution.task.interest) : 'var(--surface)',
          '--task-importance': execution.task ? getImportanceColor(execution.task.importance) : 'var(--border)',
        }"
        @click="handleExecutionClick(execution)"
      >
        <div class="task-accent" />

        <div class="task-content">
          <div class="task-header">
            <h4 class="task-name">
              {{ execution.task?.name || 'Unknown Task' }}
            </h4>
            <label
              class="done-checkbox"
              :title="execution.is_done ? t('calendar.markUndone') : t('calendar.markDone')"
              @click.stop
            >
              <input
                type="checkbox"
                :checked="execution.is_done"
                @change="handleDoneToggle(execution)"
              >
              <span class="checkmark">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="12"
                  height="12"
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
            </label>
          </div>

          <div class="task-meta">
            <span
              v-if="execution.task?.deadline"
              class="meta-pill"
            >
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                width="12"
                height="12"
              >
                <circle
                  cx="12"
                  cy="12"
                  r="10"
                />
                <polyline points="12,6 12,12 16,14" />
              </svg>
              {{ new Date(execution.task.deadline).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) }}
            </span>
            <span
              v-if="execution.task"
              class="meta-pill interest"
            >
              <svg
                viewBox="0 0 24 24"
                fill="currentColor"
                width="12"
                height="12"
              >
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
              </svg>
              {{ execution.task.interest }}
            </span>
            <span
              v-if="execution.task"
              class="meta-pill importance"
            >
              <svg
                viewBox="0 0 24 24"
                fill="currentColor"
                width="12"
                height="12"
              >
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
              </svg>
              {{ execution.task.importance }}
            </span>
          </div>

          <div class="task-hours-row">
            <label class="hours-label">{{ t('calendar.doingHours') }}:</label>
            <div
              v-if="editingHoursId === execution.id"
              class="hours-edit"
            >
              <input
                v-model.number="editingHoursValue"
                type="number"
                min="0"
                max="24"
                step="0.5"
                class="hours-input"
                autofocus
                @keydown="handleHoursKeydown($event, execution)"
                @blur="finishEditingHours(execution)"
              >
              <span class="hours-suffix">{{ t('tasks.hoursShort') }}</span>
            </div>
            <div
              v-else
              class="hours-display"
              :title="t('calendar.clickToEdit')"
              @click.stop="startEditingHours(execution)"
            >
              {{ execution.doing_hours }}{{ t('tasks.hoursShort') }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.calendar-day-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--surface);
  border-radius: var(--radius);
  overflow: hidden;
}

.day-view-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 3px solid var(--border);
  background: var(--bg);
}

.head-left {
  display: flex;
  align-items: center;
}

.head-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.date-badge {
  display: inline-flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  min-width: 48px;
  padding: 4px 0;
}

.day-name {
  font-size: 24px;
  line-height: 1;
  font-weight: 600;
  color: var(--muted);
}

.day-date {
  font-size: 42px;
  line-height: 1;
  font-weight: 700;
  color: var(--fg);
}

.work-hours-input {
  width: 60px;
  padding: 4px 8px;
  font-size: 12px;
  text-align: center;
  background: var(--surface);
  border: 3px solid var(--border);
  border-radius: 6px;
  color: var(--fg);
  font-family: inherit;
}

.work-hours-input:focus {
  outline: none;
  border-color: var(--accent);
}

.day-hours {
  font-size: 13px;
  color: var(--accent);
  font-weight: 500;
}

.day-view-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--muted);
  font-size: 14px;
}

.execution-card {
  position: relative;
  display: flex;
  background: var(--bg);
  border: 3px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 14px 14px 22px;
  cursor: pointer;
  transition: background-color 0.15s, box-shadow 0.15s, transform 0.15s;
}

.execution-card:hover {
  background: var(--surface-hover);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

.execution-card.is-done {
  opacity: 0.7;
}

.execution-card.is-done .task-name {
  text-decoration: line-through;
}

.task-accent {
  position: absolute;
  left: 8px;
  top: 12px;
  bottom: 12px;
  width: 4px;
  background: linear-gradient(180deg, var(--task-interest), var(--task-importance));
  border-radius: 999px;
}

.task-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
}

.task-name {
  font-size: 15px;
  font-weight: 500;
  color: var(--fg);
  margin: 0;
  line-height: 1.4;
}

.done-checkbox {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
}

.done-checkbox input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.checkmark {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  background: var(--surface);
  border: 3px solid var(--border);
  border-radius: 4px;
  transition: background-color 0.15s, border-color 0.15s;
}

.done-checkbox:hover .checkmark {
  border-color: var(--accent);
}

.done-checkbox input:checked ~ .checkmark {
  background: var(--accent);
  border-color: var(--accent);
}

.done-checkbox input:checked ~ .checkmark svg {
  color: var(--bg);
}

.task-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 4px;
}

.meta-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 500;
  border-radius: 999px;
  background: var(--surface);
  border: 3px solid var(--border);
  color: var(--muted);
  white-space: nowrap;
}

.meta-pill.interest svg {
  color: var(--task-interest);
}

.meta-pill.importance svg {
  color: var(--task-importance);
}

.task-hours-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 3px solid var(--border);
}

.hours-label {
  font-size: 12px;
  color: var(--muted);
}

.hours-display {
  padding: 4px 12px;
  font-size: 13px;
  font-weight: 500;
  color: var(--fg);
  background: var(--surface);
  border: 3px solid var(--border);
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.15s, border-color 0.15s;
}

.hours-display:hover {
  background: var(--surface-hover);
  border-color: var(--accent);
}

.hours-edit {
  display: flex;
  align-items: center;
  gap: 6px;
}

.hours-input {
  width: 60px;
  padding: 4px 8px;
  font-size: 13px;
  font-weight: 500;
  text-align: center;
  background: var(--surface);
  border: 1px solid var(--accent);
  border-radius: 6px;
  color: var(--fg);
  font-family: inherit;
}

.hours-input:focus {
  outline: none;
}

.hours-suffix {
  font-size: 12px;
  color: var(--muted);
}
</style>
