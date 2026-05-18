import pytest
import datetime as dt

from src.crud import calendar_crud, day_crud, user_crud
from src.models import User
from src.schemas.calendar import CalendarCreateSchema
from src.schemas.day import CreateDaySchema, DayUpdateSchema
from src.core import security


@pytest.fixture
async def test_user(db_session):
    user = User(
        name="dayowner",
        hashed_password=security.hash_password("password123")
    )
    await user_crud.create(db_session, user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_calendar(db_session, test_user):
    return await calendar_crud.schema_owner_create(
        db_session,
        CalendarCreateSchema(name="Day Test Calendar"),
        test_user.id
    )


@pytest.mark.asyncio
async def test_create_day(db_session, test_calendar):
    day_in = CreateDaySchema(
        date=dt.date(2025, 6, 15),
        work_hours=8
    )
    day = await day_crud.schema_calendar_create(
        db_session, day_in, test_calendar.id, test_calendar.user_id
    )
    assert day.date == dt.date(2025, 6, 15)
    assert day.work_hours == 8


@pytest.mark.asyncio
async def test_list_days_for_calendar(db_session, test_calendar):
    await day_crud.schema_calendar_create(
        db_session,
        CreateDaySchema(date=dt.date(2025, 7, 1), work_hours=6),
        test_calendar.id,
        test_calendar.user_id
    )
    await day_crud.schema_calendar_create(
        db_session,
        CreateDaySchema(date=dt.date(2025, 7, 2), work_hours=7),
        test_calendar.id,
        test_calendar.user_id
    )
    await db_session.commit()

    days = await day_crud.schema_calendar_list(
        db_session, test_calendar.id, test_calendar.user_id
    )
    assert len(days) >= 2


@pytest.mark.asyncio
async def test_list_days_with_date_range(db_session, test_calendar):
    await day_crud.schema_calendar_create(
        db_session,
        CreateDaySchema(date=dt.date(2025, 8, 1), work_hours=8),
        test_calendar.id,
        test_calendar.user_id
    )
    await day_crud.schema_calendar_create(
        db_session,
        CreateDaySchema(date=dt.date(2025, 8, 15), work_hours=6),
        test_calendar.id,
        test_calendar.user_id
    )
    await day_crud.schema_calendar_create(
        db_session,
        CreateDaySchema(date=dt.date(2025, 8, 30), work_hours=7),
        test_calendar.id,
        test_calendar.user_id
    )
    await db_session.commit()

    days = await day_crud.schema_calendar_list(
        db_session,
        test_calendar.id,
        test_calendar.user_id,
        start_date=dt.date(2025, 8, 10),
        end_date=dt.date(2025, 8, 20)
    )
    assert len(days) == 1
    assert days[0].date == dt.date(2025, 8, 15)


@pytest.mark.asyncio
async def test_get_day_by_id(db_session, test_calendar):
    day = await day_crud.schema_calendar_create(
        db_session,
        CreateDaySchema(date=dt.date(2025, 9, 5), work_hours=4),
        test_calendar.id,
        test_calendar.user_id
    )
    await db_session.commit()

    stored = await day_crud.schema_owner_get_by_id(db_session, day.id, test_calendar.user_id)
    assert stored is not None
    assert stored.id == day.id
    assert stored.date == dt.date(2025, 9, 5)


@pytest.mark.asyncio
async def test_update_day_work_hours(db_session, test_calendar):
    day = await day_crud.schema_calendar_create(
        db_session,
        CreateDaySchema(date=dt.date(2025, 10, 10), work_hours=8),
        test_calendar.id,
        test_calendar.user_id
    )
    await db_session.commit()

    update_data = DayUpdateSchema(work_hours=6)
    updated = await day_crud.schema_calendar_update_by_id(
        db_session, day.id, test_calendar.id, test_calendar.user_id, update_data
    )
    assert updated.work_hours == 6


@pytest.mark.asyncio
async def test_delete_day(db_session, test_calendar):
    day = await day_crud.schema_calendar_create(
        db_session,
        CreateDaySchema(date=dt.date(2025, 11, 1), work_hours=5),
        test_calendar.id,
        test_calendar.user_id
    )
    await db_session.commit()
    day_id = day.id

    await day_crud.schema_calendar_delete_by_id(
        db_session, day_id, test_calendar.id, test_calendar.user_id
    )

    days = await day_crud.schema_calendar_list(
        db_session, test_calendar.id, test_calendar.user_id
    )
    assert not any(d.id == day_id for d in days)
