import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query';
import { api } from '@/api/client';
import type { Distribution } from '@/types/api';
import { useToast } from '@/composables/useToast';

const DISTRIBUTIONS_QUERY_KEY = ['distributions'] as const;

export interface CreateDistributionData {
  name: string;
  method: string;
}

export interface UpdateDistributionData {
  name?: string;
  method?: string;
}

export const useDistributionsStore = defineStore('distributions', () => {
  const { success } = useToast();
  const queryClient = useQueryClient();

  const activeDistributionId = ref<number | null>(null);

  const useDistributionsQuery = () =>
    useQuery({
      queryKey: DISTRIBUTIONS_QUERY_KEY,
      queryFn: () => api.distributions.list(),
      staleTime: 1000 * 60,
    });

  const useDistributionQuery = (id: number) =>
    useQuery({
      queryKey: [...DISTRIBUTIONS_QUERY_KEY, id] as const,
      queryFn: () => api.distributions.get(id),
      enabled: !!id,
    });

  const useCreateDistributionMutation = () =>
    useMutation({
      mutationFn: (data: CreateDistributionData) => api.distributions.create(data),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: DISTRIBUTIONS_QUERY_KEY });
        success('Distribution created successfully');
      },
    });

  const useUpdateDistributionMutation = () =>
    useMutation({
      mutationFn: ({ id, data }: { id: number; data: UpdateDistributionData }) =>
        api.distributions.update(id, data),
      onSuccess: (_data, variables) => {
        queryClient.invalidateQueries({ queryKey: DISTRIBUTIONS_QUERY_KEY });
        queryClient.invalidateQueries({ queryKey: [...DISTRIBUTIONS_QUERY_KEY, variables.id] });
        success('Distribution updated successfully');
      },
    });

  const useDeleteDistributionMutation = () => {
    const deleteMutation = useMutation({
      mutationFn: async (id: number): Promise<void> => {
        await api.distributions.delete(id);
        return undefined;
      },
      onSuccess: (_data, id) => {
        queryClient.invalidateQueries({ queryKey: DISTRIBUTIONS_QUERY_KEY });
        // Reset active distribution if the deleted one was active
        if (activeDistributionId.value === id) {
          activeDistributionId.value = null;
        }
        success('Distribution deleted successfully');
      },
    });

    return deleteMutation;
  };

  function getActiveDistribution(distributions: Distribution[] | undefined): Distribution | null {
    if (!distributions || activeDistributionId.value === null) {
      return null;
    }
    return distributions.find((d) => d.id === activeDistributionId.value) ?? null;
  }

  async function refreshDistributions(): Promise<void> {
    await queryClient.invalidateQueries({ queryKey: DISTRIBUTIONS_QUERY_KEY });
  }

  return {
    activeDistributionId,
    useDistributionsQuery,
    useDistributionQuery,
    useCreateDistributionMutation,
    useUpdateDistributionMutation,
    useDeleteDistributionMutation,
    getActiveDistribution,
    refreshDistributions,
  };
});
