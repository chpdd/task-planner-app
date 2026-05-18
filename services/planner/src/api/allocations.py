import datetime as dt

from fastapi import APIRouter, HTTPException, Request, status
from src.core.cache import delete_cache_by_prefix, get_cache, set_cache
from src.core.dependencies import db_dep, redis_dep
from src.crud import allocation_crud, calendar_crud
from src.schemas import allocation
from src.services import AllocationPlannerMethod, apply_allocation_plan

router = APIRouter(prefix="/allocations", tags=["Allocations"])


@router.get("/allocation_types", response_model=list[allocation.AllocationTypeSchema])
async def list_allocation_types(redis: redis_dep) -> list[allocation.AllocationTypeSchema]:
    cache_key = "planner:allocation_types:v1"
    cached = await get_cache(redis, cache_key, list[allocation.AllocationTypeSchema])
    if cached is not None:
        return cached
    result = [
        allocation.AllocationTypeSchema(code="even", name="Равномерное"),
        allocation.AllocationTypeSchema(code="priority", name="По приоритету"),
        allocation.AllocationTypeSchema(code="compact", name="Компактное"),
    ]
    await set_cache(redis, cache_key, result, list[allocation.AllocationTypeSchema], expire=60 * 60 * 24 * 30)
    return result


@router.get("/by_calendar/{calendar_id}")
async def list_allocations(
    request: Request,
    calendar_id: int,
    session: db_dep,
) -> list[allocation.AllocationSchema]:
    user_id = request.state.user_id
    calendar = await calendar_crud.get(session, calendar_id)
    if calendar is None or calendar.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calendar not found")
    allocations = await allocation_crud.list_by_calendar(session, calendar_id, user_id)
    return [allocation.AllocationSchema.model_validate(a) for a in allocations]


@router.get("")
async def list_allocations_for_user(
    request: Request,
    session: db_dep,
) -> list[allocation.AllocationSchema]:
    user_id = request.state.user_id
    allocations = await allocation_crud.list_by_owner(session, user_id)
    return [allocation.AllocationSchema.model_validate(a) for a in allocations]


@router.post("/by_calendar/{calendar_id}")
async def create_allocation(
    request: Request,
    calendar_id: int,
    schema: allocation.AllocationCreateSchema,
    session: db_dep,
    redis: redis_dep,
) -> allocation.AllocationSchema:
    user_id = request.state.user_id
    calendar = await calendar_crud.get(session, calendar_id)
    if calendar is None or calendar.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calendar not found")
    alloc = await allocation_crud.create_for_calendar(session, calendar_id, schema)
    await session.commit()
    await delete_cache_by_prefix(redis, f"planner:calendar:{user_id}")
    await delete_cache_by_prefix(redis, f"planner:calendar_with_tasks:{user_id}")
    return allocation.AllocationSchema.model_validate(alloc)


@router.post("")
async def create_allocation_for_calendar(
    request: Request,
    calendar_id: int,
    schema: allocation.AllocationCreateSchema,
    session: db_dep,
    redis: redis_dep,
) -> allocation.AllocationSchema:
    user_id = request.state.user_id
    calendar = await calendar_crud.get(session, calendar_id)
    if calendar is None or calendar.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calendar not found")
    alloc = await allocation_crud.create_for_calendar(session, calendar_id, schema)
    await session.commit()
    await delete_cache_by_prefix(redis, f"planner:calendar:{user_id}")
    await delete_cache_by_prefix(redis, f"planner:calendar_with_tasks:{user_id}")
    return allocation.AllocationSchema.model_validate(alloc)


@router.post("/create_and_apply", response_model=allocation.AllocationApplyResultSchema)
async def create_and_apply_allocation(
    request: Request,
    calendar_id: int,
    schema: allocation.AllocationCreateAndApplySchema,
    session: db_dep,
    redis: redis_dep,
    method: AllocationPlannerMethod | None = None,
) -> allocation.AllocationApplyResultSchema:
    user_id = request.state.user_id
    calendar = await calendar_crud.get(session, calendar_id)
    if calendar is None or calendar.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calendar not found")

    create_schema = allocation.AllocationCreateSchema(
        name=schema.name,
        type=schema.type,
        day_limits=schema.day_limits,
    )
    alloc = await allocation_crud.create_for_calendar(session, calendar_id, create_schema)
    result = await apply_allocation_plan(
        session=session,
        allocation=alloc,
        user_id=user_id,
        method=method,
        start_date=schema.start_date,
    )
    await session.commit()
    await delete_cache_by_prefix(redis, f"planner:calendar:{user_id}")
    await delete_cache_by_prefix(redis, f"planner:calendar_with_tasks:{user_id}")
    return result


@router.get("/{allocation_id}")
async def get_allocation(
    request: Request,
    allocation_id: int,
    session: db_dep,
) -> allocation.AllocationSchema:
    user_id = request.state.user_id
    alloc = await allocation_crud.get_or_raise(session, allocation_id, user_id)
    return allocation.AllocationSchema.model_validate(alloc)


@router.patch("/{allocation_id}")
async def update_allocation(
    request: Request,
    allocation_id: int,
    schema: allocation.AllocationUpdateSchema,
    session: db_dep,
    redis: redis_dep,
) -> allocation.AllocationSchema:
    user_id = request.state.user_id
    await allocation_crud.get_or_raise(session, allocation_id, user_id)
    alloc = await allocation_crud.update_by_id(session, allocation_id, schema)
    await session.commit()
    await delete_cache_by_prefix(redis, f"planner:calendar:{user_id}")
    await delete_cache_by_prefix(redis, f"planner:calendar_with_tasks:{user_id}")
    return allocation.AllocationSchema.model_validate(alloc)


@router.delete("/{allocation_id}")
async def delete_allocation(
    request: Request,
    allocation_id: int,
    session: db_dep,
    redis: redis_dep,
) -> dict:
    user_id = request.state.user_id
    await allocation_crud.get_or_raise(session, allocation_id, user_id)
    await allocation_crud.delete_by_id(session, allocation_id)
    await session.commit()
    await delete_cache_by_prefix(redis, f"planner:calendar:{user_id}")
    await delete_cache_by_prefix(redis, f"planner:calendar_with_tasks:{user_id}")
    return {"detail": "Allocation deleted"}


@router.post("/{allocation_id}/apply", response_model=allocation.AllocationApplyResultSchema)
async def apply_allocation(
    request: Request,
    allocation_id: int,
    session: db_dep,
    redis: redis_dep,
    method: AllocationPlannerMethod | None = None,
    start_date: dt.date = dt.date.today(),
) -> allocation.AllocationApplyResultSchema:
    user_id = request.state.user_id
    alloc = await allocation_crud.get_or_raise(session, allocation_id, user_id)
    result = await apply_allocation_plan(
        session=session,
        allocation=alloc,
        user_id=user_id,
        method=method,
        start_date=start_date,
    )
    await session.commit()
    await delete_cache_by_prefix(redis, f"planner:calendar:{user_id}")
    await delete_cache_by_prefix(redis, f"planner:calendar_with_tasks:{user_id}")
    return result
