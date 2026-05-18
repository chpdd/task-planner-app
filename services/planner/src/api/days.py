import datetime as dt

from fastapi import APIRouter, Query, Request

from src.core.dependencies import db_dep
from src.crud import day_crud
from src.schemas.day import CreateDaySchema, DaySchema, DayUpdateSchema

router = APIRouter(tags=["Days"])


@router.get("/calendars/{calendar_id}/days", response_model=list[DaySchema])
async def list_days(
    request: Request,
    calendar_id: int,
    session: db_dep,
    start_date: dt.date | None = Query(default=None),
    end_date: dt.date | None = Query(default=None),
) -> list[DaySchema]:
    user_id = request.state.user_id
    return await day_crud.schema_calendar_list(
        session, calendar_id, user_id, start_date=start_date, end_date=end_date
    )


@router.post("/calendars/{calendar_id}/days", response_model=DaySchema, status_code=201)
async def create_day(
    request: Request,
    calendar_id: int,
    day_schema: CreateDaySchema,
    session: db_dep,
) -> DaySchema:
    user_id = request.state.user_id
    day = await day_crud.schema_calendar_create(session, day_schema, calendar_id, user_id)
    await session.commit()
    return day


@router.get("/days/{day_id}", response_model=DaySchema)
async def get_day(
    request: Request,
    day_id: int,
    session: db_dep,
) -> DaySchema:
    user_id = request.state.user_id
    return await day_crud.schema_owner_get_by_id(session, day_id, user_id)


@router.patch("/days/{day_id}", response_model=DaySchema)
async def update_day(
    request: Request,
    day_id: int,
    day_schema: DayUpdateSchema,
    session: db_dep,
) -> DaySchema:
    user_id = request.state.user_id
    day = await day_crud.schema_owner_get_by_id(session, day_id, user_id)
    result = await day_crud.update(session, day, **day_schema.model_dump(exclude_unset=True))
    await session.commit()
    return result


@router.delete("/days/{day_id}", status_code=204)
async def delete_day(
    request: Request,
    day_id: int,
    session: db_dep,
) -> None:
    user_id = request.state.user_id
    day = await day_crud.schema_owner_get_by_id(session, day_id, user_id)
    await day_crud.delete(session, day)
    await session.commit()
