import { ref } from 'vue';
import { defineStore } from 'pinia';

export const useUiStore = defineStore('ui', () => {
  const isTaskModalOpen = ref(false);
  const isDistributionModalOpen = ref(false);
  const isAiDrawerOpen = ref(false);

  return { isTaskModalOpen, isDistributionModalOpen, isAiDrawerOpen };
});
