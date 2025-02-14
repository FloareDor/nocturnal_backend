import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import insert, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncConnection
from supabase._async.client import AsyncClient

from src.auth.models import Users_Table as Users
from src.auth.schemas import SocialLogin, UserCreate, UserLogin, UserRole, UserUpdate
from src.auth.security import hash_password
from src.bars.service import create_bar
from src.database import fetch_one
from src.exceptions import DetailedError


async def create_user(
    user: UserCreate,
    db_connection: Optional[AsyncConnection] = None,
    supabase: Optional[AsyncClient] = None,
) -> dict[str, Any] | None:
    username = user.username or ""
    try:
        # Step 1: Create user in Supabase
        response = await supabase.auth.sign_up(
            {
                "email": user.email,
                "password": user.password,
                "options": {
                    "data": {
                        "username": username,
                        "role": user.role,
                    }
                },
            }
        )
    except Exception as e:
        raise DetailedError(e)

    if not response.user:
        raise HTTPException(status_code=400, detail="User creation failed in Supabase")

    user_id = uuid.UUID(response.user.id)

    user_data = {
        "id": user_id,
        "username": username,
        "email": user.email,
        "password": hash_password(user.password),
        "role": user.role,
        "created_at": datetime.now(timezone.utc),
    }

    try:
        # Step 2: Create user in your database
        insert_query = insert(Users).values(**user_data).returning(Users)
        db_user = await fetch_one(insert_query, connection=db_connection)

        if not db_user:
            # If user creation in the DB fails, we'd want to delete the Supabase user
            await supabase.auth.admin.delete_user(response.user.id)
            raise HTTPException(
                status_code=500, detail="Failed to create user in database"
            )

        # Step 3: If user is a bar admin, we create the associated bar
        if user.role == UserRole.BAR_ADMIN and user.bar_details:
            bar_result = await create_bar(
                bar_data=user.bar_details, user_id=user_id, db=db_connection
            )
            if not bar_result:
                # If bar creation fails, we might want to delete both the DB user and Supabase user  # noqa: E501
                await supabase.auth.admin.delete_user(response.user.id)
                raise HTTPException(status_code=500, detail="Failed to create bar")

        return {
            **db_user,
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
        }
    except SQLAlchemyError as e:
        # If any database operation fails, delete the Supabase user
        await supabase.auth.admin.delete_user(response.user.id)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


async def get_user_by_id(
    user_id: UUID, db: Optional[AsyncConnection] = None
) -> dict[str, Any] | None:
    select_query = select(Users).where(Users.c.id == user_id)

    return await fetch_one(select_query, connection=db)


async def get_user_by_email(
    email: str, db_connection: Optional[AsyncConnection] = None
) -> dict[str, Any] | None:
    select_query = select(Users).where(Users.c.email == email)

    return await fetch_one(select_query, connection=db_connection)


async def get_user_by_username(
    username: str, db_connection: Optional[AsyncConnection] = None
) -> dict[str, Any] | None:
    select_query = select(Users).where(Users.c.username == username)

    return await fetch_one(select_query, connection=db_connection)


async def authenticate_user(
    auth_data: UserLogin,
    supabase: AsyncClient,
) -> dict[str, Any]:
    try:
        response = await supabase.auth.sign_in_with_password(
            {"email": auth_data.email, "password": auth_data.password}
        )
        return response
    except Exception as e:
        print("login exception:", e)
        raise DetailedError(e)


async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    db_connection: Optional[AsyncConnection] = None,
) -> dict[str, Any]:
    update_data = user_update.model_dump(exclude_unset=True)

    if not update_data:
        return await get_user_by_id(user_id)

    update_query = (
        update(Users).where(Users.c.id == user_id).values(update_data).returning(Users)
    )

    return await fetch_one(update_query, commit_after=True)


async def refresh_session(refresh_token: str, supabase: AsyncClient):
    try:
        print("refresh token:", refresh_token)
        response = await supabase.auth.refresh_session(refresh_token)
        return response
    except Exception as e:
        print("Refresh token exception:", e)
        raise DetailedError(e)


async def logout(access_token: str, refresh_token: str, supabase: AsyncClient):
    try:
        _ = await supabase.auth.set_session(access_token, refresh_token)
        response2 = await supabase.auth.sign_out({"scope": "global"})
        return response2
    except Exception as e:
        print("Logout Exception:", e)
        raise DetailedError(e)


async def social_login(
    auth_data: SocialLogin,
    supabase: AsyncClient,
    db_connection: Optional[AsyncConnection] = None,
) -> dict[str, Any]:
    response = {}
    try:
        # Verify the Social ID token with Supabase
        response = await supabase.auth.sign_in_with_id(
            {
                "provider": auth_data.provider,
                "token": auth_data.token,
            }
        )

        if not response.user:
            raise HTTPException(
                status_code=400, detail=f"{auth_data.provider} login failed"
            )

        user_id = uuid.UUID(response.user.id)
        email = response.user.email

        existing_user = await get_user_by_id(user_id, db=db_connection)

        if existing_user:
            # Update existing user if needed
            # update the last login time for now
            update_query = (
                update(Users)
                .where(Users.c.id == user_id)
                .values(updated_at=datetime.now(timezone.utc))
                .returning(Users)
            )
            db_user = await fetch_one(
                update_query, connection=db_connection, commit_after=True
            )
        else:
            # Create a new user in your database
            insert_query = (
                insert(Users)
                .values(
                    id=user_id,
                    email=email,
                    created_at=datetime.now(timezone.utc),
                )
                .returning(Users)
            )
            db_user = await fetch_one(
                insert_query, connection=db_connection, commit_after=True
            )

        if not db_user:
            await supabase.auth.admin.delete_user(response.user.id)
            raise HTTPException(
                status_code=500,
                detail=f"""
                    {auth_data.provider} login:
                    Failed to create or update user in database
                """,
            )

        return {
            **db_user,
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
        }

    except Exception as e:
        await supabase.auth.admin.delete_user(response.user.id)
        print(f"{auth_data.provider} login exception:", e)
        raise DetailedError(e)


async def delete_user(
    user_id: UUID,
    supabase: AsyncClient,
    db_connection: Optional[AsyncConnection] = None,
) -> dict[str, Any] | None:
    try:
        # Delete user from Supabase
        _ = await supabase.auth.admin.delete_user(user_id)
    except Exception as e:
        print("Delete user exception:", e)
        raise DetailedError(e)

    try:
        # Delete user from the database
        delete_query = Users.delete().where(Users.c.id == user_id).returning(Users)

        deleted_user = await fetch_one(
            delete_query, connection=db_connection, commit_after=True
        )

        if not deleted_user:
            raise HTTPException(
                status_code=404, detail="User not found in the database"
            )

        return deleted_user
    except Exception as e:
        print("delete user exception:", e)
        raise HTTPException(status_code=404, detail=f"database error: {e}")
