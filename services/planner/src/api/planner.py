import datetime as dt

from fastapi import Depends, APIRouter, Request
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core.dependencies import db_dep, redis_dep
from src.core.cache import get_cache, set_cache
from src.core.rate_limit import RateLimiter

from src import schemas
from src.models import Calendar, TaskExecution, Day
from src.crud import failed_task_crud

router = APIRouter(tags=["Planner"])


@router.get("/calendar", dependencies=[Depends(RateLimiter(times=100, seconds=60))])
async def get_calendar(request: Request, session: db_dep, redis: redis_dep,
                       start_date: dt.date = dt.date.today()) -> list[schemas.day.TaskExecutionsDaySchema]:
    user_id = request.state.user_id
    cache_key = f"planner:calendar:{user_id}:{start_date}"

    cached_data = await get_cache(redis, cache_key, list[schemas.day.TaskExecutionsDaySchema])
    if cached_data is not None:
        return cached_data

    days_stmt = (
        select(Day)
        .join(Calendar, Day.calendar_id == Calendar.id)
        .options(selectinload(Day.task_executions))
        .where(
            Calendar.user_id == user_id,
            Day.date >= start_date,
        )
    )
    days = (await session.scalars(days_stmt)).all()

    await set_cache(redis, cache_key, days, list[schemas.day.TaskExecutionsDaySchema])
    return days


@router.get("/calendar_with_tasks", dependencies=[Depends(RateLimiter(times=100, seconds=60))])
async def get_calendar_with_tasks(request: Request, session: db_dep, redis: redis_dep,
                                  start_date: dt.date = dt.date.today()) -> list[schemas.day.TasksDaySchema]:
    user_id = request.state.user_id
    cache_key = f"planner:calendar_with_tasks:{user_id}:{start_date}"

    cached_data = await get_cache(redis, cache_key, list[schemas.day.TasksDaySchema])
    if cached_data is not None:
        return cached_data

    days_stmt = (
        select(Day)
        .join(Calendar, Day.calendar_id == Calendar.id)
        .options(selectinload(Day.task_executions).selectinload(TaskExecution.task))
        .where(
            Calendar.user_id == user_id,
            Day.date >= start_date,
        )
    )
    days = (await session.scalars(days_stmt)).all()

    await set_cache(redis, cache_key, days, list[schemas.day.TasksDaySchema])
    return days


@router.get("/allocations/{allocation_id}/failed_tasks")
async def list_failed_tasks_for_allocation(
    request: Request,
    allocation_id: int,
    session: db_dep,
) -> list[schemas.failed_task.FailedTaskSchema]:
    return await failed_task_crud.list_by_allocation(session, allocation_id, request.state.user_id)
