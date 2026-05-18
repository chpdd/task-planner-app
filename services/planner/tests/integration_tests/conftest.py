import pytest
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from pathlib import Path
from alembic.config import Config
from alembic import command

from src.core.dependencies import get_db, get_redis_client
from src.main import app
from src.core.config import settings

engine = create_async_engine(
    settings.db_url,
    poolclass=NullPool,
)
test_session_factory = async_sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    assert settings.MODE == "test", f"A non-test environment has been set up ({settings.MODE=})"
    assert "test" in settings.DB_NAME, f'The test database name "{settings.DB_NAME}" does not have the word "test" in it'

    base_dir = Path("/app")
    alembic_ini_path = base_dir / "alembic.ini"
    alembic_cfg = Config(str(alembic_ini_path))
    try:
        command.upgrade(alembic_cfg, "head")
    except Exception:
        # When DB schema is already present (e.g. repeated local runs), align version table.
        command.stamp(alembic_cfg, "head")
    yield
    try:
        command.downgrade(alembic_cfg, "base")
    except Exception:
        # Fallback for partially-idempotent historical downgrade chain.
        command.stamp(alembic_cfg, "base")


@pytest.fixture(scope="function")
async def db_session():
    async with engine.connect() as connection:
        # Beginning the transaction
        transaction = await connection.begin()
        # Create session in connection
        # With join_transaction_mode="create_savepoint", rollback will rollback the nested transaction(savepoint),
        # not the entire session
        async with test_session_factory(bind=connection, join_transaction_mode="create_savepoint") as session:
            yield session

        # Rollback all changes made during the transaction
        await transaction.rollback()


@pytest.fixture(scope="function")
async def mock_redis():
    redis_mock = AsyncMock()
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.setex = AsyncMock(return_value=True)
    redis_mock.delete = AsyncMock(return_value=1)
    redis_mock.delete_pattern = AsyncMock(return_value=0)
    redis_mock.keys = AsyncMock(return_value=[])
    redis_mock.flushdb = AsyncMock()
    return redis_mock


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession, mock_redis):
    async def test_get_db():
        yield db_session

    async def test_get_redis():
        return mock_redis

    app.dependency_overrides[get_db] = test_get_db
    app.dependency_overrides[get_redis_client] = test_get_redis
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as async_client:
        yield async_client
    app.dependency_overrides.clear()
