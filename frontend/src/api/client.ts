import type {
  Task,
  CreateTaskData,
  Distribution,
  Calendar,
  CreateCalendarData,
  Allocation,
  CreateAllocationData,
  Day,
  CreateDayData,
  TaskExecution,
  CreateExecutionData,
  UpdateExecutionData,
} from '../types/api';
import { useAuthStore } from '@/stores/authStore';

const API_BASE = import.meta.env.VITE_API_URL || '';

export class ApiError extends Error {
  status: number;
  body: unknown;

  constructor(status: number, body: unknown) {
    super('API Error');
    this.name = 'ApiError';
    this.status = status;
    this.body = body;
  }
}

export class ValidationError extends Error {
  errors: Record<string, string[]>;

  constructor(errors: Record<string, string[]>) {
    super('Validation Error');
    this.name = 'ValidationError';
    this.errors = errors;
  }
}

export class ApiClient {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
  }

  async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers = new Headers({
      'Content-Type': 'application/json',
    });

    if (options.headers) {
      if (options.headers instanceof Headers) {
        options.headers.forEach((value, key) => headers.set(key, value));
      } else if (Array.isArray(options.headers)) {
        options.headers.forEach(([key, value]) => headers.set(key, value));
      } else {
        Object.entries(options.headers).forEach(([key, value]) => headers.set(key, value));
      }
    }

    if (this.token) {
      headers.set('Authorization', `Bearer ${this.token}`);
    }

    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers,
      });

      if (!response.ok) {
        const body = await response.json().catch(() => null);

        if (response.status === 401) {
          const authStore = useAuthStore();
          authStore.logout();
          window.location.href = '/login';
        } else if (response.status === 400 && body) {
          throw new ValidationError(body.detail || body);
        }

        throw new ApiError(response.status, body);
      }

      // Handle 204 No Content
      if (response.status === 204) {
        return undefined as T;
      }

      return response.json();
    } catch (e) {
      if (e instanceof ValidationError || e instanceof ApiError) {
        throw e;
      }
      throw new ApiError(0, e instanceof Error ? e.message : 'Network error');
    }
  }

  // Auth endpoints
  auth = {
    login: (data: { username: string; password: string }) =>
      this.request<{ access_token: string; refresh_token?: string; token_type: string }>(
        '/api/auth/login',
        { method: 'POST', body: JSON.stringify(data) }
      ),
    register: (data: { username: string; password: string }) =>
      this.request<{ access_token: string; refresh_token?: string; token_type: string }>(
        '/api/auth/register',
        { method: 'POST', body: JSON.stringify(data) }
      ),
    refresh: (token: string) =>
      this.request<{ access_token: string }>(
        '/api/auth/refresh',
        { method: 'POST', body: JSON.stringify({ refresh_token: token }) }
      ),
  };

  // Tasks endpoints
  tasks = {
    list: () => this.request<Task[]>('/api/planner/tasks'),
    get: (id: number) => this.request<Task>(`/api/planner/tasks/${id}`),
    create: (data: CreateTaskData) =>
      this.request<Task>('/api/planner/tasks', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: number, data: Partial<CreateTaskData>) =>
      this.request<Task>(`/api/planner/tasks/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
    delete: (id: number) => this.request<void>(`/api/planner/tasks/${id}`, { method: 'DELETE' }),
  };

  // Distributions endpoints
  distributions = {
    list: () => this.request<Distribution[]>('/api/planner/distributions'),
    get: (id: number) => this.request<Distribution>(`/api/planner/distributions/${id}`),
    create: (data: object) =>
      this.request<Distribution>('/api/planner/distributions', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: number, data: object) =>
      this.request<Distribution>(`/api/planner/distributions/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
    delete: (id: number) => this.request<void>(`/api/planner/distributions/${id}`, { method: 'DELETE' }),
  };

  // Calendar endpoints
  calendar = {
    get: (offset: number = 0) => this.request<unknown>(`/api/planner/calendar?offset=${offset}`),
    allocate: (distributionId: number) =>
      this.request<unknown>('/api/planner/allocate', { method: 'POST', body: JSON.stringify({ distribution_id: distributionId }) }),
  };

  // Calendars endpoints
  calendars = {
    list: () => this.request<Calendar[]>('/api/planner/calendars'),
    get: (id: number) => this.request<Calendar>(`/api/planner/calendars/${id}`),
    create: (data: CreateCalendarData) =>
      this.request<Calendar>('/api/planner/calendars', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: number, data: Partial<CreateCalendarData>) =>
      this.request<Calendar>(`/api/planner/calendars/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
    delete: (id: number) => this.request<void>(`/api/planner/calendars/${id}`, { method: 'DELETE' }),
    listAllocations: (calendarId: number) =>
      this.request<Allocation[]>(`/api/planner/calendars/${calendarId}/allocations`),
    createAllocation: (calendarId: number, data: CreateAllocationData) =>
      this.request<Allocation>(`/api/planner/calendars/${calendarId}/allocations`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    listDays: (calendarId: number, startDate?: string, endDate?: string) => {
      let url = `/api/planner/calendars/${calendarId}/days`;
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      if (params.toString()) url += `?${params.toString()}`;
      return this.request<Day[]>(url);
    },
    createDay: (calendarId: number, data: CreateDayData) =>
      this.request<Day>(`/api/planner/calendars/${calendarId}/days`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  };

  // Allocations endpoints
  allocations = {
    get: (id: number) => this.request<Allocation>(`/api/planner/allocations/${id}`),
    update: (id: number, data: Partial<CreateAllocationData>) =>
      this.request<Allocation>(`/api/planner/allocations/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
    delete: (id: number) => this.request<void>(`/api/planner/allocations/${id}`, { method: 'DELETE' }),
    apply: (id: number) =>
      this.request<{ detail: string }>(`/api/planner/allocations/${id}/apply`, { method: 'POST' }),
  };

  // Days endpoints
  days = {
    update: (id: number, data: Partial<CreateDayData>) =>
      this.request<Day>(`/api/planner/days/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
    delete: (id: number) => this.request<void>(`/api/planner/days/${id}`, { method: 'DELETE' }),
  };

  // Task Executions endpoints
  taskExecutions = {
    listByAllocation: (allocationId: number) =>
      this.request<TaskExecution[]>(`/api/planner/task_executions/allocations/${allocationId}`),
    create: (data: CreateExecutionData & { allocation_id: number }) =>
      this.request<TaskExecution>('/api/planner/task_executions', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    update: (id: number, data: UpdateExecutionData) =>
      this.request<TaskExecution>(`/api/planner/task_executions/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    delete: (id: number) => this.request<void>(`/api/planner/task_executions/${id}`, { method: 'DELETE' }),
  };

  // AI endpoints
  ai = {
    chat: (message: string) =>
      this.request<{ response: string; model?: string; usage: unknown }>('/api/planner/ai/chat', {
        method: 'POST',
        body: JSON.stringify({ message }),
      }),
    createTask: (instruction: string) =>
      this.request<Task>('/api/planner/ai/create-task', {
        method: 'POST',
        body: JSON.stringify({ instruction }),
      }),
  };
}

export const api = new ApiClient();
