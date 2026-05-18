import datetime as dt

from pydantic import Field

from src.core.config import BaseSchema
from src.schemas.task_execution import CreateTaskExecutionSchema, TaskAndExecutionSchema


class CreateDaySchema(BaseSchema):
    date: dt.date = Field()
    work_hours: int | None = Field(ge=0, le=24)


class DaySchema(CreateDaySchema):
    id: int


class DayUpdateSchema(BaseSchema):
    work_hours: int | None = Field(ge=0, le=24)


class CreateTaskExecutionsDaySchema(CreateDaySchema):
    task_executions: list[CreateTaskExecutionSchema]


class TaskExecutionsDaySchema(CreateTaskExecutionsDaySchema):
    id: int


class TasksDaySchema(DaySchema):
    task_executions: list[TaskAndExecutionSchema]
