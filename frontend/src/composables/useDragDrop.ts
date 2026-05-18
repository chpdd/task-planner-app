import { ref, readonly } from 'vue'

const isDraggingTask = ref(false)
const draggedTaskId = ref<number | null>(null)
const draggedTask = ref<object | null>(null)

export function useDragDrop() {
  function onDragStart(event: DragEvent, task: object) {
    isDraggingTask.value = true
    draggedTask.value = task

    if (task && typeof task === 'object' && 'id' in task) {
      draggedTaskId.value = (task as { id: number }).id
    }

    event.dataTransfer?.setData('application/json', JSON.stringify(task))
    event.dataTransfer!.effectAllowed = 'move'
  }

  function onDragEnd() {
    isDraggingTask.value = false
    draggedTaskId.value = null
    draggedTask.value = null
  }

  function onDragOver(event: DragEvent) {
    event.preventDefault()
    event.dataTransfer!.dropEffect = 'move'
  }

  function onDragEnter(event: DragEvent, targetEl: HTMLElement) {
    event.preventDefault()
    targetEl.classList.add('drag-over')
  }

  function onDragLeave(event: DragEvent, targetEl: HTMLElement) {
    const relatedTarget = event.relatedTarget as HTMLElement | null
    if (relatedTarget && targetEl.contains(relatedTarget)) {
      return
    }
    targetEl.classList.remove('drag-over')
  }

  function onDrop(event: DragEvent): object | null {
    event.preventDefault()

    const taskData = event.dataTransfer?.getData('application/json')
    if (taskData) {
      try {
        return JSON.parse(taskData)
      } catch (e) {
        console.error('Failed to parse dropped task:', e)
      }
    }

    onDragEnd()
    return null
  }

  function parseDroppedTask(event: DragEvent): object | null {
    const taskData = event.dataTransfer?.getData('application/json')
    if (!taskData) return null

    try {
      return JSON.parse(taskData)
    } catch (e) {
      console.error('Failed to parse dropped task:', e)
      return null
    }
  }

  return {
    isDraggingTask: readonly(isDraggingTask),
    draggedTaskId: readonly(draggedTaskId),
    draggedTask: readonly(draggedTask),
    onDragStart,
    onDragEnd,
    onDragOver,
    onDragEnter,
    onDragLeave,
    onDrop,
    parseDroppedTask,
  }
}

export function isSameDayDrop(
  sourceTaskId: number,
  targetDate: Date,
  getCurrentTaskDate: (_taskId: number) => Date | null
): boolean {
  const currentDate = getCurrentTaskDate(sourceTaskId)
  if (!currentDate) return false

  return (
    targetDate.getDate() === currentDate.getDate() &&
    targetDate.getMonth() === currentDate.getMonth() &&
    targetDate.getFullYear() === currentDate.getFullYear()
  )
}
