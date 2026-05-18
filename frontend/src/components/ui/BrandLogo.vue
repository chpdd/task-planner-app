<script setup lang="ts">
// BrandLogo - Displays [todos] branding in styled box
</script>

<template>
  <div class="brand">
    <div class="brand-box" />
    <span class="brand-text">[todos]</span>
  </div>
</template>

<style scoped>
.brand {
  display: flex;
  align-items: center;
  gap: 8px;
}

.brand-box {
  width: 24px;
  height: 24px;
  background: var(--accent);
  border: 1px solid var(--border);
  border-radius: 4px;
}

.brand-text {
  font-family: var(--font-mono);
  font-size: 14px;
  color: var(--fg);
  letter-spacing: -0.02em;
}
</style>
