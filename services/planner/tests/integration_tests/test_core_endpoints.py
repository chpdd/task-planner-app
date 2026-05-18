import datetime as dt

import pytest

from src.core import security
from src.crud import calendar_crud, day_crud, task_crud, user_crud
from src.models import FailedTask, User
from src.schemas.calendar import CalendarCreateSchema
from src.schemas.day import CreateDaySchema
from src.schemas.task import CreateTaskSchema


def auth_headers(user_id: int) -> dict:
    token = security.create_access_token(sub=str(user_id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def endpoint_user(db_session):
    user = User(name="endpoint_user", hashed_password=security.hash_password("password123"))
    await user_crud.create(db_session, user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def endpoint_calendar(db_session, endpoint_user):
    calendar = await calendar_crud.schema_owner_create(
        db_session,
        CalendarCreateSchema(name="Endpoint Calendar"),
        endpoint_user.id,
    )
    await db_session.commit()
    return calendar


@pytest.mark.asyncio
async def test_allocations_create_and_list_endpoints(client, db_session, endpoint_user, endpoint_calendar):
    response = await client.post(
        f"/api/planner/allocations?calendar_id={endpoint_calendar.id}",
        json={"name": "Primary Allocation", "type": "even"},
        headers=auth_headers(endpoint_user.id),
    )
    assert response.status_code == 200
    created = response.json()
    assert created["name"] == "Primary Allocation"
    assert created["calendar_id"] == endpoint_calendar.id

    response = await client.get(
        "/api/planner/allocations",
        headers=auth_headers(endpoint_user.id),
    )
    assert response.status_code == 200
    payload = response.json()
    assert any(item["id"] == created["id"] for item in payload)


@pytest.mark.asyncio
async def test_failed_tasks_list_by_allocation_endpoint(client, db_session, endpoint_user, endpoint_calendar):
    allocation_resp = await client.post(
        f"/api/planner/allocations?calendar_id={endpoint_calendar.id}",
        json={"name": "Allocation For Failures", "type": "priority"},
        headers=auth_headers(endpoint_user.id),
    )
    assert allocation_resp.status_code == 200
    allocation_id = allocation_resp.json()["id"]

    task = await task_crud.schema_owner_create(
        db_session,
        CreateTaskSchema(name="Failed Task Candidate", work_hours=2, interest=5, importance=5),
        endpoint_user.id,
    )
    await db_session.flush()
    db_session.add(FailedTask(allocation_id=allocation_id, task_id=task.id))
    await db_session.commit()

    response = await client.get(
        f"/api/planner/allocations/{allocation_id}/failed_tasks",
        headers=auth_headers(endpoint_user.id),
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["allocation_id"] == allocation_id
    assert data[0]["task_id"] == task.id


@pytest.mark.asyncio
async def test_task_executions_create_move_delete_endpoints(client, db_session, endpoint_user, endpoint_calendar):
    day1 = await day_crud.schema_calendar_create(
        db_session,
        CreateDaySchema(date=dt.date(2026, 1, 10), work_hours=8),
        endpoint_calendar.id,
        endpoint_user.id,
    )
    day2 = await day_crud.schema_calendar_create(
        db_session,
        CreateDaySchema(date=dt.date(2026, 1, 11), work_hours=8),
        endpoint_calendar.id,
        endpoint_user.id,
    )
    task = await task_crud.schema_owner_create(
        db_session,
        CreateTaskSchema(name="Execution Endpoint Task", work_hours=2, interest=6, importance=6),
        endpoint_user.id,
    )
    await db_session.commit()

    create_resp = await client.post(
        f"/api/planner/task_executions?day_id={day1.id}",
        json={"task_id": task.id, "doing_hours": 2},
        headers=auth_headers(endpoint_user.id),
    )
    assert create_resp.status_code == 201
    execution_id = create_resp.json()["id"]
    assert create_resp.json()["day_id"] == day1.id

    move_resp = await client.post(
        "/api/planner/task_executions/move",
        json={"task_execution_id": execution_id, "target_day_id": day2.id},
        headers=auth_headers(endpoint_user.id),
    )
    assert move_resp.status_code == 200
    assert move_resp.json()["day_id"] == day2.id

    delete_resp = await client.delete(
        f"/api/planner/task_executions/{execution_id}",
        headers=auth_headers(endpoint_user.id),
    )
    assert delete_resp.status_code == 204


@pytest.mark.asyncio
async def test_allocation_types_endpoint(client, endpoint_user):
    response = await client.get(
        "/api/planner/allocations/allocation_types",
        headers=auth_headers(endpoint_user.id),
    )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 3
    assert {item["code"] for item in payload} == {"even", "priority", "compact"}


@pytest.mark.asyncio
async def test_calendars_with_allocations_hierarchy(client, endpoint_user, endpoint_calendar):
    create_resp = await client.post(
        f"/api/planner/allocations?calendar_id={endpoint_calendar.id}",
        json={"name": "Hierarchy Allocation", "type": "even"},
        headers=auth_headers(endpoint_user.id),
    )
    assert create_resp.status_code == 200

    response = await client.get(
        "/api/planner/calendars/with_allocations",
        headers=auth_headers(endpoint_user.id),
    )
    assert response.status_code == 200
    calendars = response.json()
    target = next(item for item in calendars if item["id"] == endpoint_calendar.id)
    assert len(target["allocations"]) == 1
    assert target["allocations"][0]["name"] == "Hierarchy Allocation"


@pytest.mark.asyncio
async def test_create_and_apply_allocation_endpoint(client, endpoint_user, endpoint_calendar):
    create_task_resp = await client.post(
        "/api/planner/tasks",
        json={
            "name": "Apply Allocation Task",
            "deadline": "2026-06-01",
            "interest": 7,
            "importance": 8,
            "work_hours": 3,
        },
        headers=auth_headers(endpoint_user.id),
    )
    assert create_task_resp.status_code == 200

    response = await client.post(
        f"/api/planner/allocations/create_and_apply?calendar_id={endpoint_calendar.id}",
        json={
            "name": "Auto Apply Allocation",
            "type": "priority",
            "start_date": "2026-05-20",
        },
        headers=auth_headers(endpoint_user.id),
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["allocation_id"] > 0
    assert payload["days_processed"] > 0
