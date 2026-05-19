<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseSelect from '@/components/ui/BaseSelect.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

const { t } = useI18n()

export type AllocationType = 'even' | 'frontloaded' | 'backloaded'

export interface DayLimit {
  day: number
  hours: number
}

export interface AllocationFormData {
  id?: string
  name: string
  type: AllocationType
  dayLimits: DayLimit[]
}

const props = defineProps<{
  open: boolean
  allocation?: AllocationFormData | null
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  save: [data: AllocationFormData]
}>()

const typeOptions = computed(() => [
  { value: 'even', label: t('allocation.types.even') },
  { value: 'frontloaded', label: t('allocation.types.frontloaded') },
  { value: 'backloaded', label: t('allocation.types.backloaded') },
])

const form = ref<AllocationFormData>({
  name: '',
  type: 'even',
  dayLimits: [],
})

const newDayLimitDay = ref('')
const newDayLimitHours = ref('')
const errors = ref<{ name?: string }>({})

const isEditing = computed(() => !!props.allocation?.id)

const modalTitle = computed(() =>
  isEditing.value ? t('allocation.edit') : t('allocation.create')
)

watch(
  () => props.allocation,
  (dist) => {
    if (dist) {
      form.value = {
        id: dist.id,
        name: dist.name,
        type: dist.type,
        dayLimits: [...(dist.dayLimits || [])],
      }
    } else {
      form.value = {
        name: '',
        type: 'even',
        dayLimits: [],
      }
    }
    errors.value = {}
    newDayLimitDay.value = ''
    newDayLimitHours.value = ''
  },
  { immediate: true }
)

function addDayLimit() {
  const day = parseInt(newDayLimitDay.value, 10)
  const hours = parseInt(newDayLimitHours.value, 10)

  if (isNaN(day) || day < 1 || day > 35) return
  if (isNaN(hours) || hours < 0 || hours > 24) return

  const existing = form.value.dayLimits.find((l) => l.day === day)
  if (existing) {
    existing.hours = hours
  } else {
    form.value.dayLimits.push({ day, hours })
    form.value.dayLimits.sort((a, b) => a.day - b.day)
  }

  newDayLimitDay.value = ''
  newDayLimitHours.value = ''
}

function removeDayLimit(day: number) {
  form.value.dayLimits = form.value.dayLimits.filter((l) => l.day !== day)
}

function validate(): boolean {
  errors.value = {}
  return true
}

function handleSave() {
  if (!validate()) return

  const data: AllocationFormData = {
    id: form.value.id,
    name: form.value.name.trim(),
    type: form.value.type,
    dayLimits: [...form.value.dayLimits],
  }

  emit('save', data)
  emit('update:open', false)
}

function handleCancel() {
  emit('update:open', false)
}
</script>

<template>
  <BaseModal
    :open="open"
    :title="modalTitle"
    @update:open="emit('update:open', $event)"
  >
    <form class="allocation-form" @submit.prevent="handleSave">
      <div class="field">
        <label class="field-label">{{ t('allocation.name') }}</label>
        <BaseInput
          v-model="form.name"
          :placeholder="t('allocation.namePlaceholder')"
        />
        <span v-if="errors.name" class="field-error">{{ errors.name }}</span>
      </div>

      <div class="field">
        <label class="field-label">{{ t('allocation.type') }}</label>
        <BaseSelect
          v-model="form.type"
          :options="typeOptions"
          :placeholder="t('allocation.typeSelect')"
        />
      </div>

      <div class="field">
        <label class="field-label">{{ t('allocation.dayLimits') }}</label>
        <p class="field-hint">{{ t('allocation.dayLimitsHint') }}</p>

        <div class="day-limits-list">
          <div
            v-for="limit in form.dayLimits"
            :key="limit.day"
            class="day-limit-item"
          >
            <span class="day-limit-label">{{ t('allocation.limitDay') }} {{ limit.day }}</span>
            <span class="day-limit-value">{{ limit.hours }} {{ t('tasks.hoursShort') }}</span>
            <button
              type="button"
              class="day-limit-remove"
              @click="removeDayLimit(limit.day)"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
        </div>

        <div class="day-limit-add">
          <BaseInput
            v-model="newDayLimitDay"
            type="number"
            :placeholder="t('allocation.limitDay')"
          />
          <span class="add-separator">=</span>
          <BaseInput
            v-model="newDayLimitHours"
            type="number"
            :placeholder="t('allocation.limitHours')"
          />
          <BaseButton
            type="button"
            size="small"
            @click="addDayLimit"
          >
            +
          </BaseButton>
        </div>
      </div>
    </form>

    <template #actions>
      <BaseButton @click="handleCancel">
        {{ t('common.cancel') }}
      </BaseButton>
      <BaseButton variant="primary" @click="handleSave">
        {{ isEditing ? t('common.save') : t('common.create') }}
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

.field-hint {
  font-size: 12px;
  color: var(--muted);
  opacity: 0.8;
  margin-top: -2px;
}

.field-error {
  font-size: 12px;
  color: var(--danger);
}

.day-limits-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 10px;
}

.day-limit-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background: var(--surface-hover);
  border: 3px solid var(--border);
  border-radius: var(--radius);
}

.day-limit-label {
  font-size: 13px;
  color: var(--fg);
}

.day-limit-value {
  font-size: 13px;
  color: var(--muted);
  margin-left: auto;
}

.day-limit-remove {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: transparent;
  border: none;
  color: var(--muted);
  cursor: pointer;
  border-radius: 4px;
  transition: color 0.15s, background 0.15s;
}

.day-limit-remove:hover {
  color: var(--danger);
  background: rgba(204, 77, 77, 0.1);
}

.day-limit-add {
  display: flex;
  align-items: center;
  gap: 8px;
}

.day-limit-add > :deep(.base-input) {
  width: 80px;
}

.add-separator {
  color: var(--muted);
  font-size: 14px;
}
</style>
