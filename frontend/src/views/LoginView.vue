<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useToast } from '@/composables'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const authMode = ref<'login' | 'register'>('login')
const username = ref('')
const password = ref('')
const confirmPassword = ref('')

// Validation errors
const usernameError = ref('')
const passwordError = ref('')
const confirmPasswordError = ref('')
const serverError = ref('')

function validateUsername(): boolean {
  if (!username.value.trim()) {
    usernameError.value = t('auth.usernameRequired')
    return false
  }
  usernameError.value = ''
  return true
}

function validatePassword(): boolean {
  if (!password.value) {
    passwordError.value = t('auth.passwordRequired')
    return false
  }
  if (password.value.length < 8) {
    passwordError.value = t('auth.passwordTooShort')
    return false
  }
  passwordError.value = ''
  return true
}

function validateConfirmPassword(): boolean {
  if (!confirmPassword.value) {
    confirmPasswordError.value = t('auth.confirmPasswordRequired')
    return false
  }
  if (password.value !== confirmPassword.value) {
    confirmPasswordError.value = t('auth.passwordMismatch')
    return false
  }
  confirmPasswordError.value = ''
  return true
}

function clearErrors() {
  usernameError.value = ''
  passwordError.value = ''
  confirmPasswordError.value = ''
  serverError.value = ''
  authStore.clearError()
}

const isLogin = computed(() => authMode.value === 'login')

const title = computed(() => isLogin.value ? t('auth.loginTitle') : t('auth.registerTitle'))
const submitButtonText = computed(() => isLogin.value ? t('auth.loginButton') : t('auth.registerButton'))
const toggleButtonText = computed(() => isLogin.value ? t('auth.register') : t('auth.login'))
const usernamePlaceholder = computed(() => t('auth.username'))
const passwordPlaceholder = computed(() => t('auth.password'))
const confirmPasswordPlaceholder = computed(() => t('auth.confirmPassword'))

// Watch for server errors
watch(() => authStore.lastError, (error) => {
  if (!error) return

  switch (error.type) {
    case 'credentials':
      serverError.value = t('auth.invalidCredentials')
      // Highlight both fields as error
      usernameError.value = ' '
      passwordError.value = ' '
      break
    case 'username_exists':
      usernameError.value = error.message
      break
    case 'network':
      serverError.value = error.message
      break
  }
}, { immediate: true })

function toggleMode() {
  authMode.value = authMode.value === 'login' ? 'register' : 'login'
  confirmPassword.value = ''
  clearErrors()
}

async function handleSubmit() {
  clearErrors()
  let isValid = true

  if (!validateUsername()) isValid = false
  if (!validatePassword()) isValid = false
  if (authMode.value === 'register' && !validateConfirmPassword()) isValid = false

  if (!isValid) return

  let success: boolean

  if (authMode.value === 'login') {
    success = await authStore.login(username.value, password.value)
    if (success) {
      toast.success(t('auth.loginSuccess'))
      router.push('/')
    }
  } else {
    success = await authStore.register(username.value, password.value)
    if (success) {
      toast.success(t('auth.registerSuccess'))
      router.push('/')
    }
  }
}
</script>

<template>
  <div class="login-overlay">
    <div class="login-card">
      <div class="brand">
        <div class="brand-box" />
        <span class="brand-text">[todos]</span>
      </div>

      <h2 class="auth-title">
        {{ title }}
      </h2>

      <!-- Server error message -->
      <div v-if="serverError" class="server-error">
        {{ serverError }}
      </div>

      <div class="input-group">
        <BaseInput
          v-model="username"
          type="text"
          :placeholder="usernamePlaceholder"
          :error="!!usernameError"
          autocomplete="username"
          @blur="validateUsername"
          @input="usernameError = ''"
        />
        <span v-if="usernameError && usernameError !== ' '" class="error-message">{{ usernameError }}</span>
      </div>

      <div class="input-group">
        <BaseInput
          v-model="password"
          type="password"
          :placeholder="passwordPlaceholder"
          :error="!!passwordError"
          autocomplete="current-password"
          @blur="validatePassword"
          @input="passwordError = ''"
        />
        <span v-if="passwordError && passwordError !== ' '" class="error-message">{{ passwordError }}</span>
      </div>

      <div v-if="!isLogin" class="input-group">
        <BaseInput
          v-model="confirmPassword"
          type="password"
          :placeholder="confirmPasswordPlaceholder"
          :error="!!confirmPasswordError"
          autocomplete="new-password"
          @blur="validateConfirmPassword"
          @input="confirmPasswordError = ''"
        />
        <span v-if="confirmPasswordError" class="error-message">{{ confirmPasswordError }}</span>
      </div>

      <BaseButton
        variant="primary"
        class="auth-main-btn"
        type="submit"
        :disabled="authStore.isLoading"
        @click="handleSubmit"
      >
        {{ submitButtonText }}
      </BaseButton>

      <BaseButton
        class="auth-main-btn"
        variant="default"
        :disabled="authStore.isLoading"
        @click="toggleMode"
      >
        {{ toggleButtonText }}
      </BaseButton>
    </div>
  </div>
</template>

<style scoped>
.login-overlay {
  position: fixed;
  inset: 0;
  background: var(--bg);
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-card {
  width: min(430px, calc(100vw - 30px));
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 22px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: 500;
}

.brand-box {
  width: 24px;
  height: 24px;
  border-radius: 5px;
  background: var(--accent);
}

.brand-text {
  font-family: var(--font-mono);
  font-size: 14px;
  color: var(--fg);
}

.auth-title {
  font-size: 24px;
  font-weight: 500;
  text-align: center;
  margin: 0;
}

.auth-main-btn {
  width: 100%;
  text-align: center;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.error-message {
  color: var(--danger, #ef4444);
  font-size: 12px;
  padding-left: 2px;
}

.server-error {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid var(--danger, #ef4444);
  border-radius: var(--radius);
  padding: 10px 12px;
  color: var(--danger, #ef4444);
  font-size: 13px;
  text-align: center;
}
</style>
