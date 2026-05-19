<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import EmptyState from '@/components/ui/EmptyState.vue'
import CalendarHierarchyAllocations from './CalendarHierarchyAllocations.vue'
import { useCalendarsStore } from '@/stores/calendarsStore'

const { t } = useI18n()
const calendarsStore = useCalendarsStore()

const { data: calendarsData, isLoading: isLoadingCalendars } = calendarsStore.useCalendarsQuery()

// Computed: calendars from store
const calendars = computed(() => calendarsData.value || [])
const selectedCalendarId = computed(() => calendarsStore.selectedCalendarId)
const expandedCalendarId = computed(() => calendarsStore.expandedCalendarId)
const selectedAllocationId = computed(() => calendarsStore.selectedAllocationId)
const isLoading = computed(() => isLoadingCalendars.value)

// Toggle calendar expand
function toggleCalendarExpand(calendarId: number) {
  calendarsStore.selectCalendar(calendarId)
  calendarsStore.selectAllocation(null)
  calendarsStore.toggleCalendar(calendarId)
}

// Check if calendar is expanded
function isCalendarExpanded(calendarId: number): boolean {
  return expandedCalendarId.value === calendarId
}

// Handle create allocation button click
function handleCreateAllocation(calendarId: number) {
  emit('create-allocation', calendarId)
}

const emit = defineEmits<{
  'create-calendar': []
  'create-allocation': [calendarId: number]
}>()
</script>

<template>
  <div class="calendar-hierarchy">
    <!-- Loading state -->
    <EmptyState
      v-if="isLoading"
      variant="loading"
      :title="t('common.loading')"
    />

    <!-- Empty state -->
    <div v-else-if="calendars.length === 0" class="hierarchy-empty">
      <p>{{ t('calendar.noCalendarsYet') }}</p>
      <p class="empty-hint">{{ t('calendar.emptyHint') }}</p>
    </div>

    <!-- Calendar list -->
    <div v-else class="calendar-list">
      <div
        v-for="calendar in calendars"
        :key="calendar.id"
        class="calendar-item"
      >
        <!-- Calendar row (expandable) -->
        <div
          class="calendar-row"
          :class="{
            'is-expanded': isCalendarExpanded(calendar.id),
            'is-selected': selectedCalendarId === calendar.id && !selectedAllocationId
          }"
          @click="toggleCalendarExpand(calendar.id)"
        >
          <!-- Expand/collapse chevron -->
          <span class="calendar-chevron" :class="{ rotated: isCalendarExpanded(calendar.id) }">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="9,6 15,12 9,18" />
            </svg>
          </span>

          <!-- Calendar icon -->
          <svg class="calendar-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
            <line x1="16" y1="2" x2="16" y2="6" />
            <line x1="8" y1="2" x2="8" y2="6" />
            <line x1="3" y1="10" x2="21" y2="10" />
          </svg>

          <!-- Calendar name -->
          <span class="calendar-name">{{ calendar.name }}</span>
        </div>

        <!-- Allocations section (shown when expanded) -->
        <div v-if="isCalendarExpanded(calendar.id)" class="allocations-section">
          <!-- Allocations list -->
          <CalendarHierarchyAllocations :calendar-id="calendar.id" />

          <!-- Create allocation button -->
          <button
            class="create-allocation-btn"
            type="button"
            @click.stop="handleCreateAllocation(calendar.id)"
          >
            + {{ t('allocation.create') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.calendar-hierarchy {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.hierarchy-header {
  padding-bottom: 8px;
  border-bottom: 3px solid var(--border);
}

.hierarchy-empty {
  padding: 24px 16px;
  text-align: center;
  color: var(--muted);
  font-size: 14px;
}

.empty-hint {
  font-size: 13px;
  opacity: 0.8;
  margin-top: 4px;
}

.calendar-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.calendar-item {
  display: flex;
  flex-direction: column;
}

.calendar-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: var(--surface);
  border: 3px solid var(--border);
  border-radius: var(--radius);
  cursor: pointer;
  transition: background-color 0.15s, border-color 0.15s;
  user-select: none;
}

.calendar-row:hover {
  background: var(--surface-hover);
  border-color: var(--accent);
}

.calendar-row.is-expanded {
  border-color: var(--accent);
}

.calendar-row.is-selected {
  background: var(--surface-hover);
  border-color: var(--accent);
}

.calendar-chevron {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--muted);
  transition: transform 0.15s;
}

.calendar-chevron.rotated {
  transform: rotate(90deg);
}

.calendar-icon {
  color: var(--muted);
  flex-shrink: 0;
}

.calendar-name {
  font-size: 14px;
  color: var(--fg);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.allocations-section {
  padding: 8px 12px 12px;
  background: var(--surface);
  border: 3px solid var(--border);
  border-radius: var(--radius);
  margin-top: 6px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.create-allocation-btn {
  display: block;
  width: 100%;
  padding: 7px 10px;
  background: var(--surface);
  border: 3px solid var(--border);
  border-radius: 6px;
  color: var(--fg);
  font-size: 12px;
  font-weight: 600;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.15;
}

.create-allocation-btn:hover {
  background: var(--surface-hover);
  border-color: var(--accent);
  color: var(--fg);
}
</style>
