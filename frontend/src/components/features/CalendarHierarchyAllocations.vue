<script setup lang="ts">
import { computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCalendarsStore } from '@/stores/calendarsStore'
import { Allocation } from '@/domain/Calendar'

const props = defineProps<{
  calendarId: number
}>()

const calendarsStore = useCalendarsStore()
const { t } = useI18n()

const { data, isLoading } = calendarsStore.useAllocationsQuery(props.calendarId)
const allocations = computed(() => data.value || [])
const selectedAllocationId = computed(() => calendarsStore.selectedAllocationId)

function selectAllocation(allocation: Allocation) {
  calendarsStore.selectCalendar(null)
  calendarsStore.selectAllocation(allocation)
}

function handleActionClick(allocation: Allocation) {
  selectAllocation(allocation)
}

watch(
  allocations,
  (items) => {
    if (!items.length || !selectedAllocationId.value || calendarsStore.selectedAllocation) return
    const match = items.find(item => item.id === selectedAllocationId.value)
    if (match) {
      calendarsStore.selectAllocation(match)
    }
  },
  { immediate: true },
)
</script>

<template>
  <div v-if="isLoading" class="loading-state">
    <span class="loader"></span>
  </div>
  <div v-else-if="allocations.length === 0" class="no-allocations">{{ t('allocation.empty') }}</div>
  <div v-else class="allocations-list">
    <div
      v-for="allocation in allocations"
      :key="allocation.id"
      class="allocation-item"
      :class="{ 'is-selected': selectedAllocationId === allocation.id }"
      @click.stop="selectAllocation(allocation)"
    >
      <span class="allocation-name">{{ allocation.name }}</span>
      <button
        class="allocation-action-btn"
        type="button"
        :title="t('common.select')"
        @click.stop="handleActionClick(allocation)"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" aria-hidden="true">
          <path d="M9 18l6-6-6-6" />
        </svg>
      </button>
    </div>
  </div>
</template>

<style scoped>
.loading-state {
  padding: 8px 16px;
  display: flex;
  justify-content: center;
}
.no-allocations {
  padding: 8px 16px;
  font-size: 12px;
  color: var(--muted);
}
.allocations-list {
  display: flex;
  flex-direction: column;
  width: 100%;
  gap: 6px;
}
.allocation-item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 8px 10px;
  font-size: 13px;
  color: var(--muted);
  cursor: pointer;
  transition: all 0.2s ease;
  border: 3px solid var(--border);
  border-radius: 6px;
  background: color-mix(in oklab, var(--surface) 92%, black 8%);
}
.allocation-item:hover {
  background-color: var(--surface-hover);
  color: var(--fg);
}
.allocation-item.is-selected {
  background-color: var(--surface-hover);
  color: var(--fg);
  font-weight: 500;
  border-color: var(--accent);
  box-shadow: inset 0 0 0 1px color-mix(in oklab, var(--accent) 40%, transparent);
}

.allocation-name {
  display: block;
  flex: 1;
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.allocation-action-btn {
  width: 24px;
  height: 24px;
  border: 3px solid var(--border);
  border-radius: 6px;
  background: var(--surface);
  color: var(--fg);
  font-size: 14px;
  line-height: 1;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.allocation-action-btn:hover {
  border-color: var(--accent);
  background: var(--surface-hover);
}
</style>
