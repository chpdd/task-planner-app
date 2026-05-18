<script setup lang="ts">
import { useI18n } from 'vue-i18n'

export type CalendarView = 'day' | 'week' | 'month'

const { t } = useI18n()

interface Props {
  modelValue: CalendarView
}

defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: CalendarView]
}>()

const tabs = [
  { value: 'day' as const, labelKey: 'calendar.day' },
  { value: 'week' as const, labelKey: 'calendar.week' },
  { value: 'month' as const, labelKey: 'calendar.month' },
]

function selectTab(value: CalendarView) {
  emit('update:modelValue', value)
}
</script>

<template>
  <div class="view-switch" role="tablist">
    <button
      v-for="tab in tabs"
      :key="tab.value"
      role="tab"
      type="button"
      :aria-selected="modelValue === tab.value"
      :class="['view-tab', { active: modelValue === tab.value }]"
      @click="selectTab(tab.value)"
    >
      {{ t(tab.labelKey) }}
    </button>
  </div>
</template>

<style scoped>
.view-switch {
  display: inline-flex;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 4px;
}

.view-tab {
  border: 0;
  background: transparent;
  color: var(--muted);
  padding: 7px 14px;
  border-radius: 999px;
  cursor: pointer;
  font-size: 14px;
  font-family: inherit;
  transition: background-color 0.15s, color 0.15s;
}

.view-tab:hover:not(.active) {
  color: var(--fg);
}

.view-tab.active {
  background: var(--bg);
  color: var(--fg);
  border: 1px solid var(--border);
}
</style>
