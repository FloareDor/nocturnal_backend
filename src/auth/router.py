from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncConnection
from supabase._async.client import AsyncClient as Client

from src.auth import service
from src.auth.dependencies import (
    user_exists,
    valid_user_create,
)
from src.auth.jwt import parse_jwt_user_data, parse_jwt_user_id, validateToken
from src.auth.schemas import (
    AccessTokenResponse,
    AuthorizeCreds,
    JWTData,
    SocialLogin,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)
from src.database import get_db_connection, get_supaadmin, get_supabase

router = APIRouter()


@router.post(
    "/signup", status_code=status.HTTP_201_CREATED, response_model=UserResponse
)
async def register_user(
    request: Request,
    auth_data: UserCreate = Depends(valid_user_create),
    db_connection: AsyncConnection = Depends(get_db_connection),
    supabase: Client = Depends(get_supabase),
) -> dict[str, str]:
    user = await service.create_user(
        auth_data, db_connection=db_connection, supabase=supabase
    )
    return UserResponse(**user)


@router.post(
    "/social-login", status_code=status.HTTP_201_CREATED, response_model=UserResponse
)
async def social_login(
    request: Request,
    auth_data: SocialLogin,
    db_connection: AsyncConnection = Depends(get_db_connection),
    supabase: Client = Depends(get_supabase),
) -> Any:
    user = await service.social_login(
        auth_data, db_connection=db_connection, supabase=supabase
    )
    return user


@router.get("/profile", response_model=UserResponse)
async def get_my_account(request: Request, user: Any = Depends(user_exists)) -> Any:
    return UserResponse(**user)


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    request: Request,
    user_update: UserUpdate,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
) -> UserResponse:
    updated_user = await service.update_user(jwt_data["sub"], user_update)
    return UserResponse(**updated_user)


@router.post("/login", response_model=AccessTokenResponse)
async def user_login(
    request: Request,
    auth_data: UserLogin,
    response: Response,
    supabase: Client = Depends(get_supabase),
) -> AccessTokenResponse:
    response = await service.authenticate_user(auth_data, supabase=supabase)
    return AccessTokenResponse(
        access_token=response.session.access_token,
        refresh_token=response.session.refresh_token,
    )


@router.post("/authorize", response_model=AccessTokenResponse, include_in_schema=False)
async def authorize_swagger(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    supabase: Client = Depends(get_supabase),
) -> AccessTokenResponse:
    # Convert OAuth2PasswordRequestForm to AuthUser
    auth_data = AuthorizeCreds(
        email=form_data.username,
        password=form_data.password,
    )

    response = await service.authenticate_user(auth_data, supabase=supabase)
    return AccessTokenResponse(
        access_token=response.session.access_token,
        refresh_token=response.session.refresh_token,
    )


@router.post("/refresh-token", response_model=AccessTokenResponse)
async def refresh_tokens(
    request: Request,
    refresh_token: str,
    supabase: Client = Depends(get_supabase),
) -> AccessTokenResponse:
    print(refresh_token)
    response = await service.refresh_session(
        refresh_token=refresh_token, supabase=supabase
    )
    print("refresh token response", response)
    return AccessTokenResponse(
        access_token=response.session.access_token,
        refresh_token=response.session.refresh_token,
    )


@router.delete("/logout")
async def logout_user(
    request: Request,
    refresh_token: str,
    access_token: Any = Depends(validateToken),
    supabase: Client = Depends(get_supabase),
) -> None:
    print("access token:", access_token)
    response = await service.logout(
        access_token=access_token, refresh_token=refresh_token, supabase=supabase
    )
    return response


@router.delete("/delete-account", response_model=UserResponse)
async def delete_account(
    request: Request,
    supaadmin: Client = Depends(get_supaadmin),
    user_id: UUID = Depends(parse_jwt_user_id),
) -> Any:
    response = await service.delete_user(user_id=user_id, supabase=supaadmin)
    return response
