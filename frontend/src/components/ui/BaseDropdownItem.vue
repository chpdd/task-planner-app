<script setup lang="ts">
import { DropdownMenuItem } from 'reka-ui'

interface Props {
  destructive?: boolean
  disabled?: boolean
}

withDefaults(defineProps<Props>(), {
  destructive: false,
  disabled: false,
})

defineEmits<{
  select: []
}>()
</script>

<template>
  <DropdownMenuItem
    class="base-dropdown-item"
    :class="{ destructive }"
    :disabled="disabled"
    @select="$emit('select')"
  >
    <slot />
  </DropdownMenuItem>
</template>

<style>
.base-dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: calc(var(--radius) - 4px);
  font-size: 14px;
  color: var(--fg);
  cursor: pointer;
  outline: none;
  user-select: none;
}

.base-dropdown-item:focus,
.base-dropdown-item:hover {
  background: var(--surface-hover);
  color: var(--accent);
}

.base-dropdown-item.destructive {
  color: var(--danger);
}

.base-dropdown-item.destructive:focus,
.base-dropdown-item.destructive:hover {
  background: rgba(204, 77, 77, 0.1);
}

.base-dropdown-item[data-disabled] {
  opacity: 0.5;
  pointer-events: none;
}
</style>
