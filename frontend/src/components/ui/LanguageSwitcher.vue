<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { locale, availableLocales } = useI18n()

function toggleLocale() {
  const currentIndex = availableLocales.indexOf(locale.value)
  const nextIndex = (currentIndex + 1) % availableLocales.length
  locale.value = availableLocales[nextIndex]
}
</script>

<template>
  <button
    class="lang-switcher"
    :title="`Switch to ${locale === 'ru' ? 'English' : 'Russian'}`"
    @click="toggleLocale"
  >
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
      <circle cx="12" cy="12" r="10" />
      <line x1="2" y1="12" x2="22" y2="12" />
      <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
    </svg>
    <span class="lang-text">{{ locale.toUpperCase() }}</span>
  </button>
</template>

<style scoped>
.lang-switcher {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--surface);
  border: 3px solid var(--border);
  border-radius: 999px;
  color: var(--muted);
  cursor: pointer;
  transition: all 0.15s;
}

.lang-switcher:hover {
  background: var(--surface-hover);
  color: var(--fg);
  border-color: var(--muted);
}

.lang-text {
  font-size: 12px;
  font-weight: 700;
}
</style>
