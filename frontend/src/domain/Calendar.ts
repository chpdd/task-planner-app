import type { Calendar as ApiCalendar, Allocation as ApiAllocation } from '@/types/api';

export class Allocation {
  readonly id: number;
  readonly name: string;
  readonly type: string;
  readonly calendarId: number;

  constructor(data: ApiAllocation) {
    this.id = data.id;
    this.name = data.name;
    this.type = data.type;
    this.calendarId = data.calendar_id;
  }
}

export class Calendar {
  readonly id: number;
  readonly name: string;
  readonly createdAt: Date;

  constructor(data: ApiCalendar) {
    this.id = data.id;
    this.name = data.name;
    this.createdAt = new Date(data.created_at);
  }
}
