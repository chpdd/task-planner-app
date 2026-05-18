<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useI18n } from 'vue-i18n'
import CalendarHierarchy from '@/components/features/CalendarHierarchy.vue'
import MiniCalendar from '@/components/features/MiniCalendar.vue'

const props = defineProps<{
  username?: string
  viewType?: 'tasks' | 'calendar'
  selectedDate?: Date | null
}>()

const emit = defineEmits<{
  logout: []
  'create-calendar': []
  'create-allocation': [calendarId: number]
  'create-task': []
  'date-select': [date: Date]
}>()

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const isOpen = ref(false)

const displayUsername = computed(() => props.username || authStore.user?.username || 'user')

function toggleDropdown() {
  isOpen.value = !isOpen.value
}

function closeDropdown() {
  isOpen.value = false
}

async function handleLogout() {
  authStore.logout()
  closeDropdown()
  await router.push('/login')
}

function handleCreateCalendar() {
  emit('create-calendar')
}

function handleCreateAllocation(calendarId: number) {
  emit('create-allocation', calendarId)
}

function handleCreateTask() {
  emit('create-task')
}

function handleDateSelect(date: Date) {
  emit('date-select', date)
}
</script>

<template>
  <aside class="sidebar">
    <!-- Brand -->
    <div class="brand">
      <div class="brand-box" />
      <span>[todos]</span>
    </div>

    <!-- Sidebar content area -->
    <div class="sidebar-content">
      <!-- Tasks View Sidebar -->
      <div v-if="viewType === 'tasks' && route.path !== '/calendar' && route.path !== '/schedule'" class="sidebar-section">
        <button class="create-btn orange" @click="handleCreateTask">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          {{ t('tasks.create') }}
        </button>
      </div>

      <!-- Calendar View Sidebar -->
      <div v-else-if="viewType === 'calendar' || route.path === '/calendar' || route.path === '/schedule'" class="sidebar-section">
        <button class="create-btn orange" @click="handleCreateCalendar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          {{ t('calendar.createTitle') }}
        </button>
        
        <div class="hierarchy-section">
          <CalendarHierarchy
            @create-allocation="handleCreateAllocation"
            @create-calendar="handleCreateCalendar"
          />
        </div>

        <div class="mini-calendar-section">
          <MiniCalendar
            :selected-date="selectedDate"
            @date-select="handleDateSelect"
          />
        </div>
      </div>

      <!-- Fallback / Slot for other views if needed -->
      <slot v-else />
    </div>

    <!-- User chip -->
    <div class="user-chip">
      <div class="user-dropdown">
        <button class="user-chip-btn" type="button" @click="toggleDropdown">
          <span class="user-chip-left">
            <svg class="user-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <circle cx="12" cy="8" r="4" />
              <path d="M4 20c1.8-3.6 5-5.4 8-5.4s6.2 1.8 8 5.4" />
            </svg>
            <span class="user-name">{{ displayUsername }}</span>
          </span>
          <span style="color: var(--muted)">⋯</span>
        </button>

        <div v-if="isOpen" class="dropdown-menu" @mouseleave="closeDropdown">
          <button class="dropdown-item" type="button" @click="handleLogout">
            {{ t('auth.logout') }}
          </button>
        </div>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  display: flex;
  flex-direction: column;
  width: 236px;
  height: 100vh;
  background: var(--surface);
  border-right: 1px solid var(--border);
  padding: 16px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  margin-bottom: 24px;
}

.brand-box {
  width: 28px;
  height: 28px;
  background: var(--accent);
  border-radius: 6px;
}

.brand span {
  font-size: 16px;
  font-weight: 600;
  color: var(--fg);
  font-family: var(--font-mono);
}

.sidebar-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
  height: 100%;
}

.hierarchy-section {
  flex: 1;
  overflow-y: auto;
  margin: 0 -8px;
  padding: 0 8px;
}

.mini-calendar-section {
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid var(--border);
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
  filter: brightness(1.1);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.user-chip {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border);
}

.user-chip-btn {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 8px 12px;
  background: transparent;
  border: none;
  border-radius: calc(var(--radius) - 2px);
  color: var(--fg);
  cursor: pointer;
  transition: background-color 0.15s;
}

.user-chip-btn:hover {
  background: var(--surface-hover);
}

.user-chip-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-icon {
  width: 18px;
  height: 18px;
  color: var(--muted);
}

.user-name {
  font-size: 13px;
  font-weight: 500;
}

.user-dropdown {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  bottom: 100%;
  left: 0;
  right: 0;
  margin-bottom: 4px;
  background: var(--surface-elevated, var(--surface));
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  z-index: 50;
}

.dropdown-item {
  display: block;
  width: 100%;
  padding: 10px 12px;
  background: transparent;
  border: none;
  color: var(--fg);
  font-size: 13px;
  text-align: left;
  cursor: pointer;
  transition: background-color 0.15s;
}

.dropdown-item:hover {
  background: var(--surface-hover);
}
</style>
