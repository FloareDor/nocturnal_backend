import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from src.auth.config import auth_config
from src.auth.exceptions import AuthorizationFailed, AuthRequired, InvalidToken
from src.auth.schemas import JWTData

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

    return uuid.UUID(payload["sub"])


async def parse_jwt_user_data(
    payload: Any | None = Depends(parse_jwt_user_data_optional),
) -> Any:
    if not payload:
        raise AuthRequired()
    return payload


async def parse_jwt_admin_data(
    token: JWTData = Depends(parse_jwt_user_data),
) -> JWTData:
    if not token.is_admin:
        raise AuthorizationFailed()

    return token


async def validate_admin_access(
    token: JWTData | None = Depends(parse_jwt_user_data_optional),
) -> None:
    if token and token.is_admin:
        return

    raise AuthorizationFailed()
