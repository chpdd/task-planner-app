from fastapi import Depends, APIRouter, Request

from src.core.dependencies import db_dep, redis_dep
from src.core.cache import delete_cache_by_prefix

from src.crud import manual_day_crud
from src.schemas import manual_day as schemas

router = APIRouter(prefix="/manual_days", tags=["ManualDays"])


@router.get("")
async def list_manual_days(request: Request, session: db_dep) -> list[
    schemas.ManualDaySchema]:
    return await manual_day_crud.schema_owner_list(session, owner_id=request.state.user_id)


@router.post("")
async def create_manual_day(request: Request, manual_day_schema: schemas.CreateManualDaySchema,
                            session: db_dep, redis: redis_dep) -> schemas.ManualDaySchema:
    user_id = request.state.user_id
    manual_day_schema = await manual_day_crud.schema_owner_create(session, manual_day_schema, user_id)
    await session.commit()
    
    # Изменение ручных дней влияет на будущие аллокации
    await delete_cache_by_prefix(redis, f"planner:calendar:{user_id}")
    await delete_cache_by_prefix(redis, f"planner:calendar_with_tasks:{user_id}")
    
    return manual_day_schema


@router.get("/{manual_day_id}")
async def get_manual_day(request: Request, manual_day_id: int, session: db_dep) -> schemas.ManualDaySchema:
    return await manual_day_crud.schema_owner_get(session, manual_day_id, request.state.user_id)
