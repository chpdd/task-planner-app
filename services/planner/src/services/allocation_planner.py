import datetime as dt
from enum import Enum

import task_planner as tp
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.crud import calendar_crud, failed_task_crud, task_execution_crud
from src.models import Allocation, Day, FailedTask, Task, TaskExecution
from src.schemas.allocation import AllocationApplyResultSchema


class AllocationPlannerMethod(str, Enum):  # noqa: UP042
    INTEREST = "interest"
    IMPORTANCE = "importance"
    INTEREST_IMPORTANCE = "interest_importance"
    POINTS_ALLOCATION = "points_allocation"
    FORCE_PROCRASTINATE = "force_procrastinate"


NAME_TO_METHOD = {
    AllocationPlannerMethod.INTEREST: tp.Planner.interest_allocation,
    AllocationPlannerMethod.IMPORTANCE: tp.Planner.importance_allocation,
    AllocationPlannerMethod.INTEREST_IMPORTANCE: tp.Planner.interest_importance_allocation,
    AllocationPlannerMethod.POINTS_ALLOCATION: tp.Planner.points_allocation,
    AllocationPlannerMethod.FORCE_PROCRASTINATE: tp.Planner.force_procrastination_allocation,
}

ALLOCATION_TYPE_TO_METHOD = {
    "even": tp.Planner.points_allocation,
    "priority": tp.Planner.importance_allocation,
    "compact": tp.Planner.force_procrastination_allocation,
}


async def apply_allocation_plan(
    session: AsyncSession,
    allocation: Allocation,
    user_id: int,
    method: AllocationPlannerMethod | None = None,
    start_date: dt.date | None = None,
) -> AllocationApplyResultSchema:
    start_date = start_date or dt.date.today()
    allocation_id = allocation.id

    await failed_task_crud.delete_by_allocation_id(session, allocation_id)
    await task_execution_crud.delete_by_allocation_id(session, allocation_id)

    calendar = await calendar_crud.get(session, allocation.calendar_id)
    if calendar is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calendar not found")

    tasks_stmt = select(Task).where(Task.owner_id == user_id)
    db_tasks = list((await session.scalars(tasks_stmt)).all())
    if not db_tasks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Allocation has no tasks to distribute",
        )

    planner_tasks = []
    for db_task in db_tasks:
        planner_task = tp.Task(
            id=db_task.id,
            name=db_task.name,
            deadline=db_task.deadline,
            interest=db_task.interest,
            importance=db_task.importance,
            work_hours=db_task.work_hours,
        )
        planner_tasks.append(planner_task)

    days_stmt = select(Day).where(Day.calendar_id == calendar.id)
    days = list((await session.scalars(days_stmt)).all())

    if not days:
        current = start_date
        end = start_date + dt.timedelta(days=30)
        while current <= end:
            day = Day(
                date=current,
                work_hours=settings.default_day_work_hours,
                calendar_id=calendar.id,
            )
            session.add(day)
            days.append(day)
            current += dt.timedelta(days=1)
        await session.flush()

    manual_days = []
    for day in days:
        manual_days.append(tp.Day(date=day.date, work_hours=day.work_hours))

    planner = tp.Planner(
        tasks=planner_tasks,
        manual_days=manual_days,
        start_date=start_date,
    )

    allocation_method = NAME_TO_METHOD.get(method) if method else ALLOCATION_TYPE_TO_METHOD.get(allocation.type.value)
    if allocation_method is None:
        allocation_method = tp.Planner.points_allocation
    allocation_method(planner)

    failed_tasks = [
        FailedTask(allocation_id=allocation_id, task_id=failed_task.id)
        for failed_task in planner.failed_tasks
    ]
    if failed_tasks:
        session.add_all(failed_tasks)

    task_executions_created = 0
    for planner_day in planner.calendar.days:
        day_record = next((d for d in days if d.date == planner_day.date), None)
        if day_record is None:
            continue
        for task, doing_hours in planner_day.schedule.items():
            if task.id is None:
                continue
            session.add(
                TaskExecution(
                    task_id=task.id,
                    day_id=day_record.id,
                    allocation_id=allocation_id,
                    doing_hours=doing_hours,
                )
            )
            task_executions_created += 1

    return AllocationApplyResultSchema(
        allocation_id=allocation_id,
        task_executions_created=task_executions_created,
        days_processed=len(planner.calendar.days),
    )
