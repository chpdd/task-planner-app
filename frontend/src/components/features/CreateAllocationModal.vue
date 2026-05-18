<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseSelect from '@/components/ui/BaseSelect.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import { useCalendarsStore } from '@/stores/calendarsStore'
import type { AllocationType } from '@/types/api'

const { t } = useI18n()
const calendarsStore = useCalendarsStore()

const props = defineProps<{
  open: boolean
  calendarId: number
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  created: [allocationId: number]
}>()

const typeOptions = computed(() => [
  { value: 'even', label: t('allocation.types.even') },
  { value: 'priority', label: t('allocation.types.priority') },
  { value: 'compact', label: t('allocation.types.compact') },
])

const form = ref({
  name: '',
  type: 'even' as AllocationType,
})

const errorMessage = ref('')

// Counter for default names
const allocationCounter = ref(1)

const modalTitle = computed(() => t('allocation.create'))

const defaultName = computed(() => `${t('allocation.defaultName')} ${allocationCounter.value}`)

const createAllocationMutation = calendarsStore.useCreateAllocationMutation()
const applyAllocationMutation = calendarsStore.useApplyAllocationMutation()

const isPending = computed(() => createAllocationMutation.isPending.value || applyAllocationMutation.isPending.value)

function handleCancel() {
  if (!isPending.value) {
    emit('update:open', false)
    resetForm()
  }
}

function resetForm() {
  form.value = {
    name: '',
    type: 'even',
  }
  errorMessage.value = ''
}

function handleCreateAndApply() {
  if (isPending.value) return

  errorMessage.value = ''
  const name = form.value.name.trim() || defaultName.value

  createAllocationMutation.mutate(
    { calendarId: props.calendarId, name, type: form.value.type },
    {
      onSuccess: (allocation: any) => {
        if (allocation && allocation.id) {
          applyAllocationMutation.mutate(allocation.id, {
            onSuccess: () => {
              allocationCounter.value++
              emit('created', allocation.id)
              emit('update:open', false)
              resetForm()
            },
            onError: () => {
              errorMessage.value = t('allocation.applyError')
            }
          })
        } else {
           // Fallback if the API returns void
           allocationCounter.value++
           emit('created', 0)
           emit('update:open', false)
           resetForm()
        }
      },
      onError: () => {
        errorMessage.value = t('allocation.createError')
      }
    }
  )
}
</script>

<template>
  <BaseModal
    :open="open"
    :title="modalTitle"
    @update:open="emit('update:open', $event)"
  >
    <form class="allocation-form" @submit.prevent="handleCreateAndApply">
      <div class="field">
        <label class="field-label">{{ t('allocation.name') }}</label>
        <BaseInput
          v-model="form.name"
          :placeholder="t('allocation.namePlaceholder', { name: defaultName })"
        />
      </div>

      <div class="field">
        <label class="field-label">{{ t('allocation.type') }}</label>
        <BaseSelect
          v-model="form.type"
          :options="typeOptions"
          :placeholder="t('allocation.typeSelect')"
        />
      </div>

      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
    </form>

    <template #actions>
      <BaseButton :disabled="isPending" @click="handleCancel">
        {{ t('common.cancel') }}
      </BaseButton>
      <BaseButton variant="primary" :disabled="isPending" @click="handleCreateAndApply">
        <span v-if="isPending" class="loader"></span>
        {{ t('allocation.createAndApply') }}
      </BaseButton>
    </template>
  </BaseModal>
</template>

<style scoped>
.allocation-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
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

.error-message {
  font-size: 13px;
  color: var(--danger);
  padding: 10px;
  background: rgba(204, 77, 77, 0.1);
  border: 1px solid rgba(204, 77, 77, 0.3);
  border-radius: var(--radius);
}

.loader {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>