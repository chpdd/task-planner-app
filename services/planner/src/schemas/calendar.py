from pydantic import Field

from src.core.config import BaseSchema
from src.schemas.allocation import AllocationSchema


class CalendarCreateSchema(BaseSchema):
    name: str = Field(max_length=128)


class CalendarUpdateSchema(BaseSchema):
    name: str | None = Field(default=None, max_length=128)


class CalendarSchema(BaseSchema):
    id: int
    name: str


class OwnerCalendarSchema(CalendarSchema):
    user_id: int


class CalendarWithAllocationsSchema(CalendarSchema):
    allocations: list[AllocationSchema]
