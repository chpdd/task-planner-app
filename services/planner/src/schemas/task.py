import datetime as dt
from typing import Annotated

from pydantic import Field

from src.core.config import BaseSchema


class CreateTaskSchema(BaseSchema):
    name: str = Field(max_length=128)
    deadline: Annotated[dt.date | None, Field(default=None)]
    interest: Annotated[int | None, Field(ge=1, le=10, default=None)]
    importance: Annotated[int | None, Field(ge=1, le=10, default=None)]
    work_hours: Annotated[int | None, Field(ge=1, default=None)]
    tags: list[str] = Field(default_factory=list)
    is_ai_created: bool = False


class UpdateTaskSchema(BaseSchema):
    name: str | None = Field(default=None, max_length=128)
    deadline: Annotated[dt.date | None, Field(default=None)]
    interest: Annotated[int | None, Field(ge=1, le=10, default=None)]
    importance: Annotated[int | None, Field(ge=1, le=10, default=None)]
    work_hours: Annotated[int | None, Field(ge=1, default=None)]
    tags: list[str] | None = None
    is_ai_created: bool | None = None


class TaskSchema(CreateTaskSchema):
    id: int


class OwnerTaskSchema(TaskSchema):
    owner_id: int
