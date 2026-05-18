from fastapi import APIRouter, Request
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core.dependencies import db_dep
from src.crud import calendar_crud
from src.models import Calendar
from src.schemas import calendar as schemas

router = APIRouter(prefix="/calendars", tags=["Calendar"])


@router.get("")
async def list_calendars(request: Request, session: db_dep) -> list[schemas.CalendarSchema]:
    return await calendar_crud.schema_owner_list(session, owner_id=request.state.user_id)


@router.get("/with_allocations", response_model=list[schemas.CalendarWithAllocationsSchema])
async def list_calendars_with_allocations(
    request: Request, session: db_dep
) -> list[schemas.CalendarWithAllocationsSchema]:
    stmt = (
        select(Calendar)
        .options(selectinload(Calendar.allocations))
        .where(Calendar.user_id == request.state.user_id)
    )
    calendars = list((await session.scalars(stmt)).all())
    return [schemas.CalendarWithAllocationsSchema.model_validate(c) for c in calendars]


@router.post("")
async def create_calendar(
    request: Request,
    calendar_schema: schemas.CalendarCreateSchema,
    session: db_dep,
) -> schemas.CalendarSchema:
    user_id = request.state.user_id
    calendar_schema = await calendar_crud.schema_owner_create(session, calendar_schema, user_id)
    await session.commit()
    return calendar_schema


@router.get("/{calendar_id}")
async def get_calendar(
    request: Request,
    calendar_id: int,
    session: db_dep,
) -> schemas.CalendarSchema:
    return await calendar_crud.schema_owner_get(session, calendar_id, request.state.user_id)


@router.patch("/{calendar_id}")
async def update_calendar(
    request: Request,
    calendar_id: int,
    calendar_schema: schemas.CalendarUpdateSchema,
    session: db_dep,
) -> schemas.CalendarSchema:
    user_id = request.state.user_id
    await calendar_crud.schema_owner_get(session, calendar_id, user_id)
    result = await calendar_crud.schema_update_by_id(session, calendar_id, calendar_schema)
    await session.commit()
    return result


@router.delete("/{calendar_id}")
async def delete_calendar(
    request: Request,
    calendar_id: int,
    session: db_dep,
) -> dict:
    user_id = request.state.user_id
    await calendar_crud.schema_owner_get(session, calendar_id, user_id)
    await calendar_crud.schema_delete_by_id(session, calendar_id)
    await session.commit()
    return {"status": "ok"}
