<script setup lang="ts">
import { computed } from 'vue'
import { useCalendarsStore } from '@/stores/calendarsStore'
import { Allocation } from '@/domain/Calendar'

const props = defineProps<{
  calendarId: number
}>()

const calendarsStore = useCalendarsStore()

const { data, isLoading } = calendarsStore.useAllocationsQuery(props.calendarId)
const allocations = computed(() => data.value || [])
const selectedAllocationId = computed(() => calendarsStore.selectedAllocationId)

function selectAllocation(allocation: Allocation) {
  calendarsStore.selectCalendar(null)
  calendarsStore.selectAllocation(allocation)
}
</script>

<template>
  <div v-if="isLoading" class="loading-state">
    <span class="loader"></span>
  </div>
  <div v-else-if="allocations.length === 0" class="no-allocations">
    No allocations found
  </div>
  <div v-else class="allocations-list">
    <div
      v-for="allocation in allocations"
      :key="allocation.id"
      class="allocation-item"
      :class="{ 'is-selected': selectedAllocationId === allocation.id }"
      @click.stop="selectAllocation(allocation)"
    >
      <span class="allocation-name">{{ allocation.name }}</span>
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
}
.allocation-item {
  padding: 8px 16px 8px 32px;
  font-size: 13px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
}
.allocation-item:hover {
  background-color: var(--surface-hover);
  color: var(--text);
}
.allocation-item.is-selected {
  background-color: var(--surface-active);
  color: var(--primary);
  font-weight: 500;
}
</style>
