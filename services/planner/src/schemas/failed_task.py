from src.core.config import BaseSchema


class CreateFailedTaskSchema(BaseSchema):
    allocation_id: int
    task_id: int


class FailedTaskSchema(CreateFailedTaskSchema):
    id: int
