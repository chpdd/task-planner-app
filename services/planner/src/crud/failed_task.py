from sqlalchemy import delete, select

from src.schemas.failed_task import CreateFailedTaskSchema, FailedTaskSchema
from src.models import Allocation, Calendar, FailedTask
from src.crud import SchemaCRUD


class FailedTaskCRUD(SchemaCRUD[FailedTask, CreateFailedTaskSchema, FailedTaskSchema]):
    async def list_by_allocation(self, session, allocation_id: int, user_id: int) -> list[FailedTaskSchema]:
        stmt = (
            select(FailedTask)
            .join(Allocation, FailedTask.allocation_id == Allocation.id)
            .join(Calendar, Allocation.calendar_id == Calendar.id)
            .where(FailedTask.allocation_id == allocation_id, Calendar.user_id == user_id)
        )
        result = await session.scalars(stmt)
        return [self.retrieve_schema.model_validate(obj) for obj in result]

    async def delete_by_allocation_id(self, session, allocation_id: int) -> None:
        stmt = delete(FailedTask).where(FailedTask.allocation_id == allocation_id)
        await session.execute(stmt)


failed_task_crud: FailedTaskCRUD = FailedTaskCRUD(FailedTask, CreateFailedTaskSchema, FailedTaskSchema)
