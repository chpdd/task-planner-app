import datetime as dt

from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import select

from src.core.cache import delete_cache_by_prefix
from src.core.dependencies import db_dep, redis_dep
from src.crud import day_crud, task_execution_crud
from src.models import Calendar, Day
from src.schemas.task_execution import (
    CreateTaskExecutionSchema,
    MoveTaskExecutionSchema,
    TaskExecutionSchema,
)

router = APIRouter(prefix="/task_executions", tags=["TaskExecutions"])


@router.post("/move", response_model=TaskExecutionSchema)
async def move_task_execution(
    request: Request,
    move_schema: MoveTaskExecutionSchema,
    session: db_dep,
    redis: redis_dep,
    start_date: dt.date = dt.date.today(),
) -> TaskExecutionSchema:
    user_id = request.state.user_id

    await task_execution_crud.schema_owner_get(session, move_schema.task_execution_id, user_id)

    if move_schema.target_day_id is not None:
        await day_crud.schema_owner_get_by_id(session, move_schema.target_day_id, user_id)
        target_day_id = move_schema.target_day_id
    elif move_schema.new_day_index is not None:
        days_stmt = (
            select(Day)
            .join(Calendar, Day.calendar_id == Calendar.id)
            .where(
                Calendar.user_id == user_id,
                Day.date >= start_date,
            )
            .order_by(Day.date)
        )
        days = (await session.scalars(days_stmt)).all()

        if move_schema.new_day_index < 0 or move_schema.new_day_index >= len(days):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid day index. Must be between 0 and {len(days) - 1}",
            )
        target_day_id = days[move_schema.new_day_index].id
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either target_day_id or new_day_index must be provided",
        )

    updated = await task_execution_crud.update_by_id(
        session, move_schema.task_execution_id, day_id=target_day_id
    )
    await session.commit()
    await delete_cache_by_prefix(redis, f"planner:calendar:{user_id}")
    await delete_cache_by_prefix(redis, f"planner:calendar_with_tasks:{user_id}")

    return updated


@router.post("", response_model=TaskExecutionSchema, status_code=status.HTTP_201_CREATED)
async def create_task_execution(
    request: Request,
    task_execution_schema: CreateTaskExecutionSchema,
    day_id: int,
    session: db_dep,
    redis: redis_dep,
) -> TaskExecutionSchema:
    user_id = request.state.user_id

    await day_crud.schema_owner_get_by_id(session, day_id, user_id)

    task_execution_dict = task_execution_schema.model_dump()
    task_execution_dict["day_id"] = day_id

    task_execution = await task_execution_crud.schema_owner_create(
        session,
        CreateTaskExecutionSchema(**task_execution_dict),
        user_id,
        day_id,
    )
    await session.commit()
    await delete_cache_by_prefix(redis, f"planner:calendar:{user_id}")
    await delete_cache_by_prefix(redis, f"planner:calendar_with_tasks:{user_id}")

    return task_execution


@router.delete("/{task_execution_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_task_execution(
    request: Request,
    task_execution_id: int,
    session: db_dep,
    redis: redis_dep,
) -> None:
    user_id = request.state.user_id

    await task_execution_crud.schema_owner_get(session, task_execution_id, user_id)
    task_execution = await task_execution_crud.get(session, task_execution_id)

    await task_execution_crud.delete(session, task_execution)
    await session.commit()
    await delete_cache_by_prefix(redis, f"planner:calendar:{user_id}")
    await delete_cache_by_prefix(redis, f"planner:calendar_with_tasks:{user_id}")
