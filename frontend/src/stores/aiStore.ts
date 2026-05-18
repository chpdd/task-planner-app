import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from '@/api/client';
import { useToast } from '@/composables/useToast';

export interface AiMessage {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export const useAiStore = defineStore('ai', () => {
  const toast = useToast();
  const isOpen = ref(false);
  const inputMessage = ref('');
  const messages = ref<AiMessage[]>([]);
  const isLoading = ref(false);

  function open() {
    isOpen.value = true;
  }

  function close() {
    isOpen.value = false;
  }

  function toggle() {
    isOpen.value = !isOpen.value;
  }

  async function send() {
    if (!inputMessage.value.trim() || isLoading.value) {
      return;
    }

    const userMessage = inputMessage.value;
    inputMessage.value = '';

    messages.value.push({
      id: Date.now(),
      role: 'user',
      content: userMessage,
      timestamp: new Date(),
    });

    isLoading.value = true;

    try {
      const response = await api.ai.chat(userMessage);

      messages.value.push({
        id: Date.now(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
      });
    } catch (e) {
      toast.error('Ошибка AI: ' + (e instanceof Error ? e.message : 'Неизвестная ошибка'));
    } finally {
      isLoading.value = false;
    }
  }

  return { isOpen, inputMessage, messages, isLoading, open, close, toggle, send };
});
