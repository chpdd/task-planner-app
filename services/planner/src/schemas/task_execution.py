from typing import Annotated

from pydantic import Field

from src.core.config import BaseSchema
from src.schemas.task import TaskSchema


class CreateTaskExecutionSchema(BaseSchema):
    doing_hours: Annotated[int, Field(ge=1)]
    task_id: int


class TaskExecutionUpdateSchema(BaseSchema):
    doing_hours: Annotated[int | None, Field(ge=1)] = None
    is_done: bool | None = None


class IdTaskExecutionSchema(CreateTaskExecutionSchema):
    id: int


class TaskExecutionSchema(IdTaskExecutionSchema):
    day_id: int


class TaskAndExecutionSchema(BaseSchema):
    doing_hours: int
    task: TaskSchema


class MoveTaskExecutionSchema(BaseSchema):
    task_execution_id: int
    target_day_id: int | None = None
    new_day_index: int | None = None
