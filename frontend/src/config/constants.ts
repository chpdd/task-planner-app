/**
 * Global application constants
 */

export const API_CONFIG = {
  STALE_TIME: 1000 * 60 * 5, // 5 minutes
  CACHE_TIME: 1000 * 60 * 30, // 30 minutes
  RETRY_COUNT: 1,
} as const;

export const TASK_CONFIG = {
  MIN_INTEREST: 1,
  MAX_INTEREST: 10,
  DEFAULT_INTEREST: 5,
  MIN_IMPORTANCE: 1,
  MAX_IMPORTANCE: 10,
  DEFAULT_IMPORTANCE: 5,
  MIN_HOURS: 1,
  MAX_HOURS: 24,
  DEFAULT_HOURS: 1,
} as const;

export const CALENDAR_CONFIG = {
  GRID_CELLS_COUNT: 42, // 6 weeks * 7 days
  DEFAULT_WORK_HOURS: 8,
} as const;

export const STORAGE_KEYS = {
  AUTH_TOKEN: 'tp_token',
  QUERY_CACHE: 'tp_query_cache',
} as const;
