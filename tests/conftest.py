# Pytest fixtures for async FastAPI tests.
import os
from urllib.parse import urlparse
import asyncpg
import pytest
import uuid
from dotenv import load_dotenv
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv('.env_422ca5fd-04e6-47e0-a569-9b11c4768453', override=True)

from app.main import app
from app.database import Base, get_db
from app.models import Customer, User
from app.core.security import get_password_hash

MAIN_DB_URL = os.getenv("DATABASE_URL", "")
_parts = MAIN_DB_URL.rsplit("/", 1)
TEST_DB_URL = (_parts[0] + "/" + _parts[1] + "_test") if len(_parts) == 2 else MAIN_DB_URL


def _build_admin_dsn(db_url: str) -> tuple[str, str]:
    parsed = urlparse(db_url.replace("postgresql+asyncpg", "postgresql"))
    db_name = parsed.path.lstrip("/")
    admin_db = "postgres"
    admin_dsn = (
        f"postgresql://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port or 5432}/{admin_db}"
    )
    return admin_dsn, db_name


async def _ensure_test_database() -> None:
    admin_dsn, db_name = _build_admin_dsn(TEST_DB_URL)
    conn = await asyncpg.connect(admin_dsn)
    try:
        exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname=$1", db_name)
        if not exists:
            await conn.execute(f'CREATE DATABASE "{db_name}"')
    finally:
        await conn.close()


@pytest.fixture(scope="session")
async def db_engine():
    from sqlalchemy.pool import NullPool

    await _ensure_test_database()
    main_engine = create_async_engine(MAIN_DB_URL, poolclass=NullPool)
    async with main_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await main_engine.dispose()

    engine = create_async_engine(TEST_DB_URL, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
async def seed_user(db_session):
    user = User(email="seed@example.com", full_name="Seed User", hashed_password=get_password_hash("SeedPass123"))
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def seed_customer(db_session):
    external_id = f"EXT-{uuid.uuid4().hex[:8]}"
    customer = Customer(external_id=external_id, name="Seed Customer", email="seed@customer.com")
    db_session.add(customer)
    await db_session.commit()
    await db_session.refresh(customer)
    return customer
