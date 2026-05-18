import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { VueQueryPlugin, QueryCache, MutationCache, QueryClient } from '@tanstack/vue-query';
import { persistQueryClient } from '@tanstack/query-persist-client-core';
import { createSyncStoragePersister } from '@tanstack/query-sync-storage-persister';
import App from './App.vue';
import router from './router';
import { i18n } from './i18n';
import './assets/tokens.css';
import './assets/base.css';
import { ApiError, ValidationError } from '@/api/client';
import { useToast } from '@/composables/useToast';
import { API_CONFIG, STORAGE_KEYS } from '@/config/constants';

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
app.use(i18n);

const { error: showError } = useToast();

const handleGlobalError = (e: unknown) => {
  if (e instanceof ValidationError) {
    const msg = typeof e.errors === 'string' ? e.errors : 'Validation error';
    showError(msg);
  } else if (e instanceof ApiError) {
    showError(`API Error: ${e.status}`);
  } else if (e instanceof Error) {
    showError(e.message);
  } else {
    showError('An unexpected error occurred');
  }
};

const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: handleGlobalError,
  }),
  mutationCache: new MutationCache({
    onError: handleGlobalError,
  }),
  defaultOptions: {
    queries: {
      staleTime: API_CONFIG.STALE_TIME,
      gcTime: API_CONFIG.CACHE_TIME,
      retry: API_CONFIG.RETRY_COUNT,
    },
  },
});

const localStoragePersister = createSyncStoragePersister({
  storage: window.localStorage,
  key: STORAGE_KEYS.QUERY_CACHE,
});

persistQueryClient({
  queryClient: queryClient as any,
  persister: localStoragePersister,
  maxAge: API_CONFIG.CACHE_TIME,
});

app.use(VueQueryPlugin, { queryClient });

app.mount('#app');
