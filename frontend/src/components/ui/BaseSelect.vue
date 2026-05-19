<script setup lang="ts">
interface Option {
  value: string | number
  label: string
}

interface Props {
  modelValue?: string | number
  options?: Option[]
  placeholder?: string
}

withDefaults(defineProps<Props>(), {
  modelValue: '',
  options: () => [],
  placeholder: '',
})

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<template>
  <div class="base-select-wrapper">
    <select
      :value="modelValue"
      class="base-select"
      @change="$emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
    >
      <option v-if="placeholder" value="" disabled>{{ placeholder }}</option>
      <option
        v-for="option in options"
        :key="option.value"
        :value="option.value"
      >
        {{ option.label }}
      </option>
    </select>
    <svg
      class="base-select-arrow"
      xmlns="http://www.w3.org/2000/svg"
      width="12"
      height="12"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      <polyline points="6 9 12 15 18 9" />
    </svg>
  </div>
</template>

<style scoped>
.base-select-wrapper {
  position: relative;
  width: 100%;
}

.base-select {
  width: 100%;
  background: var(--bg);
  color: var(--fg);
  border: 3px solid var(--border);
  border-radius: var(--radius);
  padding: 10px;
  padding-right: 32px;
  font: inherit;
  appearance: none;
  cursor: pointer;
}

.base-select::placeholder {
  color: var(--muted);
}

.base-select:focus {
  outline: none;
}

.base-select-arrow {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--muted);
  pointer-events: none;
}
</style>
