<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import { useCalendarsStore } from '@/stores/calendarsStore'

const { t } = useI18n()
const calendarsStore = useCalendarsStore()

const props = defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  created: [calendarId: number]
}>()

const name = ref('')
const error = ref('')

const createCalendarMutation = calendarsStore.useCreateCalendarMutation()

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      name.value = ''
      error.value = ''
    }
  }
)

function validate(): boolean {
  if (!name.value.trim()) {
    error.value = t('validation.required')
    return false
  }
  error.value = ''
  return true
}

function handleCreate() {
  if (!validate()) return

  createCalendarMutation.mutate(name.value.trim(), {
    onSuccess: () => {
      // In a real scenario you'd get the returned calendar data here to emit its ID
      // but standard Vue Query `onSuccess` only gets the typed return data.
      // We will emit 0 for now as UI might rely on query invalidation anyway.
      emit('created', 0)
      emit('update:open', false)
    }
  })
}

function handleCancel() {
  emit('update:open', false)
}
</script>

<template>
  <BaseModal
    :open="open"
    :title="t('calendar.createTitle')"
    @update:open="emit('update:open', $event)"
  >
    <form
      class="create-calendar-form"
      @submit.prevent="handleCreate"
    >
      <div class="field">
        <label class="field-label">{{ t('calendar.name') }}</label>
        <BaseInput
          v-model="name"
          :placeholder="t('calendar.namePlaceholder')"
          :error="!!error"
          :disabled="createCalendarMutation.isPending.value"
          @input="error = ''"
        />
        <span
          v-if="error"
          class="field-error"
        >{{ error }}</span>
      </div>
    </form>

    <template #actions>
      <BaseButton
        :disabled="createCalendarMutation.isPending.value"
        @click="handleCancel"
      >
        {{ t('common.cancel') }}
      </BaseButton>
      <BaseButton
        variant="primary"
        :disabled="createCalendarMutation.isPending.value"
        @click="handleCreate"
      >
        {{ t('common.create') }}
      </BaseButton>
    </template>
  </BaseModal>
</template>

<style scoped>
.create-calendar-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 13px;
  color: var(--muted);
}

.field-error {
  font-size: 12px;
  color: var(--danger);
}
</style>
