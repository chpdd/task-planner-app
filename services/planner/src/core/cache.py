import json
from typing import Any, TypeVar, Type
from pydantic import BaseModel, TypeAdapter
from redis.asyncio import Redis

T = TypeVar("T", bound=BaseModel)

async def set_cache(redis: Redis, key: str, value: Any, schema: Type[T] | None = None, expire: int = 3600):
    """
    Устанавливает значение в кэш. Если передан schema, сериализует список или объект.
    """
    if schema:
        # Используем TypeAdapter для работы со списками или одиночными объектами
        adapter = TypeAdapter(schema)
        data = adapter.dump_json(value).decode("utf-8")
    else:
        data = json.dumps(value)
    
    await redis.setex(key, expire, data)

async def get_cache(redis: Redis, key: str, schema: Type[T] | None = None) -> Any:
    """
    Получает значение из кэша. Если передан schema, десериализует его.
    """
    data = await redis.get(key)
    if not data:
        return None
    
    if schema:
        adapter = TypeAdapter(schema)
        return adapter.validate_json(data)
    
    return json.loads(data)

async def delete_cache_by_prefix(redis: Redis, prefix: str):
    """
    Удаляет все ключи по префиксу.
    """
    keys = await redis.keys(f"{prefix}*")
    if keys:
        await redis.delete(*keys)
