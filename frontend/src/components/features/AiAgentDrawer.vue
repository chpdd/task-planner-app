<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useUiStore } from '@/stores/uiStore'
import { api } from '@/api/client'
import { useToast } from '@/composables/useToast'

const { t } = useI18n()
const uiStore = useUiStore()
const toast = useToast()

const isOpen = ref(uiStore.isAiDrawerOpen)
const message = ref('')
const messages = ref<Array<{ role: 'user' | 'assistant'; content: string }>>([])
const isLoading = ref(false)
const messagesEnd = ref<HTMLElement | null>(null)
const textareaRef = ref<HTMLTextAreaElement | null>(null)

watch(() => uiStore.isAiDrawerOpen, (val) => {
  isOpen.value = val
  if (val) {
    scrollToBottom()
    nextTick(() => textareaRef.value?.focus())
  }
})

watch(message, () => {
  adjustTextareaHeight()
})

function adjustTextareaHeight() {
  const textarea = textareaRef.value
  if (!textarea) return
  
  textarea.style.height = '42px'
  const newHeight = Math.min(textarea.scrollHeight, 200)
  textarea.style.height = `${newHeight}px`
}

watch(isOpen, (val) => {
  uiStore.isAiDrawerOpen = val
})

function close() {
  isOpen.value = false
}

async function scrollToBottom() {
  await nextTick()
  if (messagesEnd.value) {
    messagesEnd.value.scrollIntoView({ behavior: 'smooth' })
  }
}

async function send() {
  const content = message.value.trim()
  if (!content || isLoading.value) return

  messages.value.push({ role: 'user', content })
  message.value = ''
  nextTick(() => {
    if (textareaRef.value) textareaRef.value.style.height = '42px'
  })
  isLoading.value = true
  await scrollToBottom()

  try {
    const response = await api.ai.chat(content)
    messages.value.push({ role: 'assistant', content: response.response })
    await scrollToBottom()
  } catch (e) {
    console.error('AI Chat Error:', e)
    toast.error(t('agent.error') || 'Failed to send message')
  } finally {
    isLoading.value = false
  }
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    send()
  }
}
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="isOpen"
        class="agent-overlay"
        @click="close"
      />
    </Transition>

    <Transition name="slide">
      <div
        v-if="isOpen"
        class="agent-drawer"
      >
        <div class="agent-head">
          <span class="agent-title">{{ t('agent.title') }}</span>
          <button
            class="agent-close-btn"
            :title="t('common.close')"
            @click="close"
          >
            <svg
              class="ico"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M18 6L6 18" />
              <path d="M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="agent-body">
          <div v-if="messages.length === 0" class="agent-empty">
            <p>{{ t('agent.placeholder') }}</p>
          </div>
          <div v-else class="agent-messages">
            <div
              v-for="(msg, index) in messages"
              :key="index"
              :class="['agent-message', `agent-message-${msg.role}`]"
            >
              <p>{{ msg.content }}</p>
            </div>
            <div v-if="isLoading" class="agent-message agent-message-assistant">
              <p>{{ t('agent.thinking') || 'Thinking...' }}</p>
            </div>
            <div ref="messagesEnd" />
          </div>
        </div>

        <div class="agent-input-wrap">
          <div class="agent-input-row">
            <button
              class="attach-btn"
              :title="t('agent.attach')"
            >
              <svg
                class="ico"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <rect
                  x="3"
                  y="3"
                  width="18"
                  height="18"
                  rx="2"
                  ry="2"
                />
                <circle
                  cx="9"
                  cy="9"
                  r="2"
                />
                <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21" />
              </svg>
            </button>

            <textarea
              ref="textareaRef"
              v-model="message"
              class="agent-input"
              :placeholder="t('agent.placeholder')"
              rows="1"
              @keydown="handleKeydown"
            />

            <button
              class="send-btn"
              :title="t('agent.send')"
              @click="send"
            >
              <svg
                class="ico"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="m22 2-11 11" />
                <path d="M22 2 15 22 11 13 2 9l20-7z" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
/* Overlay */
.agent-overlay {
  position: fixed;
  inset: 0;
  background: rgba(8, 10, 14, 0.42);
  z-index: 40;
}

/* Drawer */
.agent-drawer {
  position: fixed;
  right: 0;
  top: 0;
  width: min(620px, 52vw);
  height: 100vh;
  background: var(--surface);
  border-left: 1px solid var(--border);
  z-index: 41;
  display: flex;
  flex-direction: column;
}

@media (max-width: 980px) {
  .agent-drawer {
    width: 100vw;
  }
}

/* Header */
.agent-head {
  height: 64px;
  border-bottom: 1px solid var(--border);
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.agent-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--fg);
}

.agent-close-btn {
  width: 32px;
  height: 32px;
  padding: 0;
  border-radius: var(--radius);
  background: var(--accent);
  color: var(--bg);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.agent-close-btn:hover {
  background: var(--accent-hover);
  transform: rotate(90deg);
}

/* Body */
.agent-body {
  flex: 1;
  padding: 16px;
  overflow: auto;
  color: var(--muted);
  font-size: 13px;
  display: flex;
  flex-direction: column;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE/Edge */
}

.agent-body::-webkit-scrollbar {
  display: none; /* Chrome/Safari */
}

.agent-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.agent-messages {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.agent-message {
  max-width: 85%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.5;
}

.agent-message p {
  margin: 0;
  white-space: pre-wrap;
}

.agent-message-user {
  align-self: flex-end;
  background: var(--accent);
  color: var(--bg);
}

.agent-message-assistant {
  align-self: flex-start;
  background: var(--bg);
  border: 1px solid var(--border);
  color: var(--fg);
}

/* Input wrap */
.agent-input-wrap {
  border-top: 1px solid var(--border);
  padding: 12px;
}

.agent-input-row {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

/* Attach button */
.attach-btn {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--muted);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
}

.attach-btn:hover {
  color: var(--fg);
  border-color: var(--muted);
}

/* Input */
.agent-input {
  flex: 1;
  height: 42px;
  max-height: 200px;
  resize: none;
  border-radius: 20px;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--fg);
  padding: 10px 14px;
  font: inherit;
  font-size: 14px;
  line-height: 1.4;
  overflow-y: auto;
  transition: border-color 0.15s;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE/Edge */
}

.agent-input::-webkit-scrollbar {
  display: none; /* Chrome/Safari */
}

.agent-input::placeholder {
  color: var(--muted);
}

.agent-input:focus {
  outline: none;
  border-color: var(--muted);
}

/* Send button */
.send-btn {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  border: 1px solid transparent;
  background: var(--accent);
  color: var(--bg);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
}

.send-btn:hover {
  background: var(--accent-hover);
}

/* Icons */
.ico {
  width: 16px;
  height: 16px;
  display: block;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.2s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
}
</style>
