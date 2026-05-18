import pytest

from src.crud import allocation_crud, calendar_crud, user_crud
from src.models import User
from src.models.allocation import AllocationType
from src.schemas.allocation import AllocationCreateSchema, AllocationUpdateSchema
from src.schemas.calendar import CalendarCreateSchema
from src.core import security


@pytest.fixture
async def test_user(db_session):
    user = User(
        name="allocationowner",
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
        CalendarCreateSchema(name="Test Calendar"),
        test_user.id
    )


@pytest.mark.asyncio
async def test_create_allocation(db_session, test_calendar):
    alloc_in = AllocationCreateSchema(
        name="Test Allocation",
        type=AllocationType.PRIORITY
    )
    allocation = await allocation_crud.create_for_calendar(db_session, test_calendar.id, alloc_in)
    assert allocation.name == "Test Allocation"
    assert allocation.type == AllocationType.PRIORITY
    assert allocation.calendar_id == test_calendar.id


@pytest.mark.asyncio
async def test_list_allocations_for_calendar(db_session, test_calendar):
    await allocation_crud.create_for_calendar(
        db_session, test_calendar.id, AllocationCreateSchema(name="Alloc 1")
    )
    await allocation_crud.create_for_calendar(
        db_session, test_calendar.id, AllocationCreateSchema(name="Alloc 2")
    )
    await db_session.commit()

    allocations = await allocation_crud.list_by_calendar(
        db_session, test_calendar.id, test_calendar.user_id
    )
    assert len(allocations) >= 2
    names = [a.name for a in allocations]
    assert "Alloc 1" in names
    assert "Alloc 2" in names


@pytest.mark.asyncio
async def test_get_allocation(db_session, test_calendar):
    alloc_in = AllocationCreateSchema(name="Get Allocation")
    allocation = await allocation_crud.create_for_calendar(db_session, test_calendar.id, alloc_in)
    await db_session.commit()

    stored = await allocation_crud.get_by_id_and_owner(
        db_session, allocation.id, test_calendar.user_id
    )
    assert stored is not None
    assert stored.id == allocation.id
    assert stored.name == "Get Allocation"


@pytest.mark.asyncio
async def test_update_allocation(db_session, test_calendar):
    allocation = await allocation_crud.create_for_calendar(
        db_session, test_calendar.id, AllocationCreateSchema(name="Old Name")
    )
    await db_session.commit()

    update_data = AllocationUpdateSchema(name="New Name", type=AllocationType.COMPACT)
    updated = await allocation_crud.update_by_id(db_session, allocation.id, update_data)
    assert updated.name == "New Name"
    assert updated.type == AllocationType.COMPACT


@pytest.mark.asyncio
async def test_delete_allocation(db_session, test_calendar):
    allocation = await allocation_crud.create_for_calendar(
        db_session, test_calendar.id, AllocationCreateSchema(name="Delete Me")
    )
    await db_session.commit()
    alloc_id = allocation.id

    await allocation_crud.delete_by_id(db_session, alloc_id)

    stored = await allocation_crud.get_by_id(db_session, alloc_id)
    assert stored is None


@pytest.mark.asyncio
async def test_get_or_raise(db_session, test_calendar):
    allocation = await allocation_crud.create_for_calendar(
        db_session, test_calendar.id, AllocationCreateSchema(name="Raise Test")
    )
    await db_session.commit()

    result = await allocation_crud.get_or_raise(db_session, allocation.id, test_calendar.user_id)
    assert result.id == allocation.id


@pytest.mark.asyncio
async def test_get_or_raise_not_found(db_session, test_calendar):
    from src.core.exceptions import RowNotFoundError
    with pytest.raises(RowNotFoundError) as exc_info:
        await allocation_crud.get_or_raise(db_session, 99999, test_calendar.user_id)
    assert "99999" in str(exc_info.value)
