from datetime import datetime, timedelta, timezone
from typing import Any, Tuple
from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import service
from src.auth.config import auth_config
from src.auth.exceptions import (
    AuthorizationFailed,
    AuthRequired,
    InvalidToken,
    UserNotFound,
)
from src.database import get_db_connection

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/authorize", auto_error=False)


def create_access_token(
    *,
    user: dict[str, Any],
    expires_delta: timedelta = timedelta(minutes=auth_config.JWT_EXP),
) -> str:
    jwt_data = {
        "sub": str(user["id"]),
        "exp": datetime.now(timezone.utc) + expires_delta,
        "is_admin": user["is_admin"],
    }

    return jwt.encode(jwt_data, auth_config.JWT_SECRET, algorithm=auth_config.JWT_ALG)


async def readToken(
    token: str = Depends(oauth2_scheme),
) -> Any | None:
    if not token:
        return None

    return token


async def parse_data(token: str) -> Any | None:
    if not token:
        return None
    try:
        payload = jwt.decode(
            token,
            auth_config.JWT_SECRET,
            algorithms=[auth_config.JWT_ALG],
            audience="authenticated",
        )
    except JWTError:
        raise InvalidToken()

    return payload


async def parse_jwt_user_data_optional(
    token: str = Depends(oauth2_scheme),
) -> Any | None:
    if not token:
        return None

    try:
        payload = jwt.decode(
            token,
            auth_config.JWT_SECRET,
            algorithms=[auth_config.JWT_ALG],
            audience="authenticated",
        )
    except JWTError:
        raise InvalidToken()

    return payload


async def validateToken(
    token: str = Depends(oauth2_scheme),
) -> Any | None:
    if not token:
        return None

    try:
        _ = jwt.decode(
            token,
            auth_config.JWT_SECRET,
            algorithms=[auth_config.JWT_ALG],
            audience="authenticated",
        )
    except JWTError:
        raise InvalidToken()

    return token


async def parse_jwt_user_id(
    token: str = Depends(oauth2_scheme),
) -> Any | None:
    if not token:
        raise AuthRequired()
    try:
        payload = jwt.decode(
            token,
            auth_config.JWT_SECRET,
            algorithms=[auth_config.JWT_ALG],
            audience="authenticated",
        )
    except JWTError:
        raise InvalidToken()
    print("paylod", payload)

    return UUID(payload["sub"])


# jwt to payload (what's inside jwt ~ no)
async def parse_jwt_user_data(
    payload: Any | None = Depends(parse_jwt_user_data_optional),
) -> Any:
    if not payload:
        raise AuthRequired()
    return payload


# jwt to current db user info
async def get_current_user(
    user_id: UUID = Depends(parse_jwt_user_id),
    db: AsyncSession = Depends(get_db_connection),
) -> Tuple[dict, AsyncSession]:
    user = await service.get_user_by_id(user_id=user_id, db=db)
    if user is None:
        raise UserNotFound()
    return user, db


async def validate_superuser_access(
    user_and_db: Tuple[dict, AsyncSession] = Depends(get_current_user),
) -> Tuple[dict, AsyncSession]:
    user, _ = user_and_db
    if user["role"] != "superuser":
        raise AuthorizationFailed()
    return user_and_db


async def validate_bar_admin_access(
    user_and_db=Depends(get_current_user),
) -> Tuple[dict, AsyncSession]:
    user, _ = user_and_db
    if user["role"] != "bar_admin" and user["role"] != "superuser":
        raise AuthorizationFailed()
    return user_and_db
