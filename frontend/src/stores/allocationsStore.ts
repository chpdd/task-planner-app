import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query';
import { api } from '@/api/client';
import type { Allocation, CreateAllocationData } from '@/types/api';
import { useToast } from '@/composables/useToast';

const ALLOCATIONS_QUERY_KEY = ['allocations'] as const;

export const useAllocationsStore = defineStore('allocations', () => {
  const { success } = useToast();
  const queryClient = useQueryClient();

  const activeAllocationId = ref<number | null>(null);

  const useAllocationsQuery = () =>
    useQuery({
      queryKey: ALLOCATIONS_QUERY_KEY,
      queryFn: () => api.allocations.list(),
      staleTime: 1000 * 60,
    });

  const useAllocationQuery = (id: number) =>
    useQuery({
      queryKey: [...ALLOCATIONS_QUERY_KEY, id] as const,
      queryFn: () => api.allocations.get(id),
      enabled: !!id,
    });

  const useCreateAllocationMutation = () =>
    useMutation({
      mutationFn: (data: CreateAllocationData) => api.allocations.create(data),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ALLOCATIONS_QUERY_KEY });
        success('Allocation created successfully');
      },
    });

  const useUpdateAllocationMutation = () =>
    useMutation({
      mutationFn: ({ id, data }: { id: number; data: Partial<CreateAllocationData> }) =>
        api.allocations.update(id, data),
      onSuccess: (_data, variables) => {
        queryClient.invalidateQueries({ queryKey: ALLOCATIONS_QUERY_KEY });
        queryClient.invalidateQueries({ queryKey: [...ALLOCATIONS_QUERY_KEY, variables.id] });
        success('Allocation updated successfully');
      },
    });

  const useDeleteAllocationMutation = () => {
    const deleteMutation = useMutation({
      mutationFn: async (id: number): Promise<void> => {
        await api.allocations.delete(id);
        return undefined;
      },
      onSuccess: (_data, id) => {
        queryClient.invalidateQueries({ queryKey: ALLOCATIONS_QUERY_KEY });
        // Reset active allocation if the deleted one was active
        if (activeAllocationId.value === id) {
          activeAllocationId.value = null;
        }
        success('Allocation deleted successfully');
      },
    });

    return deleteMutation;
  };

  function getActiveAllocation(allocations: Allocation[] | undefined): Allocation | null {
    if (!allocations || activeAllocationId.value === null) {
      return null;
    }
    return allocations.find((d) => d.id === activeAllocationId.value) ?? null;
  }

  async function refreshAllocations(): Promise<void> {
    await queryClient.invalidateQueries({ queryKey: ALLOCATIONS_QUERY_KEY });
  }

  return {
    activeAllocationId,
    useAllocationsQuery,
    useAllocationQuery,
    useCreateAllocationMutation,
    useUpdateAllocationMutation,
    useDeleteAllocationMutation,
    getActiveAllocation,
    refreshAllocations,
  };
});
