import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query';
import { api } from '@/api/client';
import { Calendar, Allocation } from '@/domain/Calendar';
import type { CreateAllocationData } from '@/types/api';
import { useToast } from '@/composables/useToast';

const CALENDARS_QUERY_KEY = ['calendars'] as const;
const ALLOCATIONS_QUERY_KEY = ['allocations'] as const;

export const useCalendarsStore = defineStore('calendars', () => {
  const { success } = useToast();
  const queryClient = useQueryClient();

  const selectedCalendarId = ref<number | null>(null);
  const selectedAllocation = ref<Allocation | null>(null);
  const selectedAllocationId = ref<number | null>(null);

  // Queries
  const useCalendarsQuery = () =>
    useQuery({
      queryKey: CALENDARS_QUERY_KEY,
      queryFn: async () => {
        const data = await api.calendars.list();
        return data.map(c => new Calendar(c));
      },
      staleTime: 1000 * 60,
    });

  const useAllocationsQuery = (calendarId: number | null) =>
    useQuery({
      queryKey: [...ALLOCATIONS_QUERY_KEY, calendarId] as const,
      queryFn: async () => {
        const data = await api.calendars.listAllocations(calendarId!);
        return data.map(a => new Allocation(a));
      },
      enabled: !!calendarId,
      staleTime: 1000 * 60,
    });

  // Mutations
  const useCreateCalendarMutation = () =>
    useMutation({
      mutationFn: (name: string) => api.calendars.create({ name }),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: CALENDARS_QUERY_KEY });
        success('Calendar created successfully');
      },
    });

  const useUpdateCalendarMutation = () =>
    useMutation({
      mutationFn: ({ id, name }: { id: number; name: string }) => api.calendars.update(id, { name }),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: CALENDARS_QUERY_KEY });
        success('Calendar updated successfully');
      },
    });

  const useDeleteCalendarMutation = () =>
    useMutation({
      mutationFn: (id: number) => api.calendars.delete(id),
      onSuccess: (_data, id) => {
        queryClient.invalidateQueries({ queryKey: CALENDARS_QUERY_KEY });
        if (selectedCalendarId.value === id) {
          selectedCalendarId.value = null;
        }
        success('Calendar deleted successfully');
      },
    });

  const useCreateAllocationMutation = () =>
    useMutation({
      mutationFn: ({ calendarId, name, type }: { calendarId: number; name: string; type: string }) =>
        api.calendars.createAllocation(calendarId, { name, type: type as CreateAllocationData['type'] }),
      onSuccess: (_data, variables) => {
        queryClient.invalidateQueries({ queryKey: [...ALLOCATIONS_QUERY_KEY, variables.calendarId] });
        success('Allocation created successfully');
      },
    });

  const useUpdateAllocationMutation = () =>
    useMutation({
      mutationFn: ({ id, name }: { id: number; name: string }) => api.allocations.update(id, { name }),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ALLOCATIONS_QUERY_KEY });
        success('Allocation updated successfully');
      },
    });

  const useDeleteAllocationMutation = () =>
    useMutation({
      mutationFn: (id: number) => api.allocations.delete(id),
      onSuccess: (_data, id) => {
        queryClient.invalidateQueries({ queryKey: ALLOCATIONS_QUERY_KEY });
        if (selectedAllocationId.value === id) {
          selectedAllocationId.value = null;
          selectedAllocation.value = null;
        }
        success('Allocation deleted successfully');
      },
    });

  const useApplyAllocationMutation = () =>
    useMutation({
      mutationFn: (id: number) => api.allocations.apply(id),
      onSuccess: () => {
        success('Allocation applied successfully');
      },
    });

  function selectCalendar(id: number | null): void {
    selectedCalendarId.value = id;
  }

  function selectAllocation(allocation: Allocation | null): void {
    selectedAllocation.value = allocation;
    selectedAllocationId.value = allocation ? allocation.id : null;
  }

  return {
    selectedCalendarId,
    selectedAllocationId,
    selectedAllocation,
    useCalendarsQuery,
    useAllocationsQuery,
    useCreateCalendarMutation,
    useUpdateCalendarMutation,
    useDeleteCalendarMutation,
    useCreateAllocationMutation,
    useUpdateAllocationMutation,
    useDeleteAllocationMutation,
    useApplyAllocationMutation,
    selectCalendar,
    selectAllocation,
  };
});
