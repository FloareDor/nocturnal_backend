from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import Depends

from src.auth import service
from src.auth.exceptions import EmailTaken, UsernameTaken, UserNotFound
from src.auth.jwt import parse_jwt_user_id
from src.auth.schemas import UserCreate


async def valid_user_create(user: UserCreate) -> UserCreate:
    if await service.get_user_by_email(user.email):
        raise EmailTaken()
    if user.username is not None:
        if await service.get_user_by_username(user.username):
            raise UsernameTaken()

    return user


async def user_exists(user_id: UUID = Depends(parse_jwt_user_id)) -> Any:
    user = await service.get_user_by_id(user_id)
    if user is None:
        raise UserNotFound()
    return user


def _is_valid_refresh_token(db_refresh_token: dict[str, Any]) -> bool:
    return datetime.now(timezone.utc) <= db_refresh_token["expires_at"]
