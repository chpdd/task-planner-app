<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import TaskRow from '@/components/features/TaskRow.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import { Task } from '@/domain/Task'

defineProps<{
  tasks: Task[]
  isLoading: boolean
  error: any
}>()

const emit = defineEmits<{
  edit: [task: Task]
  delete: [task: Task]
  retry: []
}>()

const { t } = useI18n()
</script>

<template>
  <div class="content">
    <div v-if="isLoading" class="loading-state">
      <div class="loading-spinner" />
      <span>{{ t('tasks.loading') }}</span>
    </div>
    <EmptyState
      v-else-if="error"
      variant="error"
      :title="t('tasks.errorTitle')"
      :message="t('tasks.errorMessage')"
      :action-label="t('common.retry')"
      @retry="emit('retry')"
    />
    <EmptyState
      v-else-if="!tasks?.length"
      variant="empty"
      :title="t('tasks.empty')"
      :message="t('tasks.emptyHint')"
    />
    <div v-else class="task-list">
      <TaskRow
        v-for="task in tasks"
        :key="task.id"
        :task="task"
        @edit="emit('edit', task)"
        @delete="emit('delete', task)"
      />
    </div>
  </div>
</template>

<style scoped>
.content {
  flex: 1;
  overflow: auto;
  padding: 20px 24px;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 800px;
  margin: 0 auto;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 48px 24px;
  text-align: center;
  color: var(--muted);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
