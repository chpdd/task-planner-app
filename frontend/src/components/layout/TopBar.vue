<script setup lang="ts">
defineProps<{
  activeTab?: string
}>()

defineEmits<{
  'update:activeTab': [value: string]
}>()
</script>

<template>
  <header class="top">
    <slot name="tabs" />
    <div class="top-actions">
      <slot name="actions" />
    </div>
  </header>
</template>
