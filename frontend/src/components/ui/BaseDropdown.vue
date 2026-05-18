<script setup lang="ts">
import {
  DropdownMenuRoot,
  DropdownMenuTrigger,
  DropdownMenuPortal,
  DropdownMenuContent,
} from 'reka-ui'

interface Props {
  align?: 'start' | 'center' | 'end'
  sideOffset?: number
}

withDefaults(defineProps<Props>(), {
  align: 'end',
  sideOffset: 5,
})
</script>

<template>
  <DropdownMenuRoot>
    <DropdownMenuTrigger class="base-dropdown-trigger" as-child>
      <slot name="trigger" />
    </DropdownMenuTrigger>

    <DropdownMenuPortal>
      <DropdownMenuContent
        class="base-dropdown-content"
        :align="align"
        :side-offset="sideOffset"
      >
        <slot />
      </DropdownMenuContent>
    </DropdownMenuPortal>
  </DropdownMenuRoot>
</template>

<style>
.base-dropdown-trigger {
  display: inline-flex;
  cursor: pointer;
  background: transparent;
  border: none;
  padding: 0;
  color: inherit;
}

.base-dropdown-trigger:focus {
  outline: none;
}

.base-dropdown-content {
  min-width: 160px;
  background: var(--surface, #2a2b2a) !important;
  border: 1px solid var(--border, #3d3e3d);
  border-radius: var(--radius, 8px);
  padding: 4px;
  z-index: 9999 !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);

  animation: dropdown-in 0.1s ease-out;
}

@keyframes dropdown-in {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
