import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import Request, HTTPException, status
from src.core.rate_limit import RateLimiter
from src.core.redis import redis_service

@pytest.fixture
def mock_redis():
    # Мокаем клиент Redis внутри сервиса
    redis_mock = AsyncMock()
    redis_service.redis_client = redis_mock
    return redis_mock

@pytest.fixture
def request_with_user():
    req = MagicMock(spec=Request)
    req.state.user_id = 1
    req.client.host = "127.0.0.1"
    req.url.path = "/test"
    return req

@pytest.fixture
def request_anonymous():
    req = MagicMock(spec=Request)
    del req.state.user_id # Убеждаемся, что user_id нет
    req.client.host = "192.168.1.1"
    req.url.path = "/test"
    return req

@pytest.mark.asyncio
async def test_rate_limit_allowed(mock_redis, request_with_user):
    limiter = RateLimiter(times=5, seconds=60)
    
    # Эмулируем первый запрос (incr возвращает 1)
    mock_redis.incr.return_value = 1
    
    await limiter(request_with_user)
    
    # Проверяем, что вызвался expire для нового ключа
    mock_redis.incr.assert_called_with("rate_limit:/test:user:1")
    mock_redis.expire.assert_called_with("rate_limit:/test:user:1", 60)

@pytest.mark.asyncio
async def test_rate_limit_exceeded(mock_redis, request_with_user):
    limiter = RateLimiter(times=5, seconds=60)
    
    # Эмулируем 6-й запрос
    mock_redis.incr.return_value = 6
    
    with pytest.raises(HTTPException) as exc:
        await limiter(request_with_user)
    
    assert exc.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    mock_redis.incr.assert_called_with("rate_limit:/test:user:1")
    # Expire не должен вызываться для существующего ключа (если это не первый запрос)
    mock_redis.expire.assert_not_called()

@pytest.mark.asyncio
async def test_rate_limit_anonymous_ip(mock_redis, request_anonymous):
    limiter = RateLimiter(times=5, seconds=60)
    
    # Эмулируем запрос
    mock_redis.incr.return_value = 1
    
    # Нужно настроить getattr, так как MagicMock по умолчанию создает новые MagicMock
    # Но мы удалили атрибут в фикстуре, так что getattr вернет дефолтное значение None в коде
    
    await limiter(request_anonymous)
    
    # Проверяем, что ключ сформирован по IP
    mock_redis.incr.assert_called_with("rate_limit:/test:ip:192.168.1.1")
