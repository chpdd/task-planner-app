export interface Task {
  id: number;
  name: string;
  deadline?: string;
  interest: number; // 1-10
  importance: number; // 1-10
  work_hours: number;
  created_at: string;
}

export interface CreateTaskData {
  name: string;
  deadline?: string;
  interest: number;
  importance: number;
  work_hours: number;
}

export interface Calendar {
  id: number;
  name: string;
  user_id?: number;
  created_at?: string;
  updated_at?: string;
}

export interface Allocation {
  id: number;
  calendar_id: number;
  name: string;
  type: AllocationType;
  day_limits?: Record<string, number> | null;
  created_at: string;
  updated_at?: string;
}

export type AllocationType =
  | 'interest'
  | 'importance'
  | 'interest_importance'
  | 'points_allocation'
  | 'force_procrastinate';

export interface Day {
  id: number;
  calendar_id: number;
  date: string;
  work_hours: number;
  created_at: string;
  updated_at: string;
}

export interface TaskExecution {
  id: number;
  allocation_id: number;
  task_id: number;
  day_id: number;
  doing_hours: number;
  is_done: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateCalendarData {
  name: string;
}

export interface CreateAllocationData {
  name: string;
  type: AllocationType;
}

export interface CreateDayData {
  date: string;
  work_hours: number;
}

export interface CreateExecutionData {
  task_id: number;
  day_id: number;
  doing_hours: number;
}

export interface UpdateExecutionData {
  is_done?: boolean;
  doing_hours?: number;
}
