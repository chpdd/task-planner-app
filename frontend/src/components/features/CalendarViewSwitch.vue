<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

export type CalendarView = 'day' | 'three_days' | 'work_week' | 'week' | 'month'

const { t } = useI18n()

interface Props {
  modelValue: CalendarView
  listMode?: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: CalendarView]
  'update:listMode': [value: boolean]
}>()

const isOpen = ref(false)

const modes = computed(() => ([
  { value: 'day' as const, label: t('calendar.day') },
  { value: 'three_days' as const, label: t('calendar.threeDays') },
  { value: 'work_week' as const, label: t('calendar.workWeek') },
  { value: 'week' as const, label: t('calendar.week') },
  { value: 'month' as const, label: t('calendar.month') },
]))

const currentLabel = computed(() => modes.value.find(m => m.value === props.modelValue)?.label ?? t('calendar.view'))

function selectTab(value: CalendarView) {
  emit('update:modelValue', value)
  isOpen.value = false
}

function toggleList() {
  emit('update:listMode', !props.listMode)
}
</script>

<template>
  <div class="view-switch">
    <div class="dropdown">
      <button class="view-trigger" type="button" @click="isOpen = !isOpen">
        {{ t('calendar.view') }}: {{ currentLabel }}
        <span class="chevron" :class="{ open: isOpen }">▾</span>
      </button>
      <div v-if="isOpen" class="dropdown-menu">
        <button
          v-for="mode in modes"
          :key="mode.value"
          class="dropdown-item"
          :class="{ active: modelValue === mode.value }"
          type="button"
          @click="selectTab(mode.value)"
        >
          {{ mode.label }}
        </button>
      </div>
    </div>
      <button class="list-toggle" :class="{ active: listMode }" type="button" @click="toggleList">
      {{ t('calendar.list') }}
    </button>
  </div>
</template>

<style scoped>
.view-switch {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.dropdown {
  position: relative;
}

.view-trigger,
.list-toggle,
.dropdown-item {
  border: 3px solid var(--border);
  background: var(--surface);
  color: var(--fg);
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 14px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  min-width: 180px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  background: var(--surface);
  border: 3px solid var(--border);
  border-radius: 10px;
  padding: 6px;
  z-index: 10;
}

.dropdown-item {
  text-align: left;
}

.dropdown-item.active,
.list-toggle.active {
  background: var(--accent);
  color: var(--bg);
  border-color: var(--accent);
}

.chevron {
  transition: transform 0.15s ease;
}

.chevron.open {
  transform: rotate(180deg);
}
</style>
