from redis import asyncio as aioredis
from typing import Optional

from src.core.config import settings


class RedisService:
    def __init__(self):
        self.redis_client: Optional[aioredis.Redis] = None

    async def connect(self):
        self.redis_client = aioredis.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
            encoding="utf-8",
            decode_responses=True
        )
        # Проверка соединения
        await self.redis_client.ping()

    async def close(self):
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
    
    @property
    def client(self) -> aioredis.Redis:
        if not self.redis_client:
             raise RuntimeError("Redis client is not initialized. Call connect() first.")
        return self.redis_client

# Создаем единственный экземпляр сервиса
redis_service = RedisService()