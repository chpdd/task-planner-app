<script setup lang="ts">
import { useToast } from '@/composables';
import ToastContainer from '@/components/ui/ToastContainer.vue';

const { toasts } = useToast();
</script>

<template>
  <div id="app">
    <router-view />
    <ToastContainer :toasts="toasts" />
  </div>
</template>

<style>
#app {
  min-height: 100vh;
  background: var(--bg, #0e0e0c);
  color: var(--fg, #e6e6e5);
}
</style>
