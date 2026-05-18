<script setup lang="ts">
interface Props {
  placeholder?: string
  modelValue?: string
}

withDefaults(defineProps<Props>(), {
  placeholder: '',
  modelValue: '',
})

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<template>
  <textarea
    :placeholder="placeholder"
    :value="modelValue"
    class="base-textarea"
    @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
  />
</template>

<style scoped>
.base-textarea {
  width: 100%;
  min-height: 90px;
  background: var(--bg);
  color: var(--fg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 10px;
  font: inherit;
  resize: vertical;
}

.base-textarea::placeholder {
  color: var(--muted);
}

.base-textarea:focus {
  outline: none;
}
</style>
