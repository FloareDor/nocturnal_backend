import uuid
from os import environ as env
from typing import Any, AsyncGenerator

from dotenv import find_dotenv, load_dotenv
from sqlalchemy import (
    CursorResult,
    Insert,
    MetaData,
    Select,
    Update,
)
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from supabase._async.client import AsyncClient as Client
from supabase._async.client import create_client

from src.config import settings
from src.constants import DB_NAMING_CONVENTION

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

url: str = env.get("SUPABASE_URL")
key: str = env.get("SUPABASE_KEY")
# supabase: Client = create_client(url, key)

DATABASE_URL = str(settings.DATABASE_ASYNC_URL)

print("async", DATABASE_URL)

engine = create_async_engine(
    DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    pool_recycle=settings.DATABASE_POOL_TTL,
    pool_pre_ping=settings.DATABASE_POOL_PRE_PING,
    connect_args={
        "prepared_statement_name_func": lambda: f"__asyncpg_{uuid.uuid4()}__",
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
    },
)
metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)


class Base(DeclarativeBase):
    pass


async def fetch_one(
    select_query: Select | Insert | Update,
    connection: AsyncConnection | None = None,
    commit_after: bool = False,
) -> dict[str, Any] | None:
    if not connection:
        async with engine.connect() as connection:
            cursor = await _execute_query(select_query, connection, commit_after)
            return cursor.first()._asdict() if cursor.rowcount > 0 else None

    cursor = await _execute_query(select_query, connection, commit_after)
    return cursor.first()._asdict() if cursor.rowcount > 0 else None


async def fetch_all(
    select_query: Select | Insert | Update,
    connection: AsyncConnection | None = None,
    commit_after: bool = False,
) -> list[dict[str, Any]]:
    if not connection:
        async with engine.connect() as connection:
            cursor = await _execute_query(select_query, connection, commit_after)
            return [r._asdict() for r in cursor.all()]

    cursor = await _execute_query(select_query, connection, commit_after)
    return [r._asdict() for r in cursor.all()]


async def execute(
    query: Insert | Update,
    connection: AsyncConnection | None,
    commit_after: bool = False,
) -> None:
    if connection is None:
        async with engine.connect() as connection:
            await _execute_query(query, connection, commit_after)
            return

    await _execute_query(query, connection, commit_after)


async def _execute_query(
    query: Select | Insert | Update,
    connection: AsyncConnection,
    commit_after: bool = False,
) -> CursorResult:
    result = await connection.execute(query)
    if commit_after:
        await connection.commit()

    return result


async def get_db_connection() -> AsyncGenerator[AsyncConnection, None]:
    connection = await engine.connect()
    try:
        yield connection
    finally:
        await connection.close()


async def get_supabase() -> Client:
    return await create_client(url, key)


async def get_supaadmin() -> Client:
    return await create_client(url, env.get("SUPABASE_SERVICE_ROLE_KEY"))


async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
