import { defineStore } from 'pinia';
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query';
import { api } from '@/api/client';
import { Task, createTasks } from '@/domain/Task';
import type { CreateTaskData } from '@/types/api';
import { useToast } from '@/composables/useToast';

const TASKS_QUERY_KEY = ['tasks'] as const;

type UpdateTaskVariables = { id: number; data: Partial<CreateTaskData> };

export const useTasksStore = defineStore('tasks', () => {
  const { success } = useToast();
  const queryClient = useQueryClient();

  const useTasksQuery = () =>
    useQuery({
      queryKey: TASKS_QUERY_KEY,
      queryFn: async () => {
        const data = await api.tasks.list();
        return createTasks(data);
      },
      staleTime: 1000 * 60,
    });

  const useTaskQuery = (id: number) =>
    useQuery({
      queryKey: [...TASKS_QUERY_KEY, id] as const,
      queryFn: async () => {
        const data = await api.tasks.get(id);
        return new Task(data);
      },
      enabled: !!id,
    });

  const useCreateTaskMutation = () =>
    useMutation({
      mutationFn: async (data: CreateTaskData) => {
        const result = await api.tasks.create(data);
        return new Task(result);
      },
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: TASKS_QUERY_KEY });
        success('Task created successfully');
      },
    });

  const useUpdateTaskMutation = () =>
    useMutation<Task, Error, UpdateTaskVariables>({
      mutationFn: async ({ id, data }) => {
        const result = await api.tasks.update(id, data);
        return new Task(result);
      },
      onSuccess: (_task, variables) => {
        queryClient.invalidateQueries({ queryKey: TASKS_QUERY_KEY });
        queryClient.invalidateQueries({ queryKey: [...TASKS_QUERY_KEY, variables.id] });
        success('Task updated successfully');
      },
    });

  const useDeleteTaskMutation = () =>
    useMutation({
      mutationFn: (id: number) => api.tasks.delete(id),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: TASKS_QUERY_KEY });
        success('Task deleted successfully');
      },
    });

  async function refreshTasks(): Promise<void> {
    await queryClient.invalidateQueries({ queryKey: TASKS_QUERY_KEY });
  }

  return {
    useTasksQuery,
    useTaskQuery,
    useCreateTaskMutation,
    useUpdateTaskMutation,
    useDeleteTaskMutation,
    refreshTasks,
  };
});
