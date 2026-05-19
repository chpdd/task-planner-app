<script setup lang="ts">
interface Props {
  type?: string
  placeholder?: string
  modelValue?: string | number
  autocomplete?: string
  error?: boolean
}

withDefaults(defineProps<Props>(), {
  type: 'text',
  placeholder: '',
  modelValue: '',
  autocomplete: 'off',
  error: false,
})

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<template>
  <input
    :type="type"
    :placeholder="placeholder"
    :value="modelValue"
    :autocomplete="autocomplete"
    class="base-input"
    :class="{ 'base-input-error': error }"
    @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
  />
</template>

<style scoped>
.base-input {
  width: 100%;
  background: var(--bg);
  color: var(--fg);
  border: 3px solid var(--border);
  border-radius: var(--radius);
  padding: 10px;
  font: inherit;
}

.base-input::placeholder {
  color: var(--muted);
}

.base-input:focus {
  outline: none;
}

.base-input-error {
  border-color: var(--danger) !important;
}
</style>
