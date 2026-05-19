<script setup lang="ts">
import { useCalendarGrid } from '@/composables/useCalendarGrid'

const {
  currentDate,
  monthYear,
  dayNames,
  monthData,
  prevMonth,
  nextMonth,
  isToday
} = useCalendarGrid()
</script>

<template>
  <div class="month-calendar">
    <div class="calendar-nav">
      <button class="nav-btn" @click="prevMonth">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12">
          <polyline points="15,18 9,12 15,6" />
        </svg>
      </button>
      <span class="calendar-title">{{ monthYear }}</span>
      <button class="nav-btn" @click="nextMonth">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12">
          <polyline points="9,6 15,12 9,18" />
        </svg>
      </button>
    </div>
    <div class="calendar-day-names">
      <span v-for="day in dayNames" :key="day.short" class="day-name">{{ day.short }}</span>
    </div>
    <div class="calendar-grid">
      <div
        v-for="day in monthData"
        :key="day.date.toISOString()"
        class="calendar-day"
        :class="{ 'other-month': day.date.getMonth() !== currentDate.getMonth(), 'is-today': isToday(day.date) }"
      >{{ day.date.getDate() }}</div>
    </div>
  </div>
</template>

<style scoped>
.month-calendar {
  background: var(--bg);
  border: 3px solid var(--border);
  border-radius: var(--radius);
  padding: 12px;
}

.calendar-nav {
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
}

.nav-btn:hover {
  background: var(--surface-hover);
  color: var(--fg);
}

.calendar-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--fg);
}

.calendar-day-names {
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

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
}

.calendar-day {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: var(--fg);
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.15s;
}

.calendar-day:hover {
  background: var(--surface);
}

.calendar-day.is-today {
  background: var(--accent);
  color: var(--bg);
  font-weight: 600;
}

.calendar-day.other-month {
  color: var(--border);
}
</style>
