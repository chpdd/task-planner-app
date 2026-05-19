<script setup lang="ts">
export interface Tab {
  value: string
  label: string
}

interface Props {
  tabs: Tab[]
  modelValue: string
}

defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

function selectTab(value: string) {
  emit('update:modelValue', value)
}
</script>

<template>
  <div class="tabs" role="tablist">
    <button
      v-for="tab in tabs"
      :key="tab.value"
      role="tab"
      type="button"
      :aria-selected="modelValue === tab.value"
      :class="['tab', { active: modelValue === tab.value }]"
      @click="selectTab(tab.value)"
    >
      {{ tab.label }}
    </button>
  </div>
</template>

<style scoped>
.tabs {
  display: inline-flex;
  background: var(--surface);
  border: 3px solid var(--border);
  border-radius: 999px;
  padding: 4px;
}

.tab {
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

.tab:hover:not(.active) {
  color: var(--fg);
}

.tab.active {
  background: var(--bg);
  color: var(--fg);
  border: 3px solid var(--border);
}
</style>
