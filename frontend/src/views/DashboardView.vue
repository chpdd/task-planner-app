<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import AppShell from '@/components/layout/AppShell.vue'
import Sidebar from '@/components/layout/Sidebar.vue'
import TaskModal from '@/components/features/TaskModal.vue'
import AiAgentDrawer from '@/components/features/AiAgentDrawer.vue'
import MiniMonthCalendar from '@/components/features/MiniMonthCalendar.vue'
import DashboardTaskList from '@/components/features/DashboardTaskList.vue'
import DashboardWeekCalendar from '@/components/features/DashboardWeekCalendar.vue'
import CalendarHierarchy from '@/components/features/CalendarHierarchy.vue'
import CreateCalendarModal from '@/components/features/CreateCalendarModal.vue'
import CreateAllocationModal from '@/components/features/CreateAllocationModal.vue'
import ConfirmModal from '@/components/ui/ConfirmModal.vue'
import LanguageSwitcher from '@/components/ui/LanguageSwitcher.vue'
import { useUiStore } from '@/stores/uiStore'
import { useTasksStore } from '@/stores/tasksStore'
import { Task } from '@/domain/Task'
import type { CreateTaskData } from '@/types/api'

const { t } = useI18n()
const uiStore = useUiStore()
const tasksStore = useTasksStore()

const router = useRouter()

// Tab state
const activeTab = ref<'tasks' | 'calendar'>('tasks')

// Tasks logic
const { data: tasks, isLoading, error, refetch } = tasksStore.useTasksQuery()
const createTaskMutation = tasksStore.useCreateTaskMutation()
const updateTaskMutation = tasksStore.useUpdateTaskMutation()
const deleteTaskMutation = tasksStore.useDeleteTaskMutation()

const editingTask = ref<Task | null>(null)
const taskToDelete = ref<Task | null>(null)
const showDeleteConfirm = ref(false)

// Calendar/Allocation modals
const showCreateCalendarModal = ref(false)
const showCreateAllocationModal = ref(false)
const calendarIdForNewAllocation = ref<number | null>(null)

function handleEditTask(task: Task) {
  editingTask.value = task
  uiStore.isTaskModalOpen = true
}

function handleDeleteRequest(task: Task) {
  taskToDelete.value = task
  showDeleteConfirm.value = true
}

function confirmDeleteTask() {
  if (taskToDelete.value) {
    deleteTaskMutation.mutate(taskToDelete.value.id)
    taskToDelete.value = null
  }
}

function handleTaskSaved(data: CreateTaskData) {
  if (editingTask.value) {
    updateTaskMutation.mutate({ id: editingTask.value.id, data })
  } else {
    createTaskMutation.mutate(data)
  }
}

function handleCreateCalendarRequest() {
  showCreateCalendarModal.value = true
}

function handleCreateAllocationRequest(calendarId: number) {
  calendarIdForNewAllocation.value = calendarId
  showCreateAllocationModal.value = true
}
</script>

<template>
  <AppShell>
    <template #sidebar>
      <Sidebar
        :view-type="activeTab"
        @create-task="editingTask = null; uiStore.isTaskModalOpen = true"
        @create-calendar="handleCreateCalendarRequest"
        @create-allocation="handleCreateAllocationRequest"
      />
    </template>

    <template #top>
      <div class="top-bar">
        <div class="tabs">
          <button
            class="tab"
            :class="{ active: activeTab === 'tasks' }"
            @click="activeTab = 'tasks'"
          >
            {{ t('nav.tasks') }}
          </button>
          <button
            class="tab"
            :class="{ active: activeTab === 'calendar' }"
            @click="activeTab = 'calendar'"
          >
            {{ t('nav.calendar') }}
          </button>
        </div>
        <div class="top-actions">
          <LanguageSwitcher />
          <button class="ai-btn" @click="uiStore.isAiDrawerOpen = true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
            {{ t('agent.title') }}
          </button>
        </div>
      </div>
    </template>

    <DashboardTaskList
      v-if="activeTab === 'tasks'"
      :tasks="tasks || []"
      :is-loading="isLoading"
      :error="error"
      @edit="handleEditTask"
      @delete="handleDeleteRequest"
      @retry="refetch"
    />

    <DashboardWeekCalendar v-else />
  </AppShell>

  <TaskModal
    :open="uiStore.isTaskModalOpen"
    :task="editingTask"
    :existing-tasks="tasks || []"
    @update:open="uiStore.isTaskModalOpen = $event; editingTask = null"
    @save="handleTaskSaved"
  />

  <CreateCalendarModal
    v-model:open="showCreateCalendarModal"
  />

  <CreateAllocationModal
    v-if="calendarIdForNewAllocation !== null"
    v-model:open="showCreateAllocationModal"
    :calendar-id="calendarIdForNewAllocation"
    @created="calendarIdForNewAllocation = null"
  />

  <ConfirmModal
    v-model:open="showDeleteConfirm"
    :message="t('tasks.deleteConfirm', { name: taskToDelete?.name })"
    @confirm="confirmDeleteTask"
  />

  <AiAgentDrawer />
</template>

<style scoped>
.top-bar {
  height: 64px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: var(--bg);
}

.tabs {
  display: inline-flex;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 4px;
}

.tab {
  border: 0;
  background: transparent;
  color: var(--muted);
  padding: 7px 20px;
  border-radius: 999px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s ease;
}

.tab.active {
  background: var(--accent);
  color: var(--bg);
}

.top-actions {
  display: inline-flex;
  align-items: center;
  gap: 12px;
}

.ai-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--accent);
  color: var(--bg);
  border: none;
  border-radius: var(--radius);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.ai-btn:hover {
  filter: brightness(1.1);
  transform: translateY(-1px);
}

.sidebar-tab-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
  height: 100%;
}

.calendar-actions {
  display: flex;
  justify-content: center;
}

.create-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface-hover);
  color: var(--fg);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.create-btn.orange {
  background: var(--accent);
  color: var(--bg);
  border: none;
}

.create-btn:hover {
  background: var(--accent-hover);
  color: var(--bg);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.hierarchy-section {
  flex: 1;
  overflow-y: auto;
}

.mini-calendar-section {
  padding-top: 16px;
  border-top: 1px solid var(--border);
}
</style>
