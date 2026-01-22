import pytest
from unittest.mock import AsyncMock, MagicMock
from src.core.cache import set_cache, get_cache, delete_cache_by_prefix
from pydantic import BaseModel

class MockSchema(BaseModel):
    id: int
    name: str

@pytest.mark.asyncio
async def test_set_get_cache_object():
    redis = AsyncMock()
    key = "test_key"
    value = MockSchema(id=1, name="test")
    
    # Mock redis.get to return serialized value
    redis.get.return_value = value.model_dump_json()
    
    # Test set_cache
    await set_cache(redis, key, value, MockSchema)
    redis.setex.assert_called_once()
    
    # Test get_cache
    result = await get_cache(redis, key, MockSchema)
    assert result.id == 1
    assert result.name == "test"
    assert isinstance(result, MockSchema)

@pytest.mark.asyncio
async def test_set_get_cache_list():
    redis = AsyncMock()
    key = "test_list_key"
    values = [MockSchema(id=1, name="test1"), MockSchema(id=2, name="test2")]
    
    # Mock redis.get to return serialized list
    from pydantic import TypeAdapter
    adapter = TypeAdapter(list[MockSchema])
    redis.get.return_value = adapter.dump_json(values)
    
    # Test set_cache
    await set_cache(redis, key, values, list[MockSchema])
    redis.setex.assert_called_once()
    
    # Test get_cache
    result = await get_cache(redis, key, list[MockSchema])
    assert len(result) == 2
    assert result[0].name == "test1"
    assert result[1].name == "test2"

@pytest.mark.asyncio
async def test_delete_cache_by_prefix():
    redis = AsyncMock()
    prefix = "planner:calendar"
    redis.keys.return_value = [b"planner:calendar:1", b"planner:calendar:2"]
    
    await delete_cache_by_prefix(redis, prefix)
    
    redis.keys.assert_called_with(f"{prefix}*")
    redis.delete.assert_called_once_with(b"planner:calendar:1", b"planner:calendar:2")

@pytest.mark.asyncio
async def test_get_cache_miss():
    redis = AsyncMock()
    redis.get.return_value = None
    
    result = await get_cache(redis, "missing", MockSchema)
    assert result is None
