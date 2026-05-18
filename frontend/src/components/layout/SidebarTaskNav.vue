<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useRouter, useRoute } from 'vue-router'
import BaseButton from '@/components/ui/BaseButton.vue'
import { useUiStore } from '@/stores/uiStore'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const uiStore = useUiStore()

const props = defineProps<{
  onCreateTask: () => void
}>()
</script>

<template>
  <div class="sidebar-tasks-nav">
    <nav class="nav-links">
      <button class="nav-link" :class="{ active: route.path === '/tasks' }" @click="router.push('/tasks')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <path d="M9 11l3 3L22 4" />
          <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
        </svg>
        {{ t('nav.tasks') }}
      </button>
      <button class="nav-link" :class="{ active: route.path === '/schedule' }" @click="router.push('/schedule')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
          <line x1="16" y1="2" x2="16" y2="6" />
          <line x1="8" y1="2" x2="8" y2="6" />
          <line x1="3" y1="10" x2="21" y2="10" />
        </svg>
        {{ t('nav.schedule') }}
      </button>
    </nav>

    <div class="sidebar-actions">
      <BaseButton
        variant="default"
        size="small"
        style="width: 100%;"
        @click="uiStore.isAiDrawerOpen = true"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
        {{ t('agent.title') }}
      </BaseButton>
      <BaseButton variant="primary" size="small" style="width: 100%;" @click="props.onCreateTask">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
          <line x1="12" y1="5" x2="12" y2="19" />
          <line x1="5" y1="12" x2="19" y2="12" />
        </svg>
        {{ t('tasks.create') }}
      </BaseButton>
    </div>
  </div>
</template>

<style scoped>
.sidebar-tasks-nav {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.nav-links {
  display: flex;
  flex-direction: column;
  gap: 4px;
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
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  width: 100%;
  text-align: left;
  transition: background-color 0.15s, color 0.15s;
}

.nav-link:hover {
  background: var(--surface-hover);
  color: var(--fg);
}

.nav-link.active {
  background: var(--surface-hover);
  color: var(--fg);
}

.sidebar-actions {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
</style>
