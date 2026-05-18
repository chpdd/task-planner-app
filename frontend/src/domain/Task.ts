import type { Task as ApiTask } from '@/types/api';

/**
 * Task Domain Model
 * Encapsulates task-related business logic and computed properties
 */
export class Task {
  readonly id: number;
  readonly name: string;
  readonly interest: number;
  readonly importance: number;
  readonly workHours: number;
  readonly deadline: Date | null;
  readonly createdAt: Date;

  constructor(data: ApiTask) {
    this.id = data.id;
    this.name = data.name;
    this.interest = data.interest;
    this.importance = data.importance;
    this.workHours = data.work_hours;
    this.deadline = data.deadline ? new Date(data.deadline) : null;
    this.createdAt = new Date(data.created_at);
  }

  /**
   * Returns true if the task is overdue based on current time
   */
  get isOverdue(): boolean {
    if (!this.deadline) return false;
    return this.deadline.getTime() < Date.now();
  }

  /**
   * Returns a score representing priority based on importance and interest
   */
  get priorityScore(): number {
    return this.importance * 2 + this.interest;
  }

  /**
   * Formats deadline to a readable string
   */
  get formattedDeadline(): string {
    if (!this.deadline) return 'No deadline';
    return this.deadline.toLocaleDateString(undefined, { 
      day: 'numeric', 
      month: 'short',
      year: 'numeric'
    });
  }

  /**
   * Dynamic color based on interest
   */
  get color(): string {
    const hue = 30 + (this.interest - 1) * 5;
    return `oklch(0.65 0.18 ${hue})`;
  }
}

/**
 * Factory function to create Task instances
 */
export function createTasks(tasks: ApiTask[]): Task[] {
  return tasks.map(t => new Task(t));
}
