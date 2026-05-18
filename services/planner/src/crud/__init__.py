from src.crud.allocation import allocation_crud
from src.crud.base import BaseCRUD, SchemaCRUD
from src.crud.calendar import calendar_crud
from src.crud.day import day_crud
from src.crud.failed_task import failed_task_crud
from src.crud.manual_day import manual_day_crud
from src.crud.task import task_crud
from src.crud.task_execution import task_execution_crud
from src.crud.user import user_crud

__all__ = [
    'BaseCRUD',
    'SchemaCRUD',
    'user_crud',
    'manual_day_crud',
    'task_crud',
    'day_crud',
    'task_execution_crud',
    'failed_task_crud',
    'calendar_crud',
    'allocation_crud',
]
