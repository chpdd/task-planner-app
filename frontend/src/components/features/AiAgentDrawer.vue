<script setup lang="ts">
import { ref, watch, nextTick, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useUiStore } from '@/stores/uiStore'
import { api } from '@/api/client'
import { useToast } from '@/composables/useToast'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const { t } = useI18n()
const uiStore = useUiStore()
const toast = useToast()

const isOpen = ref(uiStore.isAiDrawerOpen)
const message = ref('')
const messages = ref<Array<{ role: 'user' | 'assistant'; content: string }>>([])
const isLoading = ref(false)
const messagesEnd = ref<HTMLElement | null>(null)
const textareaRef = ref<HTMLTextAreaElement | null>(null)

// History & Conversations
const conversations = ref<any[]>([])
const currentConversationId = ref<number | null>(uiStore.selectedAiConversationId)
const isHistoryOpen = ref(false)

const activeConversationTitle = computed(() => {
  if (!currentConversationId.value) return t('agent.newChat') || 'Новый чат'
  const conv = conversations.value.find(c => c.id === currentConversationId.value)
  return conv?.title || `${t('agent.chat')} #${currentConversationId.value}`
})

onMounted(() => {
  loadConversations()
  if (currentConversationId.value && uiStore.isAiDrawerOpen) {
    selectConversation(currentConversationId.value)
  }
})

async function loadConversations() {
  try {
    conversations.value = await api.ai.listConversations()
  } catch (e) {
    console.error('Failed to load conversations:', e)
  }
}

async function selectConversation(id: number | null) {
  currentConversationId.value = id
  uiStore.selectedAiConversationId = id
  isHistoryOpen.value = false
  messages.value = []
  
  if (id) {
    isLoading.value = true
    try {
      const history = await api.ai.listMessages(id)
      messages.value = history.map(m => ({
        role: m.role as 'user' | 'assistant',
        content: m.content
      }))
      await scrollToBottom()
    } catch (e) {
      toast.error('Failed to load messages')
    } finally {
      isLoading.value = false
    }
  }
}

watch(() => uiStore.isAiDrawerOpen, (val) => {
  isOpen.value = val
  if (val) {
    scrollToBottom()
    nextTick(() => textareaRef.value?.focus())
    loadConversations()
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
    const assistantMessage = ref({ role: 'assistant' as const, content: '' })
    messages.value.push(assistantMessage.value)
    const msgIndex = messages.value.length - 1

    const stream = api.ai.chatStream(content, currentConversationId.value || undefined)
    
    let started = false
    for await (const chunk of stream) {
      if (chunk.type === 'meta' && !currentConversationId.value) {
        currentConversationId.value = chunk.conversation_id
        loadConversations()
      } else if (chunk.type === 'token') {
        if (!started) {
          started = true
        }
        messages.value[msgIndex].content += chunk.text
        await scrollToBottom()
      }
    }
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

function renderMarkdown(content: string) {
  if (!content) return ''
  const rawHtml = marked.parse(content, { gfm: true, breaks: true }) as string
  return DOMPurify.sanitize(rawHtml)
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
          <div class="header-left">
            <button class="history-toggle" @click="isHistoryOpen = !isHistoryOpen">
              <span class="chat-title">{{ activeConversationTitle }}</span>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" :class="{ rotated: isHistoryOpen }">
                <path d="M6 9l6 6 6-6" />
              </svg>
            </button>
          </div>
          
          <div class="header-right">
            <button class="new-chat-btn" :title="t('agent.newChat')" @click="selectConversation(null)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
                <line x1="12" y1="5" x2="12" y2="19" />
                <line x1="5" y1="12" x2="19" y2="12" />
              </svg>
            </button>
            <button
              class="agent-close-btn"
              :title="t('common.close')"
              @click="close"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 6L6 18" />
                <path d="M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- History Dropdown -->
          <Transition name="fade-down">
            <div v-if="isHistoryOpen" class="history-dropdown">
              <div class="history-list">
                <button 
                  v-for="conv in conversations" 
                  :key="conv.id" 
                  class="history-item"
                  :class="{ active: currentConversationId === conv.id }"
                  @click="selectConversation(conv.id)"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                  </svg>
                  <span class="history-item-title">{{ conv.title || `Chat ${conv.id}` }}</span>
                </button>
                <div v-if="conversations.length === 0" class="history-empty-hint">
                  Нет истории чатов
                </div>
              </div>
            </div>
          </Transition>
        </div>

        <div class="agent-body">
          <div v-if="messages.length === 0 && !isLoading" class="agent-empty">
            <div class="agent-empty-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="1.5" width="40" height="40">
                    <path d="M12 8V4m0 0H8m4 0h4M9 12h.01M15 12h.01M5 10a2 2 0 012-2h10a2 2 0 012 2v8a2 2 0 01-2 2H7a2 2 0 01-2-2v-8z" />
                    <path d="M9 16c1 1 2 1 3 1s2 0 3-1" />
                </svg>
            </div>
            <p>{{ t('agent.placeholder') }}</p>
          </div>
          <div v-else class="agent-messages">
            <TransitionGroup name="message">
                <div
                v-for="(msg, index) in messages"
                :key="index"
                :class="['agent-message', `agent-message-${msg.role}`, { 'is-typing': msg.role === 'assistant' && !msg.content && isLoading }]"
                >
                    <div v-if="msg.role === 'assistant' && msg.content" class="markdown-content" v-html="renderMarkdown(msg.content)" />
                    <p v-else-if="msg.role === 'user'">{{ msg.content }}</p>
                    
                    <!-- Thinking indicator inside the bubble if empty -->
                    <div v-if="msg.role === 'assistant' && !msg.content" class="thinking-loader">
                        <span class="dot"></span>
                        <span class="dot"></span>
                        <span class="dot"></span>
                    </div>
                </div>
            </TransitionGroup>
            <div ref="messagesEnd" />
          </div>
        </div>

        <div class="agent-input-wrap">
          <div class="agent-input-row">
            <button
              class="attach-btn"
              :title="t('agent.attach')"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                <circle cx="9" cy="9" r="2" />
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
              :disabled="isLoading || !message.trim()"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
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
  border-left: 3px solid var(--border);
  z-index: 41;
  display: flex;
  flex-direction: column;
}

@media (max-width: 980px) {
  .agent-drawer { width: 100vw; }
}

/* Header */
.agent-head {
  height: 64px;
  border-bottom: 3px solid var(--border);
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.history-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  background: transparent;
  border: none;
  color: var(--fg);
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 8px;
  transition: background 0.2s;
  max-width: 100%;
}

.history-toggle:hover {
  background: var(--surface-hover);
}

.chat-title {
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.new-chat-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 3px solid var(--border);
  border-radius: 8px;
  color: var(--muted);
  cursor: pointer;
  transition: all 0.2s;
}

.new-chat-btn:hover {
  background: var(--surface-hover);
  color: var(--accent);
  border-color: var(--accent);
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

.agent-close-btn svg { width: 16px; height: 16px; }

.agent-close-btn:hover {
  background: var(--accent-hover);
  transform: rotate(90deg);
}

/* History Dropdown */
.history-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--surface);
  border-bottom: 3px solid var(--border);
  max-height: 300px;
  overflow-y: auto;
  z-index: 50;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
}

.history-list {
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: var(--muted);
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
}

.history-item:hover {
  background: var(--surface-hover);
  color: var(--fg);
}

.history-item.active {
  background: var(--bg);
  color: var(--accent);
}

.history-item-title {
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-empty-hint {
  padding: 20px;
  text-align: center;
  color: var(--muted);
  font-size: 13px;
}

/* Body */
.agent-body {
  flex: 1;
  padding: 20px 16px;
  overflow: auto;
  scrollbar-width: none;
}

.agent-body::-webkit-scrollbar { display: none; }

.agent-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  opacity: 0.5;
}

.agent-empty-icon {
    animation: float 3s infinite ease-in-out;
}

@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

.agent-messages {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.agent-message {
  max-width: 85%;
  padding: 12px 16px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.6;
  position: relative;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.agent-message-user {
  align-self: flex-end;
  background: var(--accent);
  color: var(--bg);
  border-bottom-right-radius: 4px;
}

.agent-message-assistant {
  align-self: flex-start;
  background: var(--surface-hover);
  border: 3px solid var(--border);
  color: var(--fg);
  border-bottom-left-radius: 4px;
}

.thinking-loader {
    display: flex;
    gap: 4px;
    padding: 4px 0;
}

.dot {
    width: 6px;
    height: 6px;
    background: var(--accent);
    border-radius: 50%;
    animation: dot-wave 1.2s infinite ease-in-out;
    opacity: 0.6;
}

.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes dot-wave {
    0%, 60%, 100% { transform: translateY(0); }
    30% { transform: translateY(-6px); }
}

/* Markdown styling */
.markdown-content :deep(p) { margin-bottom: 8px; }
.markdown-content :deep(p:last-child) { margin-bottom: 0; }
.markdown-content :deep(strong) { color: var(--accent); font-weight: 600; }
.markdown-content :deep(code) { background: var(--bg); padding: 2px 4px; border-radius: 4px; font-family: var(--font-mono); font-size: 0.9em; }

/* Input wrap */
.agent-input-wrap {
  border-top: 3px solid var(--border);
  padding: 16px;
  background: var(--surface);
}

.agent-input-row {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.attach-btn {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  border: 3px solid var(--border);
  background: var(--bg);
  color: var(--muted);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.attach-btn:hover { color: var(--fg); border-color: var(--muted); }

.agent-input {
  flex: 1;
  min-height: 42px;
  max-height: 200px;
  resize: none;
  border-radius: 16px;
  border: 3px solid var(--border);
  background: var(--bg);
  color: var(--fg);
  padding: 11px 14px;
  font: inherit;
  font-size: 14px;
  line-height: 1.4;
  overflow-y: auto;
  scrollbar-width: none;
}

.agent-input:focus { outline: none; border-color: var(--accent); }

.send-btn {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: var(--accent);
  color: var(--bg);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.send-btn:disabled { opacity: 0.5; filter: grayscale(1); cursor: not-allowed; }
.send-btn:not(:disabled):hover { background: var(--accent-hover); transform: scale(1.05); }

/* Animations */
.slide-enter-active, .slide-leave-active { transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.slide-enter-from, .slide-leave-to { transform: translateX(100%); }

.fade-down-enter-active, .fade-down-leave-active { transition: all 0.2s ease-out; }
.fade-down-enter-from, .fade-down-leave-to { opacity: 0; transform: translateY(-10px); }

.message-enter-active { transition: all 0.3s ease-out; }
.message-enter-from { opacity: 0; transform: translateY(10px) scale(0.95); }

.rotated { transform: rotate(180deg); }
</style>
