<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import AppShell from '@/components/layout/AppShell.vue'
import Sidebar from '@/components/layout/Sidebar.vue'
import CalendarViewSwitch from '@/components/features/CalendarViewSwitch.vue'
import CalendarNav from '@/components/features/CalendarNav.vue'
import CalendarMonthView from '@/components/features/CalendarMonthView.vue'
import CalendarWeekView from '@/components/features/CalendarWeekView.vue'
import CalendarDayView from '@/components/features/CalendarDayView.vue'
import CalendarListView from '@/components/features/CalendarListView.vue'
import CreateCalendarModal from '@/components/features/CreateCalendarModal.vue'
import CreateAllocationModal from '@/components/features/CreateAllocationModal.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import { useCalendarsStore } from '@/stores/calendarsStore'
import { useDaysStore } from '@/stores/daysStore'
import { useTaskExecutionsStore } from '@/stores/taskExecutionsStore'
import { useTasksStore } from '@/stores/tasksStore'
import { useUiStore } from '@/stores/uiStore'
import { Task } from '@/domain/Task'

import type { UpdateExecutionData } from '@/types/api'

type CalendarViewType = 'day' | 'three_days' | 'work_week' | 'week' | 'month'

function formatLocalDate(date: Date): string {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function parseLocalDate(value: string): Date {
  const [y, m, d] = value.split('-').map(Number)
  return new Date(y, (m ?? 1) - 1, d ?? 1)
}

const { t } = useI18n()
const calendarsStore = useCalendarsStore()
const daysStore = useDaysStore()
const executionsStore = useTaskExecutionsStore()
const tasksStore = useTasksStore()
const uiStore = useUiStore()

// View state
const currentView = ref<CalendarViewType>(uiStore.calendarView)
const focusDate = ref(parseLocalDate(uiStore.calendarFocusDate))
const listMode = ref(uiStore.calendarListMode)

// Modals state
const showCreateCalendarModal = ref(false)
const showCreateAllocationModal = ref(false)
const selectedCalendarIdForAllocation = ref<number | null>(null)

// Fetch tasks for task execution display
const { data: tasksData } = tasksStore.useTasksQuery()
const tasks = computed(() => tasksData.value || [])

// Create task lookup map
const taskMap = computed(() => {
  const map = new Map<number, Task>()
  tasks.value.forEach(task => map.set(task.id, task))
  return map
})

// Selected allocation
const selectedAllocationId = computed(() => calendarsStore.selectedAllocationId)
const selectedAllocation = computed(() => calendarsStore.selectedAllocation)

// Calculate date range based on view and offset
function startOfWeek(base: Date): Date {
  const d = new Date(base)
  const dayOfWeek = d.getDay()
  const mondayOffset = (dayOfWeek + 6) % 7
  d.setDate(d.getDate() - mondayOffset)
  d.setHours(0, 0, 0, 0)
  return d
}

function getDateRange(baseDate: Date, view: CalendarViewType): { startDate: string; endDate: string } {
  const base = new Date(baseDate)
  base.setHours(0, 0, 0, 0)
  let startDate: Date
  let endDate: Date

  if (view === 'month') {
    const targetMonth = new Date(base.getFullYear(), base.getMonth(), 1)
    startDate = new Date(targetMonth.getFullYear(), targetMonth.getMonth(), 1)
    const dayOfWeek = startDate.getDay()
    startDate = new Date(startDate.getFullYear(), startDate.getMonth(), 1 - ((dayOfWeek + 6) % 7))
    endDate = new Date(startDate.getFullYear(), startDate.getMonth() + 1, 0)
    const endDayOfWeek = endDate.getDay()
    endDate = new Date(endDate.getFullYear(), endDate.getMonth(), endDate.getDate() + (6 - endDayOfWeek + 7) % 7)
  } else if (view === 'week') {
    startDate = startOfWeek(base)
    endDate = new Date(startDate)
    endDate.setDate(startDate.getDate() + 6)
  } else if (view === 'work_week') {
    startDate = startOfWeek(base)
    endDate = new Date(startDate)
    endDate.setDate(startDate.getDate() + 4)
  } else if (view === 'three_days') {
    startDate = new Date(base)
    endDate = new Date(startDate)
    endDate.setDate(startDate.getDate() + 2)
  } else {
    startDate = new Date(base)
    endDate = new Date(startDate)
  }

  return {
    startDate: startDate.toISOString().split('T')[0],
    endDate: endDate.toISOString().split('T')[0]
  }
}

const dateRange = computed(() => getDateRange(focusDate.value, currentView.value))
const activeCalendarId = computed(
  () => selectedAllocation.value?.calendarId || calendarsStore.selectedAllocationCalendarId || null,
)

const startDateRef = computed(() => dateRange.value.startDate)
const endDateRef = computed(() => dateRange.value.endDate)

// Fetch days and executions with Vue Query
const { data: daysData, isLoading: isLoadingDays } = daysStore.useDaysQuery(
  activeCalendarId,
  startDateRef,
  endDateRef
)

const { data: executionsData, isLoading: isLoadingExecutions } = executionsStore.useExecutionsQuery(selectedAllocationId)

const currentDays = computed(() => daysData.value || [])
const currentExecutions = computed(() => executionsData.value || [])

const updateExecutionMutation = executionsStore.useUpdateExecutionMutation()
const updateDayWorkHoursMutation = daysStore.useUpdateDayWorkHoursMutation()

// Period label for navigation
const periodLabel = computed(() => {
  const { startDate, endDate } = dateRange.value
  const start = new Date(startDate + 'T00:00:00')
  const end = new Date(endDate + 'T00:00:00')

  if (currentView.value === 'day') {
    return start.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })
  } else if (currentView.value === 'week' || currentView.value === 'work_week' || currentView.value === 'three_days') {
    return `${start.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${end.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`
  } else {
    return start.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
  }
})

// Build calendar data from days and executions
const calendarData = computed(() => {
  return currentDays.value.map(day => {
    // Get executions for this day
    const dayExecutions = currentExecutions.value.filter(e => e.day_id === day.id)

    return {
      date: new Date(day.date + 'T00:00:00'),
      day,
      executions: dayExecutions.map(exec => ({
        ...exec,
        task: taskMap.value.get(exec.task_id)
      }))
    }
  })
})

// Navigation handlers
function handlePrev() {
  const d = new Date(focusDate.value)
  if (currentView.value === 'day') d.setDate(d.getDate() - 1)
  if (currentView.value === 'week' || currentView.value === 'work_week' || currentView.value === 'three_days') d.setDate(d.getDate() - 7)
  if (currentView.value === 'month') d.setMonth(d.getMonth() - 1)
  focusDate.value = d
  uiStore.calendarFocusDate = formatLocalDate(d)
}

function handleNext() {
  const d = new Date(focusDate.value)
  if (currentView.value === 'day') d.setDate(d.getDate() + 1)
  if (currentView.value === 'week' || currentView.value === 'work_week' || currentView.value === 'three_days') d.setDate(d.getDate() + 7)
  if (currentView.value === 'month') d.setMonth(d.getMonth() + 1)
  focusDate.value = d
  uiStore.calendarFocusDate = formatLocalDate(d)
}

function handleViewChange(view: CalendarViewType) {
  currentView.value = view
  uiStore.calendarView = view
}

function handleListModeChange(value: boolean) {
  listMode.value = value
  uiStore.calendarListMode = value
}

// Convert selected date from mini calendar to offset
function handleDateSelect(date: Date) {
  const selected = new Date(date)
  selected.setHours(0, 0, 0, 0)
  focusDate.value = selected
  uiStore.calendarFocusDate = formatLocalDate(selected)
}

// Get selected date for mini calendar display
const selectedDate = computed(() => {
  return new Date(focusDate.value)
})

const selectedRange = computed(() => {
  const { startDate, endDate } = dateRange.value
  return {
    start: new Date(`${startDate}T00:00:00`),
    end: new Date(`${endDate}T00:00:00`),
  }
})

// Update execution (is_done toggle or doing_hours change)
function handleExecutionUpdate(executionId: number, data: UpdateExecutionData) {
  updateExecutionMutation.mutate({ executionId, data })
}

// Update day work_hours
function handleWorkHoursUpdate(dayId: number, workHours: number) {
  updateDayWorkHoursMutation.mutate({ dayId, workHours })
}

// Modal handlers
function handleCreateCalendar() {
  showCreateCalendarModal.value = true
}

function handleCreateAllocation(calendarId: number) {
  selectedCalendarIdForAllocation.value = calendarId
  showCreateAllocationModal.value = true
}

function handleCalendarCreated() {
  showCreateCalendarModal.value = false
}

function handleAllocationCreated() {
  showCreateAllocationModal.value = false
  selectedCalendarIdForAllocation.value = null
}

// Is loading state
const isLoading = computed(() => isLoadingDays.value || isLoadingExecutions.value)
</script>

<template>
  <AppShell>
    <template #sidebar>
      <Sidebar
        view-type="calendar"
        :selected-date="selectedDate"
        :selected-range-start="selectedRange.start"
        :selected-range-end="selectedRange.end"
        :calendar-period-label="periodLabel"
        @create-calendar="handleCreateCalendar"
        @create-allocation="handleCreateAllocation"
        @date-select="handleDateSelect"
        @prev-period="handlePrev"
        @next-period="handleNext"
      />
    </template>

    <template #top>
      <div class="calendar-header-wrapper">
        <div class="header-left">
          <CalendarViewSwitch
            :model-value="currentView"
            :list-mode="listMode"
            @update:model-value="handleViewChange"
            @update:list-mode="handleListModeChange"
          />
        </div>
        <CalendarNav
          :period="periodLabel"
          :offset="0"
          @prev="handlePrev"
          @next="handleNext"
        />
      </div>
    </template>

    <div class="calendar-view">
      <!-- Main calendar area -->
      <main class="calendar-main">
        <!-- No allocation selected -->
        <EmptyState
          v-if="!selectedAllocationId"
          variant="empty"
          :title="t('calendar.selectAllocation')"
          :message="t('calendar.selectAllocationHint')"
        />

        <!-- Calendar content -->
        <template v-else>
          <!-- Loading state -->
          <div
            v-if="isLoading"
            class="calendar-loading"
          >
            <span>{{ t('common.loading') }}...</span>
          </div>

          <!-- Calendar views -->
          <div
            v-else
            class="calendar-content"
          >
            <CalendarListView
              v-if="listMode"
              :list-data="calendarData"
            />

            <CalendarMonthView
              v-else-if="currentView === 'month'"
              :month-data="calendarData"
              @work-hours-change="handleWorkHoursUpdate"
              @execution-click="(exec) => handleExecutionUpdate(exec.id, { is_done: !exec.is_done })"
            />

            <CalendarWeekView
              v-else-if="currentView === 'week' || currentView === 'work_week' || currentView === 'three_days'"
              :week-data="calendarData"
              @work-hours-change="handleWorkHoursUpdate"
              @execution-click="(exec) => handleExecutionUpdate(exec.id, { is_done: !exec.is_done })"
            />

            <CalendarDayView
              v-else
              :day-data="calendarData[0]"
              @work-hours-change="handleWorkHoursUpdate"
              @execution-update="handleExecutionUpdate"
              @execution-click="() => {}"
            />
          </div>
        </template>
      </main>
    </div>

    <!-- Create Calendar Modal -->
    <CreateCalendarModal
      v-model:open="showCreateCalendarModal"
      @created="handleCalendarCreated"
    />

    <!-- Create Allocation Modal -->
    <CreateAllocationModal
      v-if="selectedCalendarIdForAllocation"
      v-model:open="showCreateAllocationModal"
      :calendar-id="selectedCalendarIdForAllocation"
      @created="handleAllocationCreated"
    />
  </AppShell>
</template>

<style scoped>
.calendar-view {
  display: flex;
  height: 100%;
  padding: 20px;
}

.calendar-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.calendar-header-wrapper {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 0 8px 16px;
  gap: 12px;
  border-bottom: 3px solid var(--border);
}

.mini-calendar-container {
  padding: 16px 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.calendar-loading {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--muted);
  font-size: 16px;
}

.calendar-content {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}
</style>
