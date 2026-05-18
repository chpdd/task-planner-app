<script setup lang="ts">
import { useId } from 'vue'
import {
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogOverlay,
  DialogPortal,
  DialogRoot,
  DialogTitle,
  useForwardPropsEmits,
} from 'reka-ui'
import type { DialogContentEmits, DialogContentProps } from 'reka-ui'

const props = defineProps<DialogContentProps & { open?: boolean; title?: string; description?: string }>()
const emits = defineEmits<DialogContentEmits & { 'update:open': [value: boolean] }>()

const descriptionId = useId()
const forwarded = useForwardPropsEmits(props, emits)
</script>

<template>
  <DialogRoot :open="open" @update:open="emits('update:open', $event)">
    <DialogPortal>
      <DialogOverlay class="modal-overlay" />
      <DialogContent
        v-bind="forwarded"
        :aria-describedby="descriptionId"
        class="modal-content"
      >
        <DialogTitle v-if="title || $slots.title" class="modal-title">
          <slot name="title">{{ title }}</slot>
        </DialogTitle>
        <DialogDescription :id="descriptionId" class="modal-description">
          <slot name="description">{{ description }}</slot>
        </DialogDescription>

        <div class="modal-body">
          <slot />
        </div>

        <div v-if="$slots.actions" class="modal-actions">
          <slot name="actions" />
        </div>

        <DialogClose class="modal-close" aria-label="Close">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </DialogClose>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 50;
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: min(580px, calc(100vw - 30px));
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
  z-index: 51;
  max-height: calc(100vh - 60px);
  overflow-y: auto;
}

.modal-title {
  font-size: 20px;
  font-weight: 500;
  margin-bottom: 12px;
  padding-right: 28px;
}

.modal-description {
  color: var(--muted);
  margin-bottom: 12px;
}

.modal-body {
  margin-bottom: 12px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: var(--muted);
  border-radius: 6px;
  cursor: pointer;
  transition: color 0.15s, background 0.15s;
}

.modal-close:hover {
  color: var(--fg);
  background: var(--surface-hover);
}
</style>
