from fastapi import APIRouter

from src.api.ai import router as ai_router
from src.api.calendars import router as calendars_router
from src.api.days import router as days_router
from src.api.allocations import router as allocations_router
from src.api.manual_day import router as manual_day_router
from src.api.planner import router as planner_router
from src.api.task import router as task_router
from src.api.task_execution import router as task_execution_router

api_router = APIRouter()

api_router.include_router(planner_router)
api_router.include_router(task_router)
api_router.include_router(task_execution_router)
api_router.include_router(manual_day_router)
api_router.include_router(allocations_router)
api_router.include_router(calendars_router)
api_router.include_router(days_router)
api_router.include_router(ai_router)
