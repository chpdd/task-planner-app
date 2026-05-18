import { defineStore } from 'pinia';
import { ref, type Ref } from 'vue';
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query';
import { api } from '@/api/client';
import { useToast } from '@/composables/useToast';

const DAYS_QUERY_KEY = ['days'] as const;

export const useDaysStore = defineStore('days', () => {
  const { success } = useToast();
  const queryClient = useQueryClient();

  const currentCalendarId = ref<number | null>(null);

  const useDaysQuery = (calendarIdRef: Ref<number | null>, startDateRef: Ref<string>, endDateRef: Ref<string>) =>
    useQuery({
      queryKey: [...DAYS_QUERY_KEY, calendarIdRef, startDateRef, endDateRef],
      queryFn: () => {
        const id = calendarIdRef.value;
        currentCalendarId.value = id;
        return api.calendars.listDays(id!, startDateRef.value, endDateRef.value);
      },
      enabled: () => !!calendarIdRef.value,
      staleTime: 1000 * 60,
    });

  const useCreateDayMutation = () =>
    useMutation({
      mutationFn: ({ calendarId, date, workHours }: { calendarId: number; date: string; workHours: number }) =>
        api.calendars.createDay(calendarId, { date, work_hours: workHours }),
      onSuccess: (_data, variables) => {
        queryClient.invalidateQueries({ queryKey: [...DAYS_QUERY_KEY, variables.calendarId] });
        success('Day created successfully');
      },
    });

  const useUpdateDayWorkHoursMutation = () =>
    useMutation({
      mutationFn: ({ dayId, workHours }: { dayId: number; workHours: number }) =>
        api.days.update(dayId, { work_hours: workHours }),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: DAYS_QUERY_KEY });
        success('Day updated successfully');
      },
    });

  const useDeleteDayMutation = () =>
    useMutation({
      mutationFn: (dayId: number) => api.days.delete(dayId),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: DAYS_QUERY_KEY });
        success('Day deleted successfully');
      },
    });

  return {
    currentCalendarId,
    useDaysQuery,
    useCreateDayMutation,
    useUpdateDayWorkHoursMutation,
    useDeleteDayMutation,
  };
});
