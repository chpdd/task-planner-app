from fastapi import Depends, APIRouter, Request


from src.core.dependencies import db_dep, redis_dep
from src.core.cache import delete_cache_by_prefix

from src.crud import task_crud
from src.schemas import task as schemas

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("")
async def list_tasks(request: Request, session: db_dep) -> list[schemas.TaskSchema]:
    return await task_crud.schema_owner_list(session, owner_id=request.state.user_id)


@router.post("")
async def create_task(request: Request, task_schema: schemas.TaskSchema, session: db_dep,
                      redis: redis_dep) -> schemas.TaskSchema:
    user_id = request.state.user_id
    task_schema = await task_crud.schema_owner_create(session, task_schema, user_id)
    await session.commit()
    
    # Изменение задач может повлиять на расписание (хотя аллокация запускается вручную, 
    # лучше сбросить кэш, если мы кэшируем и список задач тоже в будущем)
    await delete_cache_by_prefix(redis, f"planner:calendar:{user_id}")
    await delete_cache_by_prefix(redis, f"planner:calendar_with_tasks:{user_id}")
    
    return task_schema


@router.get("/{task_id}")
async def get_task(request: Request, task_id: int, session: db_dep) -> schemas.TaskSchema:
    return await task_crud.schema_owner_get(session, task_id, request.state.user_id)


@router.patch("/{task_id}")
async def update_task(request: Request, task_schema: schemas.CreateTaskSchema, task_id: int, session: db_dep,
                      redis: redis_dep) -> schemas.TaskSchema:
    user_id = request.state.user_id
    task_schema = await task_crud.schema_update_by_id(session, task_id, task_schema)
    await session.commit()
    
    # Сбрасываем кэш, так как в calendar_with_tasks есть детали задач
    await delete_cache_by_prefix(redis, f"planner:calendar:{user_id}")
    await delete_cache_by_prefix(redis, f"planner:calendar_with_tasks:{user_id}")
    
    return task_schema
