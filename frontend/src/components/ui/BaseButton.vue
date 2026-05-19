<script setup lang="ts">
interface Props {
  variant?: 'default' | 'primary'
  size?: 'default' | 'small'
  disabled?: boolean
  type?: 'button' | 'submit' | 'reset'
}

withDefaults(defineProps<Props>(), {
  variant: 'default',
  size: 'default',
  disabled: false,
  type: 'button',
})
</script>

<template>
  <button
    :type="type"
    :disabled="disabled"
    :class="[
      'btn',
      {
        'btn-primary': variant === 'primary',
        'btn-small': size === 'small',
      },
    ]"
  >
    <slot />
  </button>
</template>

<style scoped>
.btn {
  border: 3px solid var(--border);
  background: var(--surface);
  color: var(--fg);
  border-radius: var(--radius);
  padding: 10px 14px;
  cursor: pointer;
  font-size: 14px;
  font-family: inherit;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: background-color 0.15s, box-shadow 0.15s;
}

.btn:hover:not(:disabled) {
  background: var(--surface-hover);
  box-shadow: 0 0 0 1px var(--accent);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--accent);
  color: #141414;
  border-color: transparent;
}

.btn-primary:hover:not(:disabled) {
  background: var(--accent);
  opacity: 0.9;
  box-shadow: 0 0 0 1px var(--accent);
}

.btn-small {
  padding: 6px 10px;
  font-size: 13px;
}
</style>
