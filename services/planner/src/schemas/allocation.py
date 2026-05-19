import datetime as dt
from typing import TYPE_CHECKING, Literal

from pydantic import Field

from src.core.config import BaseSchema
AllocationTypeCode = Literal[
    "interest",
    "importance",
    "interest_importance",
    "points_allocation",
    "force_procrastinate",
]

if TYPE_CHECKING:
    from src.schemas.task import TaskSchema


class AllocationCreateSchema(BaseSchema):
    name: str = Field(max_length=128)
    type: AllocationTypeCode = "points_allocation"
    day_limits: dict | None = Field(default=None)


class AllocationUpdateSchema(BaseSchema):
    name: str | None = Field(max_length=128)
    type: AllocationTypeCode | None = None
    day_limits: dict | None = None


class AllocationSchema(BaseSchema):
    id: int
    name: str
    type: AllocationTypeCode
    day_limits: dict | None
    calendar_id: int
    created_at: dt.datetime


class AllocationWithTasksSchema(AllocationSchema):
    tasks: list["TaskSchema"] = []


class AllocationApplyResultSchema(BaseSchema):
    allocation_id: int
    task_executions_created: int
    days_processed: int


class AllocationTypeSchema(BaseSchema):
    code: AllocationTypeCode
    name: str


class AllocationCreateAndApplySchema(AllocationCreateSchema):
    start_date: dt.date | None = None
