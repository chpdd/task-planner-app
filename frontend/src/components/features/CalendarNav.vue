<script setup lang="ts">
interface Props {
  period: string
  offset?: number
}

withDefaults(defineProps<Props>(), {
  offset: 0,
})

const emit = defineEmits<{
  prev: []
  next: []
}>()
</script>

<template>
  <div class="calendar-nav">
    <button
      type="button"
      class="nav-arrow"
      aria-label="Previous period"
      @click="emit('prev')"
    >
      &#8592;
    </button>

    <span class="calendar-period">{{ period }}</span>

    <button
      type="button"
      class="nav-arrow"
      aria-label="Next period"
      @click="emit('next')"
    >
      &#8594;
    </button>
  </div>
</template>

<style scoped>
.calendar-nav {
  display: flex;
  align-items: center;
  gap: 12px;
}

.nav-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--muted);
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.15s, color 0.15s;
}

.nav-arrow:hover {
  background: var(--surface-hover);
  color: var(--fg);
}

.calendar-period {
  min-width: 170px;
  text-align: center;
  font-size: 16px;
  font-weight: 500;
  color: var(--fg);
}
</style>
