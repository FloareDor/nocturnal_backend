from typing import Optional, Tuple
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt import (
    validate_bar_admin_access,
)
from src.bars import service
from src.bars.schemas import BarCreate


async def valid_create_bar(
    bar: BarCreate,
    user_and_db: Tuple[dict, AsyncSession] = Depends(validate_bar_admin_access),
) -> Tuple[BarCreate, UUID, AsyncSession]:
    current_user, db = user_and_db
    user_bar = await service.get_bar_by_user_id(current_user["id"])
    if user_bar is not None and current_user["role"] != "superuser":
        raise HTTPException(
            status_code=403, detail="Account is linked to a Bar already"
        )
    return bar, current_user["id"], db


async def validate_and_get_bar_id(
    user_and_db: Tuple[dict, AsyncSession] = Depends(validate_bar_admin_access),
    bar_id: Optional[int] = None,
) -> Tuple[int, AsyncSession]:
    current_user, db = user_and_db
    if current_user["role"] == "bar_admin":
        user_bar = await service.get_bar_by_user_id(current_user["id"], db=db)
        if user_bar is None:
            raise HTTPException(status_code=404, detail="Bar not found for this admin")
        return user_bar["id"], db
    elif current_user["role"] == "superuser":
        if bar_id is None:
            raise HTTPException(
                status_code=400, detail="bar_id is required for superusers"
            )
        return bar_id, db
    else:
        raise HTTPException(status_code=403, detail="Unauthorized")
