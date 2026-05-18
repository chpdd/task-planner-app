<script setup lang="ts">
import { ToastRoot, ToastProvider, ToastTitle, ToastViewport } from 'radix-vue'

export type ToastType = 'success' | 'error' | 'info'

interface Toast {
  id: string
  type: ToastType
  message: string
}

defineProps<{
  toasts: Toast[]
}>()
</script>

<template>
  <ToastProvider>
    <div class="toast-container">
      <ToastRoot
        v-for="toast in toasts"
        :key="toast.id"
        :class="['toast', `toast--${toast.type}`]"
        :duration="4000"
      >
        <div class="toast__icon">
          <span v-if="toast.type === 'success'">✓</span>
          <span v-else-if="toast.type === 'error'">✕</span>
          <span v-else>i</span>
        </div>
        <div class="toast__content">
          <ToastTitle class="toast__title">
            {{ toast.type === 'success' ? 'Success' : toast.type === 'error' ? 'Error' : 'Info' }}
          </ToastTitle>
          <p class="toast__message">{{ toast.message }}</p>
        </div>
      </ToastRoot>
    </div>
    <ToastViewport class="toast-viewport" />
  </ToastProvider>
</template>

<style scoped>
.toast-container {
  position: fixed;
  bottom: var(--spacing-4, 1rem);
  right: var(--spacing-4, 1rem);
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3, 0.75rem);
  max-width: 400px;
  width: 100%;
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-3, 0.75rem);
  padding: var(--spacing-4, 1rem);
  background: var(--surface, oklch(20% 0.024 252));
  border: 1px solid var(--border, oklch(35% 0.018 240));
  border-radius: var(--radius, 10px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  pointer-events: auto;
  animation: toast-slide-in 0.2s ease-out;
}

.toast--success {
  border-left: 3px solid var(--accent, oklch(68% 0.14 40));
}

.toast--success .toast__icon {
  color: var(--accent, oklch(68% 0.14 40));
}

.toast--error {
  border-left: 3px solid var(--danger, oklch(61% 0.28 26));
}

.toast--error .toast__icon {
  color: var(--danger, oklch(61% 0.28 26));
}

.toast--info {
  border-left: 3px solid var(--fg, oklch(97% 0.012 80));
}

.toast--info .toast__icon {
  color: var(--fg, oklch(97% 0.012 80));
}

.toast__icon {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  border-radius: 50%;
  background: transparent;
}

.toast__content {
  flex: 1;
  min-width: 0;
}

.toast__title {
  font-size: 14px;
  font-weight: 600;
  color: var(--fg, oklch(97% 0.012 80));
  margin: 0 0 var(--spacing-1, 0.25rem) 0;
}

.toast__message {
  font-size: 13px;
  color: var(--muted, oklch(72% 0.01 240));
  margin: 0;
  line-height: 1.4;
}

.toast-viewport {
  position: fixed;
  bottom: var(--spacing-4, 1rem);
  right: var(--spacing-4, 1rem);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3, 0.75rem);
  width: 380px;
  max-width: calc(100vw - var(--spacing-8, 2rem));
  z-index: 9999;
  outline: none;
  pointer-events: none;
}

@keyframes toast-slide-in {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
</style>
