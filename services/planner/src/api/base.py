from fastapi import APIRouter

from src.api.planner import router as planner_router
from src.api.task import router as task_router
from src.api.manual_day import router as manual_day_router
from src.api.logger_check import router as logger_check_router

api_router = APIRouter()

api_router.include_router(planner_router)
api_router.include_router(task_router)
api_router.include_router(manual_day_router)
api_router.include_router(logger_check_router)
