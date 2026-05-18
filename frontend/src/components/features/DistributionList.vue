<script setup lang="ts">
import { watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import BaseDropdown from '@/components/ui/BaseDropdown.vue'
import BaseDropdownItem from '@/components/ui/BaseDropdownItem.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import type { DistributionFormData } from './DistributionModal.vue'
import { useToast } from '@/composables/useToast'

const { t } = useI18n()
const { error: showError } = useToast()

const typeLabels = computed(() => ({
  even: t('distribution.types.even'),
  frontloaded: t('distribution.types.frontloaded'),
  backloaded: t('distribution.types.backloaded'),
}))

const props = withDefaults(defineProps<{
  distributions: DistributionFormData[]
  activeId?: string | null
  isLoading?: boolean
  error?: Error | null
}>(), {
  isLoading: false,
  error: null,
})

const emit = defineEmits<{
  select: [id: string]
  edit: [distribution: DistributionFormData]
  delete: [id: string]
  retry: []
}>()

watch(() => props.error, (err) => {
  if (err) {
    showError(t('tasks.loadError'));
  }
});

function handleEdit(distribution: DistributionFormData) {
  emit('edit', distribution)
}

function handleDelete(id: string) {
  emit('delete', id)
}
</script>

<template>
  <div class="distribution-list">
    <div class="list-header">
      <BaseButton @click="emit('select', '')">
        + {{ t('distribution.create') }}
      </BaseButton>
    </div>

    <EmptyState
      v-if="isLoading"
      variant="loading"
      :title="t('common.loading')"
    />

    <EmptyState
      v-else-if="error"
      variant="error"
      :title="t('tasks.loadError')"
      :message="t('tasks.loadError')"
      :action-label="t('common.retry')"
      @retry="emit('retry')"
    />

    <div v-else-if="distributions.length === 0" class="list-empty">
      <p>{{ t('tasks.empty') }}</p>
      <p class="empty-hint">{{ t('tasks.emptyHint') }}</p>
    </div>

    <div v-else class="list-items">
      <div
        v-for="dist in distributions"
        :key="dist.id"
        class="list-item"
        :class="{ active: dist.id === activeId }"
      >
        <div class="item-content" @click="emit('select', dist.id || '')">
          <div class="item-name">
            {{ dist.name || t('distribution.title') }}
          </div>
          <div class="item-meta">
            <span class="item-type">{{ typeLabels[dist.type] }}</span>
            <span v-if="dist.dayLimits.length > 0" class="item-limits">
              {{ t('distribution.limitsCount', { count: dist.dayLimits.length }) }}
            </span>
          </div>
        </div>

        <BaseDropdown align="end">
          <template #trigger>
            <button class="item-menu-btn" type="button">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="1" />
                <circle cx="12" cy="5" r="1" />
                <circle cx="12" cy="19" r="1" />
              </svg>
            </button>
          </template>

          <BaseDropdownItem @select="handleEdit(dist)">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
            </svg>
            {{ t('common.edit') }}
          </BaseDropdownItem>

          <BaseDropdownItem destructive @select="handleDelete(dist.id!)">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="3 6 5 6 21 6" />
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
            </svg>
            {{ t('common.delete') }}
          </BaseDropdownItem>
        </BaseDropdown>
      </div>
    </div>
  </div>
</template>

<style scoped>
.distribution-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.list-header {
  padding-bottom: 4px;
}

.list-empty {
  padding: 24px 16px;
  text-align: center;
  color: var(--muted);
  font-size: 14px;
}

.empty-hint {
  font-size: 13px;
  opacity: 0.8;
  margin-top: 4px;
}

.list-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.list-item {
  display: flex;
  align-items: center;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  transition: background-color 0.15s, border-color 0.15s;
}

.list-item:hover {
  background: var(--surface-hover);
  border-color: var(--accent);
}

.list-item.active {
  background: var(--surface-hover);
  border-color: var(--accent);
}

.item-content {
  flex: 1;
  padding: 12px;
  cursor: pointer;
  min-width: 0;
}

.item-name {
  font-size: 14px;
  color: var(--fg);
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-meta {
  display: flex;
  gap: 8px;
  font-size: 12px;
}

.item-type {
  color: var(--muted);
}

.item-limits {
  color: var(--muted);
  opacity: 0.8;
}

.item-menu-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: transparent;
  border: none;
  color: var(--muted);
  cursor: pointer;
  transition: color 0.15s;
}

.item-menu-btn:hover {
  color: var(--fg);
}

.list-item :deep(.base-dropdown-content) {
  min-width: 160px;
}
</style>
