import pytest

from src.crud import calendar_crud, user_crud
from src.schemas.calendar import CalendarCreateSchema, CalendarUpdateSchema
from src.models import User
from src.core import security


@pytest.fixture
async def test_user(db_session):
    user = User(
        name="calendarowner",
        hashed_password=security.hash_password("password123")
    )
    await user_crud.create(db_session, user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.mark.asyncio
async def test_create_calendar(db_session, test_user):
    calendar_in = CalendarCreateSchema(name="My Calendar")
    calendar = await calendar_crud.schema_owner_create(db_session, calendar_in, test_user.id)
    assert calendar.name == "My Calendar"
    assert calendar.id is not None


@pytest.mark.asyncio
async def test_get_calendar(db_session, test_user):
    calendar_in = CalendarCreateSchema(name="Get Calendar")
    calendar = await calendar_crud.schema_owner_create(db_session, calendar_in, test_user.id)
    await db_session.commit()

    stored = await calendar_crud.schema_owner_get(db_session, calendar.id, test_user.id)
    assert stored is not None
    assert stored.id == calendar.id
    assert stored.name == "Get Calendar"


@pytest.mark.asyncio
async def test_list_calendars(db_session, test_user):
    await calendar_crud.schema_owner_create(db_session, CalendarCreateSchema(name="Calendar 1"), test_user.id)
    await calendar_crud.schema_owner_create(db_session, CalendarCreateSchema(name="Calendar 2"), test_user.id)
    await db_session.commit()

    calendars = await calendar_crud.schema_owner_list(db_session, owner_id=test_user.id)
    assert len(calendars) >= 2
    names = [c.name for c in calendars]
    assert "Calendar 1" in names
    assert "Calendar 2" in names


@pytest.mark.asyncio
async def test_update_calendar(db_session, test_user):
    calendar = await calendar_crud.schema_owner_create(
        db_session,
        CalendarCreateSchema(name="Old Name"),
        test_user.id
    )
    await db_session.commit()

    update_data = CalendarUpdateSchema(name="New Name")
    updated = await calendar_crud.schema_update_by_id(db_session, calendar.id, update_data)
    assert updated.name == "New Name"


@pytest.mark.asyncio
async def test_delete_calendar(db_session, test_user):
    calendar = await calendar_crud.schema_owner_create(
        db_session,
        CalendarCreateSchema(name="Delete Me"),
        test_user.id
    )
    await db_session.commit()
    calendar_id = calendar.id

    await calendar_crud.schema_delete_by_id(db_session, calendar_id)

    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await calendar_crud.schema_owner_get(db_session, calendar_id, test_user.id)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_calendar_ownership(db_session, test_user):
    other_user = User(
        name="otherowner",
        hashed_password=security.hash_password("password123")
    )
    await user_crud.create(db_session, other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    calendar = await calendar_crud.schema_owner_create(db_session, CalendarCreateSchema(name="Private"), test_user.id)
    await db_session.commit()

    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await calendar_crud.schema_owner_get(db_session, calendar.id, other_user.id)
    assert exc_info.value.status_code == 404
