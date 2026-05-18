<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import AppShell from '@/components/layout/AppShell.vue'
import Sidebar from '@/components/layout/Sidebar.vue'
import { useCalendarGrid } from '@/composables/useCalendarGrid'

const { t } = useI18n()
const {
  currentDate,
  monthYear,
  dayNames,
  monthData,
  prevMonth,
  nextMonth,
  goToday,
  isToday
} = useCalendarGrid()

function getTaskColor(task: any) {
  // Logic for task color based on interest/importance if needed
  return 'var(--accent)'
}
</script>

<template>
  <AppShell>
    <template #sidebar>
      <Sidebar view-type="calendar" />
    </template>

    <div class="schedule-view">
      <!-- Header with month navigation -->
      <div class="calendar-header">
        <div class="nav-controls">
          <button class="nav-btn" @click="prevMonth" :title="t('calendar.previousPeriod')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
              <polyline points="15,18 9,12 15,6" />
            </svg>
          </button>
          <h2 class="month-year">{{ monthYear }}</h2>
          <button class="nav-btn" @click="nextMonth" :title="t('calendar.nextPeriod')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
              <polyline points="9,6 15,12 9,18" />
            </svg>
          </button>
        </div>
        <button class="today-btn" @click="goToday">
          {{ t('calendar.today') }}
        </button>
      </div>

      <!-- Day of week labels -->
      <div class="dow-row">
        <div v-for="day in dayNames" :key="day.full" class="dow-label">
          {{ day.short }}
        </div>
      </div>

      <!-- Calendar grid -->
      <div class="calendar-grid">
        <div
          v-for="(day, index) in monthData"
          :key="index"
          class="day-cell"
          :class="{
            'other-month': day.date.getMonth() !== currentDate.getMonth(),
            'is-today': isToday(day.date),
          }"
        >
          <div class="day-number">{{ day.date.getDate() }}</div>
          <div class="day-tasks">
            <!-- Future: Add tasks for this day if available in monthData -->
          </div>
        </div>
      </div>
    </div>
  </AppShell>
</template>

<style scoped>
.schedule-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 20px;
  gap: 12px;
}

.calendar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 8px;
}

.nav-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.nav-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  color: var(--fg);
  cursor: pointer;
  transition: background-color 0.15s, border-color 0.15s;
}

.nav-btn:hover {
  background: var(--surface-hover);
  border-color: var(--accent);
}

.month-year {
  font-size: 20px;
  font-weight: 600;
  color: var(--fg);
  min-width: 180px;
  text-align: center;
  margin: 0;
}

.today-btn {
  padding: 8px 16px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  color: var(--fg);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.15s, border-color 0.15s;
}

.today-btn:hover {
  background: var(--surface-hover);
  border-color: var(--accent);
}

.dow-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  border-bottom: 1px solid var(--border);
  padding-bottom: 8px;
}

.dow-label {
  text-align: center;
  font-size: 12px;
  font-weight: 600;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.calendar-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  grid-template-rows: repeat(6, 1fr);
  gap: 1px;
  background: var(--border);
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
}

.day-cell {
  display: flex;
  flex-direction: column;
  background: var(--calendar-bg);
  padding: 8px;
  min-height: 100px;
  transition: background-color 0.15s;
}

.day-cell.other-month {
  background: var(--bg);
}

.day-cell.other-month .day-number {
  color: var(--muted);
  opacity: 0.5;
}

.day-cell.is-today {
  background: oklch(0.25 0.005 285 / 0.5);
}

.day-cell.is-today .day-number {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent);
  color: var(--fg);
  border-radius: 50%;
}

.day-number {
  font-size: 12px;
  font-family: var(--font-mono);
  color: var(--muted);
  text-align: right;
  margin-bottom: 4px;
}

.day-tasks {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 3px;
  overflow: hidden;
}

.task-chip {
  padding: 3px 6px;
  font-size: 10px;
  font-weight: 500;
  color: var(--bg);
  border-radius: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
