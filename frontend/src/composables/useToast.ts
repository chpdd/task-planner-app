import { ref } from 'vue'
import type { ToastType } from '@/components/ui/ToastContainer.vue'

const toasts = ref<Array<{ id: string; type: ToastType; message: string }>>([])

let toastIdCounter = 0

export function useToast() {
  function addToast(type: ToastType, message: string, duration = 4000) {
    const id = `toast-${++toastIdCounter}`
    toasts.value.push({ id, type, message })

    setTimeout(() => {
      removeToast(id)
    }, duration)

    return id
  }

  function removeToast(id: string) {
    const index = toasts.value.findIndex((t) => t.id === id)
    if (index !== -1) {
      toasts.value.splice(index, 1)
    }
  }

  function success(message: string) {
    return addToast('success', message)
  }

  function error(message: string) {
    return addToast('error', message)
  }

  function info(message: string) {
    return addToast('info', message)
  }

  return {
    toasts,
    success,
    error,
    info,
    removeToast,
  }
}
