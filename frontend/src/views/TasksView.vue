<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Task } from '@/domain/Task'
import AppShell from '@/components/layout/AppShell.vue'
import Sidebar from '@/components/layout/Sidebar.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import TaskRow from '@/components/features/TaskRow.vue'
import TaskModal from '@/components/features/TaskModal.vue'
import AiAgentDrawer from '@/components/features/AiAgentDrawer.vue'
import { useUiStore } from '@/stores/uiStore'
import { useTasksStore } from '@/stores/tasksStore'
import type { CreateTaskData } from '@/types/api'

const uiStore = useUiStore()
const tasksStore = useTasksStore()

const { t } = useI18n()

const {
  data: tasks,
  isLoading,
  error,
  refetch,
} = tasksStore.useTasksQuery()

const createTaskMutation = tasksStore.useCreateTaskMutation()
const updateTaskMutation = tasksStore.useUpdateTaskMutation()
const deleteTaskMutation = tasksStore.useDeleteTaskMutation()

const editingTask = ref<Task | null>(null)

function handleEdit(task: Task) {
  editingTask.value = task
  uiStore.isTaskModalOpen = true
}

function handleDelete(task: Task) {
  if (confirm(`Удалить задачу "${task.name}"?`)) {
    deleteTaskMutation.mutate(task.id)
  }
}

function openCreateTaskModal() {
  editingTask.value = null
  uiStore.isTaskModalOpen = true
}

function handleTaskSaved(data: CreateTaskData) {
  if (editingTask.value) {
    updateTaskMutation.mutate({ id: editingTask.value.id, data })
  } else {
    createTaskMutation.mutate(data)
  }
}
</script>

<template>
  <AppShell>
    <template #sidebar>
      <Sidebar view-type="tasks" @create-task="openCreateTaskModal" />
    </template>

    <template #top>
      <div class="top-bar">
        <h1 class="page-title">{{ t('tasks.title') }}</h1>
        <span class="task-count">{{ tasks?.length || 0 }} задач</span>
      </div>
    </template>

    <div class="tasks-container">
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
        @retry="refetch"
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
          @edit="handleEdit"
          @delete="handleDelete"
        />
      </div>
    </div>
  </AppShell>
  <TaskModal
    :open="uiStore.isTaskModalOpen"
    :task="editingTask"
    :existing-tasks="tasks || []"
    @update:open="uiStore.isTaskModalOpen = $event; editingTask = null"
    @save="handleTaskSaved"
  />
  <AiAgentDrawer />
</template>

<style scoped>
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  border-bottom: 3px solid var(--border);
  background: var(--bg);
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--fg);
  margin: 0;
}

.task-count {
  font-size: 13px;
  color: var(--muted);
  background: var(--surface);
  padding: 4px 12px;
  border-radius: 999px;
  border: 3px solid var(--border);
}

.tasks-container {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
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
  to {
    transform: rotate(360deg);
  }
}

.nav-links {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 0 12px;
  margin-top: 24px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: calc(var(--radius) - 2px);
  border: none;
  background: none;
  color: var(--muted);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  width: 100%;
  text-align: left;
  transition: background-color 0.15s, color 0.15s;
}

.nav-link:hover {
  background: var(--surface);
  color: var(--fg);
}

.nav-link.active {
  background: var(--surface);
  color: var(--fg);
}
</style>
