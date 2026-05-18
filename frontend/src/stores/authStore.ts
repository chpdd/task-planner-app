import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import { api, ApiError, ValidationError } from '@/api/client';

export type AuthError = { type: 'credentials'; message: string } | { type: 'network'; message: string } | { type: 'username_exists'; message: string } | null;

interface User {
  id: string;
  email: string;
  username: string;
}

const TOKEN_KEY = 'auth_token';
const USER_KEY = 'auth_user';

function loadStoredAuth() {
  try {
    const token = localStorage.getItem(TOKEN_KEY);
    const user = localStorage.getItem(USER_KEY);
    return {
      token: token || null,
      user: user ? JSON.parse(user) : null,
    };
  } catch {
    return { token: null, user: null };
  }
}

function saveAuth(token: string | null, user: User | null) {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
  if (user) {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  } else {
    localStorage.removeItem(USER_KEY);
  }
}

const stored = loadStoredAuth();

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(stored.user);
  const token = ref<string | null>(stored.token);
  const isLoading = ref(false);
  const lastError = ref<AuthError>(null);

  // Restore API client token on init
  if (token.value) {
    api.setToken(token.value);
  }

  const isAuthenticated = computed(() => !!token.value);

  async function login(username: string, password: string): Promise<boolean> {
    isLoading.value = true;
    lastError.value = null;
    try {
      const response = await api.auth.login({ username, password });
      token.value = response.access_token;
      user.value = { id: '', username, email: '' };
      api.setToken(response.access_token);
      saveAuth(response.access_token, user.value);
      return true;
    } catch (e) {
      if (e instanceof ValidationError) {
        lastError.value = { type: 'credentials', message: 'Validation error' };
      } else if (e instanceof ApiError) {
        if (e.status === 401 || e.status === 404) {
          const message = typeof e.body === 'object' && e.body && 'detail' in e.body
            ? String(e.body.detail)
            : 'Invalid username or password';
          lastError.value = { type: 'credentials', message };
        } else {
          lastError.value = { type: 'network', message: 'Login failed. Please try again.' };
        }
      } else {
        lastError.value = { type: 'network', message: 'Network error. Please check your connection.' };
      }
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  async function register(username: string, password: string): Promise<boolean> {
    isLoading.value = true;
    lastError.value = null;
    try {
      const response = await api.auth.register({ username, password });
      token.value = response.access_token;
      user.value = { id: '', username, email: '' };
      api.setToken(response.access_token);
      saveAuth(response.access_token, user.value);
      return true;
    } catch (e) {
      if (e instanceof ValidationError) {
        lastError.value = { type: 'credentials', message: 'Validation error' };
      } else if (e instanceof ApiError) {
        if (e.status === 409) {
          const message = typeof e.body === 'object' && e.body && 'detail' in e.body
            ? String(e.body.detail)
            : 'Username already exists';
          lastError.value = { type: 'username_exists', message };
        } else {
          lastError.value = { type: 'network', message: 'Registration failed. Please try again.' };
        }
      } else {
        lastError.value = { type: 'network', message: 'Network error. Please check your connection.' };
      }
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  function logout() {
    token.value = null;
    user.value = null;
    api.setToken(null);
    saveAuth(null, null);
  }

  function clearError() {
    lastError.value = null;
  }

  return { user, token, isLoading, isAuthenticated, lastError, login, register, logout, clearError };
});
