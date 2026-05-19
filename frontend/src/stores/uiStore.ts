import { ref, watch } from 'vue';
import { defineStore } from 'pinia';

type DashboardTab = 'tasks' | 'calendar';
type CalendarViewType = 'day' | 'three_days' | 'work_week' | 'week' | 'month';

const UI_STORAGE_KEY = 'planner_ui_state_v1';
function todayLocalDate(): string {
  const now = new Date();
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, '0');
  const d = String(now.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

function loadState(): {
  isAiDrawerOpen?: boolean;
  activeTab?: DashboardTab;
  selectedAiConversationId?: number | null;
  calendarView?: CalendarViewType;
  calendarListMode?: boolean;
  calendarFocusDate?: string;
} {
  try {
    const raw = localStorage.getItem(UI_STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

export const useUiStore = defineStore('ui', () => {
  const initial = loadState();
  const isTaskModalOpen = ref(false);
  const isAllocationModalOpen = ref(false);
  const isAiDrawerOpen = ref(Boolean(initial.isAiDrawerOpen));
  const activeTab = ref<DashboardTab>(initial.activeTab ?? 'tasks');
  const selectedAiConversationId = ref<number | null>(initial.selectedAiConversationId ?? null);
  const calendarView = ref<CalendarViewType>(initial.calendarView ?? 'week');
  const calendarListMode = ref(Boolean(initial.calendarListMode));
  const calendarFocusDate = ref<string>(initial.calendarFocusDate ?? todayLocalDate());

  watch(
    [isAiDrawerOpen, activeTab, selectedAiConversationId, calendarView, calendarFocusDate, calendarListMode],
    () => {
      localStorage.setItem(
        UI_STORAGE_KEY,
        JSON.stringify({
          isAiDrawerOpen: isAiDrawerOpen.value,
          activeTab: activeTab.value,
          selectedAiConversationId: selectedAiConversationId.value,
          calendarView: calendarView.value,
          calendarFocusDate: calendarFocusDate.value,
          calendarListMode: calendarListMode.value,
        }),
      );
    },
    { deep: false },
  );

  return {
    isTaskModalOpen,
    isAllocationModalOpen,
    isAiDrawerOpen,
    activeTab,
    selectedAiConversationId,
    calendarView,
    calendarFocusDate,
    calendarListMode,
  };
});
