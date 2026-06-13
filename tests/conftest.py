import os
from urllib.parse import urlparse
import pytest
import asyncpg
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from dotenv import load_dotenv

load_dotenv('.env_dbf2ee37-0d53-416c-8916-7748075b87f8', override=True)

from app.main import app
from app.database import Base, get_db
from app.models import *

MAIN_DB_URL = os.getenv("DATABASE_URL", "")
_parts = MAIN_DB_URL.rsplit("/", 1)
TEST_DB_URL = (_parts[0] + "/" + _parts[1] + "_test") if len(_parts) == 2 else MAIN_DB_URL
TEST_DB_NAME = (_parts[1] + "_test") if len(_parts) == 2 else ""


def _asyncpg_url(url: str) -> str:
    return url.replace("postgresql+asyncpg", "postgresql")


async def ensure_database_exists(db_url: str, db_name: str):
    if not db_url or not db_name:
        return
    parsed = urlparse(_asyncpg_url(db_url))
    host = parsed.hostname or "localhost"
    port = parsed.port or 5432
    user = parsed.username or "postgres"
    password = parsed.password or ""
    admin_url = f"postgresql://{user}:{password}@{host}:{port}/postgres"
    conn = await asyncpg.connect(admin_url)
    exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname=$1", db_name)
    if not exists:
        await conn.execute(f'CREATE DATABASE "{db_name}"')
    await conn.close()


@pytest.fixture(scope="session")
async def db_engine():
    from sqlalchemy.pool import NullPool

    await ensure_database_exists(MAIN_DB_URL, TEST_DB_NAME)

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
        try:
            yield session
        finally:
            try:
                await session.rollback()
            except RuntimeError:
                pass


@pytest.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
