from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import SchemaCRUD
from src.models import Calendar, Day
from src.schemas.day import CreateDaySchema, DaySchema, DayUpdateSchema


class DayCRUD(SchemaCRUD[Day, CreateDaySchema, DaySchema]):
    async def schema_owner_get_by_id(self, session: AsyncSession, day_id: int, owner_id: int) -> DaySchema:
        """Get day by ID and verify ownership through calendar."""
        stmt = (
            select(Day)
            .join(Calendar, Day.calendar_id == Calendar.id)
            .where(Day.id == day_id, Calendar.user_id == owner_id)
        )
        day = await session.scalar(stmt)
        if day is None:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Day not found")
        return self.retrieve_schema.model_validate(day)

    async def schema_list_for_owner(
        self,
        session: AsyncSession,
        owner_id: int,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[DaySchema]:
        """List days for a specific owner via calendar chain."""
        stmt = (
            select(self.orm_model)
            .join(Calendar, self.orm_model.calendar_id == Calendar.id)
            .where(Calendar.user_id == owner_id)
        )
        if start_date is not None:
            stmt = stmt.where(self.orm_model.date >= start_date)
        if end_date is not None:
            stmt = stmt.where(self.orm_model.date <= end_date)
        stmt = stmt.order_by(self.orm_model.date)
        days = await session.scalars(stmt)
        return [self.retrieve_schema.model_validate(day) for day in days]

    async def schema_calendar_list(
        self,
        session: AsyncSession,
        calendar_id: int,
        owner_id: int,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[DaySchema]:
        """List days for a specific calendar."""
        stmt = (
            select(self.orm_model)
            .join(Calendar, self.orm_model.calendar_id == Calendar.id)
            .where(
                self.orm_model.calendar_id == calendar_id,
                Calendar.user_id == owner_id,
            )
        )
        if start_date is not None:
            stmt = stmt.where(self.orm_model.date >= start_date)
        if end_date is not None:
            stmt = stmt.where(self.orm_model.date <= end_date)
        stmt = stmt.order_by(self.orm_model.date)
        days = await session.scalars(stmt)
        return [self.retrieve_schema.model_validate(day) for day in days]

    async def schema_calendar_create(
        self, session: AsyncSession, obj_schema: CreateDaySchema, calendar_id: int, owner_id: int
    ) -> DaySchema:
        """Create a day for a calendar."""
        calendar_stmt = select(Calendar).where(Calendar.id == calendar_id, Calendar.user_id == owner_id)
        calendar = await session.scalar(calendar_stmt)
        if calendar is None:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calendar not found")

        obj = self.orm_model(**obj_schema.model_dump(), calendar_id=calendar_id)
        await self.create(session, obj)
        return self.retrieve_schema.model_validate(obj)

    async def schema_calendar_update_by_id(
        self, session: AsyncSession, day_id: int, calendar_id: int, owner_id: int | None, update_schema: DayUpdateSchema
    ) -> DaySchema:
        """Update a day for a calendar."""
        from fastapi import HTTPException, status
        stmt = select(Day).where(Day.id == day_id, Day.calendar_id == calendar_id)
        if owner_id is not None:
            stmt = stmt.join(Calendar, Day.calendar_id == Calendar.id).where(Calendar.user_id == owner_id)
        day = await session.scalar(stmt)
        if day is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Day not found")
        update_data = update_schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(day, key, value)
        await session.flush()
        await session.refresh(day)
        return self.retrieve_schema.model_validate(day)

    async def schema_calendar_delete_by_id(
        self, session: AsyncSession, day_id: int, calendar_id: int, owner_id: int | None = None
    ) -> None:
        """Delete a day from a calendar."""
        from fastapi import HTTPException, status
        stmt = select(Day).where(Day.id == day_id, Day.calendar_id == calendar_id)
        if owner_id is not None:
            stmt = stmt.join(Calendar, Day.calendar_id == Calendar.id).where(Calendar.user_id == owner_id)
        day = await session.scalar(stmt)
        if day is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Day not found")
        await session.delete(day)
        await session.flush()


day_crud: DayCRUD = DayCRUD(Day, CreateDaySchema, DaySchema)
