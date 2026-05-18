from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from src.crud import SchemaCRUD
from src.models import Calendar
from src.schemas.calendar import CalendarCreateSchema, OwnerCalendarSchema


class CalendarCRUD(SchemaCRUD[Calendar, CalendarCreateSchema, OwnerCalendarSchema]):
    async def schema_delete_by_id(self, session: AsyncSession, obj_id: int) -> None:
        from sqlalchemy import select
        stmt = select(Calendar).where(Calendar.id == obj_id)
        obj = await session.scalar(stmt)
        if obj is not None:
            await session.delete(obj)
            await session.flush()

    async def schema_owner_get(self, session: AsyncSession, obj_id: int, owner_id: int) -> OwnerCalendarSchema:
        """Override to use user_id instead of owner_id."""
        from sqlalchemy import select
        stmt = select(Calendar).where(Calendar.id == obj_id)
        calendar = await session.scalar(stmt)
        if calendar is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calendar not found")
        if calendar.user_id != owner_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calendar not found")
        return OwnerCalendarSchema.model_validate(calendar)

    async def schema_owner_list(self, session: AsyncSession, owner_id: int) -> list[OwnerCalendarSchema]:
        """Override to use user_id instead of owner_id."""
        from sqlalchemy import select
        stmt = select(Calendar).where(Calendar.user_id == owner_id)
        calendars = await session.scalars(stmt)
        return [OwnerCalendarSchema.model_validate(c) for c in calendars]

    async def schema_owner_create(self, session: AsyncSession, obj_schema: CalendarCreateSchema,
                                  owner_id: int) -> OwnerCalendarSchema:
        """Override to use user_id instead of owner_id."""
        calendar = Calendar(user_id=owner_id, **obj_schema.model_dump())
        session.add(calendar)
        await session.flush()
        await session.refresh(calendar)
        return OwnerCalendarSchema.model_validate(calendar)


calendar_crud: CalendarCRUD = CalendarCRUD(Calendar, CalendarCreateSchema, OwnerCalendarSchema)
