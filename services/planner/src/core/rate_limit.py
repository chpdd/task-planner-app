from fastapi import Request, HTTPException, status
from src.core.redis import redis_service


class RateLimiter:
    def __init__(self, times: int, seconds: int):
        self.times = times
        self.seconds = seconds

    async def __call__(self, request: Request):
        redis = redis_service.client

        # Пытаемся получить user_id из state (если пользователь авторизован)
        # Если нет (например, на этапе логина в auth сервисе), используем IP
        user_id = getattr(request.state, "user_id", None)
        ip = request.client.host if request.client else "127.0.0.1"
        
        identifier = f"user:{user_id}" if user_id else f"ip:{ip}"
        
        # Ключ уникален для пути и идентификатора
        key = f"rate_limit:{request.url.path}:{identifier}"

        # Атомарно увеличиваем счетчик
        request_count = await redis.incr(key)

        # Если это первый запрос — ставим таймер жизни ключа (окно)
        if request_count == 1:
            await redis.expire(key, self.seconds)

        if request_count > self.times:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {self.times} requests per {self.seconds} seconds"
            )
