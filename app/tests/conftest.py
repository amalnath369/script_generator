import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator

from app.core.main import app
from app.infrastructure.database.session import Base
from app.infrastructure.database.uow import  UnitOfWork
from app.interfaces.v1.api.dependencies.dependencies import get_uow

# Test database configuration
TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_password@postgres_db:5432/test_db"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False
)

# Test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


def override_get_uow():
    """Override UoW to use test database"""
    return UnitOfWork(TestSessionLocal)


# Override the dependency in your app
app.dependency_overrides[get_uow] = override_get_uow


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Create test database tables"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Cleanup
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await test_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_test_client() -> AsyncGenerator[AsyncClient, None]:
    """HTTP client for testing API endpoints"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        timeout=30.0
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def uow() -> AsyncGenerator[UnitOfWork, None]:
    """Unit of Work instance for direct repository testing"""
    uow_instance = UnitOfWork(TestSessionLocal)
    async with uow_instance:
        yield uow_instance
        await uow_instance.rollback()


@pytest.fixture(scope="function", autouse=True)
async def cleanup_database():
    """Clean database after each test"""
    yield
    # Truncate tables after each test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
