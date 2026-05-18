import pytest
import datetime as dt

from sqlalchemy import select

from src.crud import (
    allocation_crud,
    calendar_crud,
    day_crud,
    task_crud,
    user_crud,
)
from src.models import TaskExecution, User
from src.schemas.allocation import AllocationCreateSchema
from src.schemas.calendar import CalendarCreateSchema
from src.schemas.day import CreateDaySchema
from src.schemas.task import CreateTaskSchema
from src.core import security


@pytest.fixture
async def test_user(db_session):
    user = User(
        name="executionowner",
        hashed_password=security.hash_password("password123")
    )
    await user_crud.create(db_session, user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_setup(db_session, test_user):
    calendar = await calendar_crud.schema_owner_create(
        db_session, CalendarCreateSchema(name="Exec Calendar"), test_user.id
    )
    await db_session.commit()

    allocation = await allocation_crud.create_for_calendar(
        db_session, calendar.id, AllocationCreateSchema(name="Exec Allocation")
    )
    await db_session.commit()

    day = await day_crud.schema_calendar_create(
        db_session,
        CreateDaySchema(date=dt.date(2025, 12, 1), work_hours=8),
        calendar.id,
        test_user.id
    )
    await db_session.commit()

    task = await task_crud.schema_owner_create(
        db_session, CreateTaskSchema(name="Exec Task"), test_user.id
    )
    await db_session.commit()

    return {
        "user": test_user,
        "calendar": calendar,
        "allocation": allocation,
        "day": day,
        "task": task,
    }


def create_task_execution_params(test_setup, **kwargs):
    from src.models import TaskExecution
    return TaskExecution(
        task_id=test_setup["task"].id,
        day_id=test_setup["day"].id,
        allocation_id=test_setup["allocation"].id,
        doing_hours=kwargs.get("doing_hours", 2),
        is_done=kwargs.get("is_done", False),
    )


@pytest.mark.asyncio
async def test_create_task_execution(db_session, test_setup):
    task_execution = create_task_execution_params(test_setup)
    db_session.add(task_execution)
    await db_session.commit()
    await db_session.refresh(task_execution)

    assert task_execution.id is not None
    assert task_execution.is_done is False
    assert task_execution.doing_hours == 2


@pytest.mark.asyncio
async def test_update_is_done_to_true(db_session, test_setup):
    task_execution = create_task_execution_params(test_setup, doing_hours=3, is_done=False)
    db_session.add(task_execution)
    await db_session.commit()
    await db_session.refresh(task_execution)

    task_execution.is_done = True
    await db_session.commit()
    await db_session.refresh(task_execution)

    assert task_execution.is_done is True


@pytest.mark.asyncio
async def test_update_is_done_to_false(db_session, test_setup):
    task_execution = create_task_execution_params(test_setup, doing_hours=1, is_done=True)
    db_session.add(task_execution)
    await db_session.commit()
    await db_session.refresh(task_execution)

    task_execution.is_done = False
    await db_session.commit()
    await db_session.refresh(task_execution)

    assert task_execution.is_done is False


@pytest.mark.asyncio
async def test_list_task_executions_by_allocation(db_session, test_setup):
    exec1 = create_task_execution_params(test_setup, doing_hours=2, is_done=False)
    exec2 = create_task_execution_params(test_setup, doing_hours=3, is_done=True)
    db_session.add(exec1)
    db_session.add(exec2)
    await db_session.commit()

    stmt = select(TaskExecution).where(
        TaskExecution.allocation_id == test_setup["allocation"].id
    )
    results = list((await db_session.scalars(stmt)).all())

    assert len(results) >= 2
    is_done_statuses = [r.is_done for r in results]
    assert True in is_done_statuses
    assert False in is_done_statuses


@pytest.mark.asyncio
async def test_task_execution_default_is_done_false(db_session, test_setup):
    task_execution = create_task_execution_params(test_setup, doing_hours=1)
    db_session.add(task_execution)
    await db_session.commit()
    await db_session.refresh(task_execution)

    assert task_execution.is_done is False
