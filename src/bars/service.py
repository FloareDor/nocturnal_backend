# bars/service.py

from typing import Any, Optional
from uuid import UUID

from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncConnection

from src.auth.models import Users_Table
from src.bars.models import Bars_Table
from src.bars.schemas import BarCreate, BarUpdate
from src.database import execute, fetch_one


async def create_bar(
    bar_data: BarCreate, user_id: UUID, db: Optional[AsyncConnection] = None
) -> dict[str, Any]:
    insert_query = (
        insert(Bars_Table)
        .values(**bar_data.model_dump(), admin_id=user_id)
        .returning(Bars_Table)
    )
    return await fetch_one(insert_query, connection=db, commit_after=True)


async def get_bar_by_id(
    bar_id: int, db: Optional[AsyncConnection] = None
) -> Optional[dict[str, Any]]:
    select_query = select(Bars_Table).where(Bars_Table.c.id == bar_id)
    return await fetch_one(select_query, connection=db)


async def get_bar_by_user_id(
    user_id: UUID, db: Optional[AsyncConnection] = None
) -> Optional[dict[str, Any]]:
    select_query = select(Bars_Table).where(Bars_Table.c.admin_id == user_id)
    return await fetch_one(select_query, connection=db)


async def get_bars(db: AsyncConnection):
    query = select(Bars_Table).order_by(Bars_Table.c.created_at.desc())
    return await paginate(conn=db, query=query)


async def update_bar(
    bar_id: int, bar_data: BarUpdate, db: Optional[AsyncConnection] = None
) -> Optional[dict[str, Any]]:
    update_query = (
        update(Bars_Table)
        .where(Bars_Table.c.id == bar_id)
        .values(**bar_data.model_dump(exclude_unset=True))
        .returning(Bars_Table)
    )
    return await fetch_one(update_query, connection=db, commit_after=True)


async def delete_bar(bar_id: int, db: Optional[AsyncConnection] = None) -> None:
    delete_query = delete(Bars_Table).where(Bars_Table.c.id == bar_id)
    await execute(delete_query, connection=db, commit_after=True)


async def get_bar_admin(
    bar_id: int, db: Optional[AsyncConnection] = None
) -> Optional[dict[str, Any]]:
    select_query = (
        select(Users_Table)
        .join(Bars_Table, Users_Table.c.id == Bars_Table.c.admin_id)
        .where(Bars_Table.c.id == bar_id)
    )
    return await fetch_one(select_query, connection=db)


async def is_user_bar_admin(
    user_id: UUID, bar_id: int, db: Optional[AsyncConnection] = None
) -> bool:
    select_query = (
        select(Bars_Table)
        .where(Bars_Table.c.id == bar_id)
        .where(Bars_Table.c.admin_id == user_id)
    )
    result = await fetch_one(select_query, connection=db)
    return result is not None
