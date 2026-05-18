<script setup lang="ts">
</script>

<template>
  <div class="app-shell">
    <slot name="sidebar" />
    <main class="main">
      <slot name="top" />
      <section class="content">
        <slot />
      </section>
    </main>
  </div>
</template>

<style scoped>
.app-shell {
  display: flex;
  min-height: 100vh;
  background: var(--bg);
}

.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}
</style>
