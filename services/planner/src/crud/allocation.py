from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import RowNotFoundError
from src.crud.base import BaseCRUD
from src.models import Allocation, Calendar
from src.schemas.allocation import AllocationCreateSchema, AllocationUpdateSchema


class AllocationCRUD(BaseCRUD[Allocation]):

    def __init__(self):
        super().__init__(Allocation)

    async def get_by_id(self, session: AsyncSession, allocation_id: int) -> Allocation | None:
        stmt = select(Allocation).where(Allocation.id == allocation_id)
        return await session.scalar(stmt)

    async def get_by_id_and_owner(
        self, session: AsyncSession, allocation_id: int, user_id: int
    ) -> Allocation | None:
        stmt = (
            select(Allocation)
            .join(Calendar, Allocation.calendar_id == Calendar.id)
            .where(and_(Allocation.id == allocation_id, Calendar.user_id == user_id))
        )
        return await session.scalar(stmt)

    async def list_by_calendar(
        self, session: AsyncSession, calendar_id: int, user_id: int
    ) -> list[Allocation]:
        stmt = (
            select(Allocation)
            .join(Calendar, Allocation.calendar_id == Calendar.id)
            .where(and_(Calendar.id == calendar_id, Calendar.user_id == user_id))
        )
        result = await session.scalars(stmt)
        return list(result.all())

    async def list_by_owner(self, session: AsyncSession, user_id: int) -> list[Allocation]:
        stmt = (
            select(Allocation)
            .join(Calendar, Allocation.calendar_id == Calendar.id)
            .where(Calendar.user_id == user_id)
        )
        result = await session.scalars(stmt)
        return list(result.all())

    async def create_for_calendar(
        self, session: AsyncSession, calendar_id: int, schema: AllocationCreateSchema
    ) -> Allocation:
        allocation = Allocation(
            calendar_id=calendar_id,
            **schema.model_dump(),
        )
        session.add(allocation)
        await session.flush()
        await session.refresh(allocation)
        return allocation

    async def update_by_id(
        self, session: AsyncSession, allocation_id: int, schema: AllocationUpdateSchema
    ) -> Allocation:
        allocation = await self.get(session, allocation_id)
        if allocation is None:
            raise RowNotFoundError(f"Allocation with id={allocation_id} not found")

        update_data = schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(allocation, key, value)

        await session.flush()
        await session.refresh(allocation)
        return allocation

    async def delete_by_id(self, session: AsyncSession, allocation_id: int) -> None:
        from sqlalchemy import select
        stmt = select(Allocation).where(Allocation.id == allocation_id)
        allocation = await session.scalar(stmt)
        if allocation is not None:
            await session.delete(allocation)
            await session.flush()

    async def get_or_raise(
        self, session: AsyncSession, allocation_id: int, user_id: int
    ) -> Allocation:
        allocation = await self.get_by_id_and_owner(session, allocation_id, user_id)
        if allocation is None:
            raise RowNotFoundError(f"Allocation with id={allocation_id} not found")
        return allocation


allocation_crud: AllocationCRUD = AllocationCRUD()
