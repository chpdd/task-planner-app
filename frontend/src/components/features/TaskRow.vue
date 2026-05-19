<script setup lang="ts">
import BaseDropdown from '@/components/ui/BaseDropdown.vue';
import BaseDropdownItem from '@/components/ui/BaseDropdownItem.vue';
import { Task } from '@/domain/Task';

defineProps<{
  task: Task;
}>();

const emit = defineEmits<{
  edit: [task: Task];
  delete: [task: Task];
}>();

function getInterestColor(interest: number): string {
  // 1 (Grey) -> 10 (Green)
  const hue = 140; // Green
  const chroma = (interest - 1) * (0.18 / 9); // 0 to 0.18
  const lightness = 0.65;
  return `oklch(${lightness} ${chroma} ${hue})`;
}

function getImportanceColor(importance: number): string {
  // 1 (Grey) -> 10 (Red)
  const hue = 25; // Red-ish
  const chroma = (importance - 1) * (0.18 / 9); // 0 to 0.18
  const lightness = 0.65;
  return `oklch(${lightness} ${chroma} ${hue})`;
}
</script>

<template>
  <div
    class="task-row"
    :class="{ 'is-overdue': task.isOverdue }"
    :style="{
      '--task-interest': getInterestColor(task.interest),
      '--task-importance': getImportanceColor(task.importance),
    }"
  >
    <!-- Gradient bar (visible on hover) -->
    <div class="gradient-bar" />

    <!-- Content -->
    <div class="task-content">
      <!-- Header -->
      <div class="task-header">
        <h3 class="task-name">{{ task.name }}</h3>
        <BaseDropdown align="end">
          <template #trigger>
            <button type="button" class="action-btn" aria-label="Actions">
              <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                <circle cx="12" cy="6" r="1.5" />
                <circle cx="12" cy="12" r="1.5" />
                <circle cx="12" cy="18" r="1.5" />
              </svg>
            </button>
          </template>
          <BaseDropdownItem @select="emit('edit', task)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
            </svg>
            Edit
          </BaseDropdownItem>
          <BaseDropdownItem destructive @select="emit('delete', task)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
              <polyline points="3,6 5,6 21,6" />
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
            </svg>
            Delete
          </BaseDropdownItem>
        </BaseDropdown>
      </div>

      <!-- Meta info -->
      <div class="task-meta">
        <!-- Deadline pill -->
        <span v-if="task.deadline" class="pill deadline-pill" :class="{ 'text-danger': task.isOverdue }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12">
            <circle cx="12" cy="12" r="10" />
            <polyline points="12,6 12,12 16,14" />
          </svg>
          {{ task.formattedDeadline }}
        </span>

        <!-- Interest pill -->
        <span class="pill interest-pill">
          <svg viewBox="0 0 24 24" fill="currentColor" width="12" height="12">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
          </svg>
          Interest {{ task.interest }}
        </span>

        <!-- Importance pill -->
        <span class="pill importance-pill">
          <svg viewBox="0 0 24 24" fill="currentColor" width="12" height="12">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
          </svg>
          Importance {{ task.importance }}
        </span>

        <!-- Hours pill -->
        <span class="pill hours-pill">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12">
            <circle cx="12" cy="12" r="10" />
            <polyline points="12,6 12,12 16,14" />
          </svg>
          {{ task.workHours }}h
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.task-row {
  position: relative;
  display: flex;
  align-items: stretch;
  background: var(--surface);
  border: 3px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 14px 14px 24px;
  transition: background-color 0.15s, box-shadow 0.15s;
  cursor: default;
}

.task-row:hover {
  background: var(--surface-hover);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.gradient-bar {
  position: absolute;
  left: 10px;
  top: 14px;
  bottom: 14px;
  width: 5px;
  background: linear-gradient(180deg, var(--task-interest), var(--task-importance));
  border-radius: 999px;
  opacity: 0.9;
}

.task-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.task-name {
  font-size: 15px;
  font-weight: 500;
  color: var(--fg);
  line-height: 1.4;
  margin: 0;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: transparent;
  border: none;
  border-radius: calc(var(--radius) - 4px);
  color: var(--muted);
  cursor: pointer;
  transition: background-color 0.15s, color 0.15s;
  flex-shrink: 0;
}

.action-btn:hover {
  background: var(--bg);
  color: var(--fg);
}

.task-description {
  font-size: 13px;
  color: var(--muted);
  line-height: 1.5;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.task-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 4px;
}

.pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 500;
  border-radius: 999px;
  background: var(--bg);
  border: 3px solid var(--border);
  color: var(--muted);
  white-space: nowrap;
}

.deadline-pill svg {
  color: var(--accent);
}

.interest-pill svg {
  color: var(--task-interest);
}

.importance-pill svg {
  color: var(--task-importance);
}

.hours-pill {
  background: oklch(0.25 0.005 285);
}
</style>
