from datetime import datetime, timezone
from typing import Optional, Tuple

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt import validate_bar_admin_access
from src.posts import service as posts_service
from src.posts.exceptions import UnauthorizedPostAction
from src.posts.schemas import PostCreate, PostUpdate


def ensure_timezone_aware(dt: Optional[datetime]) -> Optional[datetime]:
    if dt and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


async def valid_post_create(post: PostCreate) -> PostCreate:
    # Ensure event_datetime is timezone-aware
    post.event_datetime = ensure_timezone_aware(post.event_datetime)
    # Add any additional validation logic here
    return post


async def valid_post_update(post: PostUpdate) -> PostUpdate:
    # Add any additional validation logic here
    return post


async def validate_post_access(
    post_id: int,
    user_and_db: Tuple[dict, AsyncSession] = Depends(validate_bar_admin_access),
) -> Tuple[int, dict, AsyncSession]:
    current_user, db = user_and_db
    post = await posts_service.get_post_by_id(post_id, db=db)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    if current_user["role"] == "bar_admin":
        if post["user_id"] != current_user["id"]:
            raise UnauthorizedPostAction()
    elif current_user["role"] != "superuser":
        raise UnauthorizedPostAction()

    return current_user, db
