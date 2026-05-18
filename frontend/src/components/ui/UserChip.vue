<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// UserChip - User avatar with name and logout button
interface Props {
  username: string
  isAdmin?: boolean
}

withDefaults(defineProps<Props>(), {
  isAdmin: false,
})

defineEmits<{
  logout: []
}>()
</script>

<template>
  <div class="user-chip">
    <button class="user-chip-btn" type="button">
      <span class="user-chip-left">
        <!-- Avatar circle with first letter -->
        <span class="avatar">{{ username.charAt(0).toUpperCase() }}</span>
        <span class="user-name">{{ username }}</span>
        <!-- Admin badge -->
        <span v-if="isAdmin" class="admin-badge">{{ t('user.admin') }}</span>
      </span>
      <!-- Logout indicator -->
      <span class="logout-icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" />
          <polyline points="16 17 21 12 16 7" />
          <line x1="21" y1="12" x2="9" y2="12" />
        </svg>
      </span>
    </button>
  </div>
</template>

<style scoped>
.user-chip {
  width: 100%;
}

.user-chip-btn {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 8px 12px;
  background: transparent;
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  transition: background 150ms ease;
}

.user-chip-btn:hover {
  background: var(--surface-hover);
}

.user-chip-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: var(--accent);
  color: var(--bg);
  font-size: 14px;
  font-weight: 600;
  border-radius: 50%;
}

.user-name {
  font-size: 14px;
  color: var(--fg);
}

.admin-badge {
  padding: 2px 6px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--bg);
  background: var(--accent);
  border-radius: 4px;
}

.logout-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  color: var(--muted);
}

.logout-icon svg {
  width: 100%;
  height: 100%;
}
</style>
