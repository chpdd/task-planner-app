<script setup lang="ts">
interface Props {
  title: string
  message?: string
  icon?: string
  actionLabel?: string
  variant?: 'empty' | 'error' | 'loading'
}

withDefaults(defineProps<Props>(), {
  message: '',
  icon: '',
  actionLabel: '',
  variant: 'empty',
})

const emit = defineEmits<{
  retry: []
}>()
</script>

<template>
  <div class="empty-state" :class="[`empty-state--${variant}`]">
    <div class="empty-state__icon">
      <span v-if="icon">{{ icon }}</span>
      
      <svg v-else-if="variant === 'error'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="48" height="48">
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" />
        <line x1="12" y1="16" x2="12.01" y2="16" />
      </svg>
      
      <svg v-else-if="variant === 'loading'" class="spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="48" height="48">
        <path d="M21 12a9 9 0 1 1-6.219-8.56" />
      </svg>
      
      <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="48" height="48">
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
        <line x1="9" y1="9" x2="15" y2="9" />
        <line x1="9" y1="13" x2="15" y2="13" />
        <line x1="9" y1="17" x2="15" y2="17" />
      </svg>
    </div>
    <h3 class="empty-state__title">{{ title }}</h3>
    <p v-if="message" class="empty-state__message">{{ message }}</p>
    <button
      v-if="variant === 'error' && actionLabel"
      class="empty-state__action"
      @click="emit('retry')"
    >
      {{ actionLabel }}
    </button>
  </div>
</template>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
  min-height: 200px;
}

.empty-state__icon {
  margin-bottom: 16px;
  opacity: 0.7;
  color: var(--muted);
}

.empty-state__title {
  font-size: 18px;
  font-weight: 600;
  color: var(--fg);
  margin: 0 0 8px 0;
}

.empty-state__message {
  font-size: 14px;
  color: var(--muted);
  margin: 0 0 16px 0;
  max-width: 320px;
}

.empty-state__action {
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--fg);
  border-radius: var(--radius);
  padding: 10px 14px;
  cursor: pointer;
  font-size: 14px;
  font-family: inherit;
  transition: background-color 0.15s, box-shadow 0.15s;
}

.empty-state__action:hover {
  background: var(--surface-hover);
  box-shadow: 0 0 0 1px var(--accent);
}

.empty-state--error .empty-state__icon {
  color: var(--danger);
}

.empty-state--loading .empty-state__icon {
  color: var(--accent);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
