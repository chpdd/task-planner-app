<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import AppShell from '@/components/layout/AppShell.vue'
import CalendarHierarchy from '@/components/features/CalendarHierarchy.vue'
import CalendarViewSwitch from '@/components/features/CalendarViewSwitch.vue'
import CalendarNav from '@/components/features/CalendarNav.vue'
import CalendarMonthView from '@/components/features/CalendarMonthView.vue'
import CalendarWeekView from '@/components/features/CalendarWeekView.vue'
import CalendarDayView from '@/components/features/CalendarDayView.vue'
import MiniCalendar from '@/components/features/MiniCalendar.vue'
import CreateCalendarModal from '@/components/features/CreateCalendarModal.vue'
import CreateAllocationModal from '@/components/features/CreateAllocationModal.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import { useCalendarsStore } from '@/stores/calendarsStore'
import { useDaysStore } from '@/stores/daysStore'
import { useTaskExecutionsStore } from '@/stores/taskExecutionsStore'
import { useTasksStore } from '@/stores/tasksStore'
import { Task } from '@/domain/Task'

import type { UpdateExecutionData } from '@/types/api'

type CalendarViewType = 'day' | 'week' | 'month'

const { t } = useI18n()
const calendarsStore = useCalendarsStore()
const daysStore = useDaysStore()
const executionsStore = useTaskExecutionsStore()
const tasksStore = useTasksStore()

// View state
const currentView = ref<CalendarViewType>('week')
const calendarOffset = ref(0)

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
function getDateRange(offset: number, view: CalendarViewType): { startDate: string; endDate: string } {
  const today = new Date()
  let startDate: Date
  let endDate: Date

  if (view === 'month') {
    const targetMonth = new Date(today.getFullYear(), today.getMonth() + offset, 1)
    startDate = new Date(targetMonth.getFullYear(), targetMonth.getMonth(), 1)
    const dayOfWeek = startDate.getDay()
    startDate = new Date(startDate.getFullYear(), startDate.getMonth(), 1 - ((dayOfWeek + 6) % 7))
    endDate = new Date(startDate.getFullYear(), startDate.getMonth() + 1, 0)
    const endDayOfWeek = endDate.getDay()
    endDate = new Date(endDate.getFullYear(), endDate.getMonth(), endDate.getDate() + (6 - endDayOfWeek + 7) % 7)
  } else if (view === 'week') {
    const dayOfWeek = today.getDay()
    const mondayOffset = (dayOfWeek + 6) % 7
    startDate = new Date(today)
    startDate.setDate(today.getDate() - mondayOffset + offset * 7)
    endDate = new Date(startDate)
    endDate.setDate(startDate.getDate() + 6)
  } else {
    startDate = new Date(today)
    startDate.setDate(today.getDate() + offset)
    endDate = new Date(startDate)
  }

  return {
    startDate: startDate.toISOString().split('T')[0],
    endDate: endDate.toISOString().split('T')[0]
  }
}

const dateRange = computed(() => getDateRange(calendarOffset.value, currentView.value))
const activeCalendarId = computed(() => selectedAllocation.value?.calendarId || null)

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
  } else if (currentView.value === 'week') {
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
  calendarOffset.value -= 1
}

function handleNext() {
  calendarOffset.value += 1
}

function handleViewChange(view: CalendarViewType) {
  currentView.value = view
  calendarOffset.value = 0
}

// Convert selected date from mini calendar to offset
function handleDateSelect(date: Date) {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const selected = new Date(date)
  selected.setHours(0, 0, 0, 0)

  const diffTime = selected.getTime() - today.getTime()
  const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24))

  if (currentView.value === 'day') {
    calendarOffset.value = diffDays
  } else if (currentView.value === 'week') {
    // Convert to week offset (7 days = 1 week)
    calendarOffset.value = Math.round(diffDays / 7)
  } else {
    // Month view - calculate month difference
    const yearDiff = selected.getFullYear() - today.getFullYear()
    const monthDiff = selected.getMonth() - today.getMonth()
    calendarOffset.value = yearDiff * 12 + monthDiff
  }
}

// Get selected date for mini calendar display
const selectedDate = computed(() => {
  const { startDate } = dateRange.value
  return new Date(startDate + 'T00:00:00')
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
        @create-calendar="handleCreateCalendar"
        @create-allocation="handleCreateAllocation"
        @date-select="handleDateSelect"
      />
    </template>

    <template #top>
      <div class="calendar-header-wrapper">
        <div class="header-left">
          <CalendarViewSwitch
            :model-value="currentView"
            @update:model-value="handleViewChange"
          />
        </div>

        <CalendarNav
          :period="periodLabel"
          :offset="calendarOffset"
          @prev="handlePrev"
          @next="handleNext"
        />

        <div class="header-right">
        </div>
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
            <CalendarMonthView
              v-if="currentView === 'month'"
              :month-data="calendarData"
              @work-hours-change="handleWorkHoursUpdate"
              @execution-click="(exec) => handleExecutionUpdate(exec.id, { is_done: !exec.is_done })"
            />

            <CalendarWeekView
              v-else-if="currentView === 'week'"
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
  justify-content: space-between;
  padding: 0 8px 16px;
  gap: 24px;
  border-bottom: 1px solid var(--border);
}

.mini-calendar-container {
  padding: 16px 24px;
}

.header-left,
.header-right {
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
