from fastapi import Depends, status, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from typing import Annotated

from src.core.database import engine, session_factory
from src.core.redis import redis_service
from src.models import User


async def get_autocommit_conn():
    async with engine.connect() as conn:
        await conn.execution_options(isolation_level="AUTOCOMMIT")

        yield conn


async def get_db():
    async with session_factory() as session:
        yield session


db_dep = Annotated[AsyncSession, Depends(get_db)]


async def get_redis_client() -> Redis:
    return redis_service.client


redis_dep = Annotated[Redis, Depends(get_redis_client)]


async def get_admin_id(request: Request, session: db_dep):
    user_id = request.state.user_id
    user = await session.get(User, user_id)
    if user and user.is_admin:
        return user_id
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access forbidden. This route is available only for admins.")


admin_id_dep = Annotated[int, Depends(get_admin_id)]
