from sqlalchemy import delete
from sqlalchemy import select

from src.crud import SchemaCRUD
from src.models import Calendar, Day, TaskExecution
from src.schemas.task_execution import CreateTaskExecutionSchema, TaskExecutionSchema


class TaskExecutionCRUD(SchemaCRUD[TaskExecution, CreateTaskExecutionSchema, TaskExecutionSchema]):
    async def schema_owner_get(self, session, obj_id: int, owner_id: int) -> TaskExecutionSchema:
        stmt = (
            select(TaskExecution)
            .join(Day, TaskExecution.day_id == Day.id)
            .join(Calendar, Day.calendar_id == Calendar.id)
            .where(TaskExecution.id == obj_id, Calendar.user_id == owner_id)
        )
        obj = await session.scalar(stmt)
        if obj is None:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TaskExecution not found")
        return self.retrieve_schema.model_validate(obj)

    async def schema_owner_create(
        self,
        session,
        obj_schema: CreateTaskExecutionSchema,
        owner_id: int,
        day_id: int,
    ) -> TaskExecutionSchema:
        day_stmt = (
            select(Day)
            .join(Calendar, Day.calendar_id == Calendar.id)
            .where(Day.id == day_id, Calendar.user_id == owner_id)
        )
        day = await session.scalar(day_stmt)
        if day is None:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Day not found")

        obj = self.orm_model(**obj_schema.model_dump(), day_id=day_id)
        await self.create(session, obj)
        return self.retrieve_schema.model_validate(obj)

    async def delete_by_allocation_id(self, session, allocation_id: int) -> None:
        stmt = delete(TaskExecution).where(TaskExecution.allocation_id == allocation_id)
        await session.execute(stmt)


task_execution_crud: TaskExecutionCRUD = TaskExecutionCRUD(
    TaskExecution, CreateTaskExecutionSchema, TaskExecutionSchema
)
