# posts/service.py

from typing import Any, Optional
from uuid import UUID

from fastapi import HTTPException
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import delete, insert, null, select, update
from sqlalchemy.ext.asyncio import AsyncConnection

from src.bars.models import Bars_Table
from src.database import execute, fetch_one
from src.posts.models import Likes_Table, Posts_Table, RSVP_Table
from src.posts.schemas import PostCreate, PostUpdate


async def create_post(
    post_data: PostCreate, user_id: UUID, db: Optional[AsyncConnection] = None
) -> dict[str, Any]:
    # check if the bar exists
    bar_query = select(Bars_Table).where(Bars_Table.c.id == post_data.bar_id)
    bar = await fetch_one(bar_query)
    if not bar:
        raise HTTPException(status_code=404, detail="Bar not found")

    # If bar exists, proceed with post creation
    insert_query = (
        insert(Posts_Table)
        .values(**post_data.model_dump(), user_id=user_id)
        .returning(Posts_Table)
    )
    return await fetch_one(insert_query, commit_after=True, connection=db)


async def get_post_by_id(
    post_id: int, db: Optional[AsyncConnection] = None
) -> Optional[dict[str, Any]]:
    select_query = select(Posts_Table).where(Posts_Table.c.id == post_id)
    return await fetch_one(select_query)


async def get_posts(db_connection: AsyncConnection):
    query = (
        select(Posts_Table)
        .where(Posts_Table.c.deleted_at == null())
        .order_by(Posts_Table.c.created_at.desc())
    )
    return await paginate(conn=db_connection, query=query)


async def update_post(
    post_id: int, new_post_data: PostUpdate, db: Optional[AsyncConnection] = None
) -> Optional[dict[str, Any]]:
    update_query = (
        update(Posts_Table)
        .where(Posts_Table.c.id == post_id)
        .values(**new_post_data.model_dump(exclude_unset=True))
        .returning(Posts_Table)
    )
    return await fetch_one(update_query, commit_after=True, connection=db)


async def delete_post(post_id: int, db: Optional[AsyncConnection] = None) -> None:
    delete_query = delete(Posts_Table).where(Posts_Table.c.id == post_id)
    await execute(delete_query, commit_after=True, connection=db)


async def like_post(
    user_id: UUID, post_id: int, db: Optional[AsyncConnection] = None
) -> dict[str, Any]:
    insert_query = (
        insert(Likes_Table)
        .values(user_id=user_id, post_id=post_id)
        .returning(Likes_Table)
    )
    return await fetch_one(insert_query, commit_after=True, connection=db)


async def unlike_post(
    user_id: UUID, post_id: int, db: Optional[AsyncConnection] = None
) -> None:
    delete_query = delete(Likes_Table).where(
        (Likes_Table.c.user_id == user_id) & (Likes_Table.c.post_id == post_id)
    )
    await execute(delete_query, commit_after=True, connection=db)


async def rsvp_to_event(
    user_id: UUID, post_id: int, db: Optional[AsyncConnection] = None
) -> dict[str, Any]:
    insert_query = (
        insert(RSVP_Table)
        .values(user_id=user_id, post_id=post_id)
        .returning(RSVP_Table)
    )
    return await fetch_one(insert_query, commit_after=True, connection=db)


async def cancel_rsvp(
    user_id: UUID, post_id: int, db: Optional[AsyncConnection] = None
) -> None:
    delete_query = delete(RSVP_Table).where(
        (RSVP_Table.c.user_id == user_id) & (RSVP_Table.c.post_id == post_id)
    )
    await execute(delete_query, commit_after=True, connection=db)


async def is_user_post_owner(
    user_id: UUID, post_id: int, db: Optional[AsyncConnection] = None
) -> bool:
    select_query = (
        select(Posts_Table)
        .where(Posts_Table.c.id == post_id)
        .where(Posts_Table.c.user_id == user_id)
    )
    result = await fetch_one(select_query, connection=db)
    return result is not None
