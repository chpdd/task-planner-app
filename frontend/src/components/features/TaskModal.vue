<script setup lang="ts">
import { computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import { Task } from '@/domain/Task'
import { createTaskSchema } from '@/schemas/task'
import { TASK_CONFIG } from '@/config/constants'
import type { CreateTaskData } from '@/types/api'

const { t } = useI18n()

const props = defineProps<{
  open: boolean
  task?: Task | null
  existingTasks?: Task[]
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  save: [data: CreateTaskData]
}>()

const validationSchema = computed(() => {
  return toTypedSchema(
    createTaskSchema(t).refine((data) => {
      if (isEditing.value) {
        // If editing, exclude current task from name check
        return !props.existingTasks?.some(
          t => t.name.toLowerCase() === data.name.trim().toLowerCase() && t.id !== props.task?.id
        )
      }
      return !props.existingTasks?.some(
        t => t.name.toLowerCase() === data.name.trim().toLowerCase()
      )
    }, {
      message: t('tasks.duplicateName'),
      path: ['name']
    })
  )
})

const { values, errors, defineField, handleSubmit, resetForm, setValues } = useForm({
  validationSchema,
  initialValues: {
    name: '',
    deadline: '',
    interest: TASK_CONFIG.DEFAULT_INTEREST,
    importance: TASK_CONFIG.DEFAULT_IMPORTANCE,
    work_hours: TASK_CONFIG.DEFAULT_HOURS,
  }
})

const [name, nameProps] = defineField('name', {
  validateOnInput: false,
  validateOnBlur: true,
})
const [deadline, deadlineProps] = defineField('deadline')
const [interest, interestProps] = defineField('interest')
const [importance, importanceProps] = defineField('importance')
const [work_hours, workHoursProps] = defineField('work_hours')

const isEditing = computed(() => !!props.task?.id)
const modalTitle = computed(() => isEditing.value ? t('tasks.edit') : t('tasks.create'))

watch(
  () => props.task,
  (task) => {
    if (task) {
      setValues({
        name: task.name,
        deadline: task.deadline ? task.deadline.toISOString().split('T')[0] : '',
        interest: task.interest,
        importance: task.importance,
        work_hours: task.workHours,
      })
    } else {
      resetForm()
    }
  },
  { immediate: true }
)

const handleSave = handleSubmit((formValues) => {
  const data: CreateTaskData = {
    name: formValues.name.trim(),
    deadline: formValues.deadline || undefined,
    interest: formValues.interest,
    importance: formValues.importance,
    work_hours: formValues.work_hours,
  }

  if (props.task?.id) {
    ;(data as CreateTaskData & { id: number }).id = props.task.id
  }

  emit('save', data)
  emit('update:open', false)
})

function handleCancel() {
  emit('update:open', false)
}

// Quick date selection
function setQuickDate(daysFromNow: number) {
  const date = new Date()
  date.setDate(date.getDate() + daysFromNow)
  setValues({ deadline: date.toISOString().split('T')[0] })
}

function clearDate() {
  setValues({ deadline: '' })
}

// Dynamic slider colors
const interestGradient = computed(() => {
  const val = values.interest ?? TASK_CONFIG.DEFAULT_INTEREST
  const hue = 145 // Green
  const chroma = (val - 1) * (0.35 / 9)
  return `oklch(0.65 ${chroma} ${hue})`
})

const importanceGradient = computed(() => {
  const val = values.importance ?? TASK_CONFIG.DEFAULT_IMPORTANCE
  const hue = 28 // Red
  const chroma = (val - 1) * (0.35 / 9)
  return `oklch(0.65 ${chroma} ${hue})`
})

const interestSliderBg = `linear-gradient(90deg, oklch(0.65 0 0), oklch(0.65 0.35 145))`
const importanceSliderBg = `linear-gradient(90deg, oklch(0.65 0 0), oklch(0.65 0.35 28))`
</script>

<template>
  <BaseModal
    :open="open"
    :title="modalTitle"
    @update:open="emit('update:open', $event)"
  >
    <form
      class="task-form"
      @submit.prevent="handleSave"
    >
      <div class="field">
        <label class="field-label">{{ t('tasks.title') }}</label>
        <BaseInput
          v-model="name"
          v-bind="nameProps"
          :placeholder="t('tasks.enterTitle')"
          :error="!!errors.name"
        />
        <span
          v-if="errors.name"
          class="field-error"
        >{{ errors.name }}</span>
      </div>

      <div class="form-row">
        <div class="field flex-1">
          <label class="field-label">{{ t('tasks.deadline') }}</label>
          <div class="date-picker-container">
             <BaseInput
              v-model="deadline"
              v-bind="deadlineProps"
              type="date"
            />
            <div class="quick-dates">
              <button type="button" class="quick-date-btn" @click="setQuickDate(0)">
                Сегодня
              </button>
              <button type="button" class="quick-date-btn" @click="setQuickDate(1)">
                Завтра
              </button>
              <button v-if="values.deadline" type="button" class="quick-date-btn clear-btn" @click="clearDate">
                &times;
              </button>
            </div>
          </div>
        </div>

        <div class="field work-hours-field">
          <label class="field-label">{{ t('tasks.workHours') }}</label>
          <BaseInput
            v-model.number="work_hours"
            v-bind="workHoursProps"
            type="number"
            step="1"
            :min="TASK_CONFIG.MIN_HOURS"
            class="hours-input-small"
            :error="!!errors.work_hours"
          />
        </div>
      </div>

      <div class="slider-field">
        <div class="slider-header">
          <label class="field-label">{{ t('tasks.interest') }}</label>
          <span class="slider-value" :style="{ color: interestGradient }">{{ values.interest }}</span>
        </div>
        <input
          v-model.number="interest"
          v-bind="interestProps"
          type="range"
          :min="TASK_CONFIG.MIN_INTEREST"
          :max="TASK_CONFIG.MAX_INTEREST"
          step="1"
          class="range-input"
          :style="{ background: interestSliderBg }"
        >
      </div>

      <div class="slider-field">
        <div class="slider-header">
          <label class="field-label">{{ t('tasks.importance') }}</label>
          <span class="slider-value" :style="{ color: importanceGradient }">{{ values.importance }}</span>
        </div>
        <input
          v-model.number="importance"
          v-bind="importanceProps"
          type="range"
          :min="TASK_CONFIG.MIN_IMPORTANCE"
          :max="TASK_CONFIG.MAX_IMPORTANCE"
          step="1"
          class="range-input"
          :style="{ background: importanceSliderBg }"
        >
      </div>
    </form>

    <template #actions>
      <BaseButton @click="handleCancel">
        {{ t('common.cancel') }}
      </BaseButton>
      <BaseButton
        variant="primary"
        @click="handleSave"
      >
        {{ isEditing ? t('common.save') : t('common.create') }}
      </BaseButton>
    </template>
  </BaseModal>
</template>

<style scoped>
.task-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.flex-1 { flex: 1; }

.work-hours-field {
  width: 100px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--muted);
}

.field-error {
  font-size: 12px;
  color: var(--danger);
  margin-top: 2px;
}

.date-picker-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.quick-dates {
  display: flex;
  gap: 4px;
}

.quick-date-btn {
  padding: 2px 8px;
  font-size: 11px;
  border: 1px solid var(--border);
  border-radius: 4px;
  background: var(--surface-hover);
  color: var(--muted);
  cursor: pointer;
  transition: all 0.1s;
}

.quick-date-btn:hover {
  background: var(--bg);
  color: var(--fg);
}

.quick-date-btn.clear-btn {
  color: var(--danger);
  font-weight: bold;
}

.slider-field {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.slider-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.slider-value {
  font-size: 14px;
  font-weight: 600;
  min-width: 24px;
  text-align: right;
}

.range-input {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 6px;
  border-radius: 999px;
  outline: none;
  cursor: pointer;
}

.range-input::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--bg);
  border: 2px solid var(--fg);
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  cursor: pointer;
}

.range-input::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--bg);
  border: 2px solid var(--fg);
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  cursor: pointer;
}
</style>
