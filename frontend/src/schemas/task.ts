import { z } from 'zod';
import { TASK_CONFIG } from '@/config/constants';

/**
 * Task Form Validation Schema factory
 * We use a factory to support dynamic localization of error messages
 */
export const createTaskSchema = (t: (key: string, args?: any) => string) => z.object({
  name: z.string()
    .min(1, t('tasks.titleRequired'))
    .max(100, t('validation.maxLength', { count: 100 })),
  deadline: z.string().optional().or(z.literal('')),
  interest: z.number()
    .min(TASK_CONFIG.MIN_INTEREST, t('tasks.interestRange'))
    .max(TASK_CONFIG.MAX_INTEREST, t('tasks.interestRange')),
  importance: z.number()
    .min(TASK_CONFIG.MIN_IMPORTANCE, t('tasks.importanceRange'))
    .max(TASK_CONFIG.MAX_IMPORTANCE, t('tasks.importanceRange')),
  work_hours: z.number()
    .int(t('validation.integer'))
    .min(TASK_CONFIG.MIN_HOURS, t('tasks.hoursRange'))
    .max(TASK_CONFIG.MAX_HOURS, t('tasks.hoursRange')),
});

// Backward compatibility or default
export const taskSchema = z.object({
  name: z.string().min(1, 'Task name is required').max(100, 'Task name is too long'),
  deadline: z.string().optional().or(z.literal('')),
  interest: z.number()
    .min(TASK_CONFIG.MIN_INTEREST, `Interest must be at least ${TASK_CONFIG.MIN_INTEREST}`)
    .max(TASK_CONFIG.MAX_INTEREST, `Interest must be at most ${TASK_CONFIG.MAX_INTEREST}`),
  importance: z.number()
    .min(TASK_CONFIG.MIN_IMPORTANCE, `Importance must be at least ${TASK_CONFIG.MIN_IMPORTANCE}`)
    .max(TASK_CONFIG.MAX_IMPORTANCE, `Importance must be at most ${TASK_CONFIG.MAX_IMPORTANCE}`),
  work_hours: z.number()
    .int('Work hours must be an integer')
    .min(TASK_CONFIG.MIN_HOURS, `Work hours must be at least ${TASK_CONFIG.MIN_HOURS}`)
    .max(TASK_CONFIG.MAX_HOURS, `Work hours must be at most ${TASK_CONFIG.MAX_HOURS}`),
});

export type TaskSchema = z.infer<typeof taskSchema>;
