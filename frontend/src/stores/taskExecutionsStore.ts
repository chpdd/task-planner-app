import { defineStore } from 'pinia';
import { type Ref } from 'vue';
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query';
import { api } from '@/api/client';
import type { UpdateExecutionData } from '@/types/api';
import { useToast } from '@/composables/useToast';

const EXECUTIONS_QUERY_KEY = ['executions'] as const;

export const useTaskExecutionsStore = defineStore('taskExecutions', () => {
  const { success } = useToast();
  const queryClient = useQueryClient();

  const useExecutionsQuery = (allocationIdRef: Ref<number | null>) =>
    useQuery({
      queryKey: [...EXECUTIONS_QUERY_KEY, allocationIdRef],
      queryFn: () => api.taskExecutions.listByAllocation(allocationIdRef.value!),
      enabled: () => !!allocationIdRef.value,
      staleTime: 1000 * 60,
    });

  const useCreateExecutionMutation = () =>
    useMutation({
      mutationFn: ({
        allocationId,
        taskId,
        dayId,
        doingHours,
      }: {
        allocationId: number;
        taskId: number;
        dayId: number;
        doingHours: number;
      }) =>
        api.taskExecutions.create({
          allocation_id: allocationId,
          task_id: taskId,
          day_id: dayId,
          doing_hours: doingHours,
        }),
      onSuccess: (_data, variables) => {
        queryClient.invalidateQueries({ queryKey: [...EXECUTIONS_QUERY_KEY, variables.allocationId] });
        success('Execution created successfully');
      },
    });

  const useUpdateExecutionMutation = () =>
    useMutation({
      mutationFn: ({ executionId, data }: { executionId: number; data: UpdateExecutionData }) =>
        api.taskExecutions.update(executionId, data),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: EXECUTIONS_QUERY_KEY });
        success('Execution updated successfully');
      },
    });

  const useDeleteExecutionMutation = () =>
    useMutation({
      mutationFn: (executionId: number) => api.taskExecutions.delete(executionId),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: EXECUTIONS_QUERY_KEY });
        success('Execution deleted successfully');
      },
    });

  return {
    useExecutionsQuery,
    useCreateExecutionMutation,
    useUpdateExecutionMutation,
    useDeleteExecutionMutation,
  };
});
