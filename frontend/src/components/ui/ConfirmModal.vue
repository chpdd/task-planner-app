<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

defineProps<{
  open: boolean
  title?: string
  message: string
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  confirm: []
  cancel: []
}>()

const { t } = useI18n()

function handleConfirm() {
  emit('confirm')
  emit('update:open', false)
}

function handleCancel() {
  emit('cancel')
  emit('update:open', false)
}
</script>

<template>
  <BaseModal
    :open="open"
    :title="title || t('common.confirmTitle')"
    @update:open="emit('update:open', $event)"
  >
    <div class="confirm-message">
      {{ message }}
    </div>

    <template #actions>
      <BaseButton @click="handleCancel">
        {{ t('common.cancel') }}
      </BaseButton>
      <BaseButton
        variant="primary"
        class="destructive-btn"
        @click="handleConfirm"
      >
        {{ t('common.delete') }}
      </BaseButton>
    </template>
  </BaseModal>
</template>

<style scoped>
.confirm-message {
  font-size: 15px;
  line-height: 1.5;
  color: var(--fg);
  padding: 8px 0;
}

.destructive-btn {
  background: var(--danger) !important;
  color: white !important;
}

.destructive-btn:hover {
  filter: brightness(1.1);
}
</style>
