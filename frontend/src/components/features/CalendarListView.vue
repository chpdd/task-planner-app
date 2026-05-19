<script setup lang="ts">
import type { Day, TaskExecution } from '@/types/api'
import { Task } from '@/domain/Task'

interface ExecutionWithTask extends TaskExecution {
  task?: Task
}

interface CalendarDayData {
  date: Date
  day: Day
  executions: ExecutionWithTask[]
}

defineProps<{
  listData: CalendarDayData[]
}>()

function dateTitle(date: Date): string {
  return date.toLocaleDateString('ru-RU', { weekday: 'long', day: 'numeric', month: 'long' })
}
</script>

<template>
  <div class="list-view">
    <div v-for="dayData in listData" :key="dayData.date.toISOString()" class="list-day">
      <div class="list-day-title">{{ dateTitle(dayData.date) }}</div>
      <div v-if="!dayData.executions.length" class="list-empty">Нет задач</div>
      <div v-for="execution in dayData.executions" :key="execution.id" class="list-item">
        <span class="name">{{ execution.task?.name || 'Unknown Task' }}</span>
        <span class="hours">{{ execution.doing_hours }}ч</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.list-view {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.list-day {
  border: 3px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
}

.list-day-title {
  padding: 10px 12px;
  background: var(--surface);
  font-weight: 600;
}

.list-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 12px;
  border-top: 3px solid var(--border);
}

.hours {
  color: var(--muted);
}

.list-empty {
  padding: 10px 12px;
  color: var(--muted);
}
</style>
