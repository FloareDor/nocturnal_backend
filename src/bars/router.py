from typing import Tuple
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, add_pagination
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt import parse_jwt_user_id
from src.bars import service as bars_service
from src.bars.dependencies import valid_create_bar, validate_and_get_bar_id
from src.bars.schemas import BarResponse, BarUpdate
from src.database import get_db_connection

router = APIRouter()


@router.post("/", response_model=BarResponse)
async def create_bar(
    bar_userid_db=Depends(valid_create_bar),
    db: AsyncSession = Depends(get_db_connection),
):
    bar_data, user_id, db = bar_userid_db
    return await bars_service.create_bar(bar_data, user_id, db=db)


@router.get("/", response_model=Page[BarResponse])
async def get_bars(
    db: AsyncSession = Depends(get_db_connection), _: UUID = Depends(parse_jwt_user_id)
):
    return await bars_service.get_bars(db=db)


@router.get("/{bar_id}", response_model=BarResponse)
async def get_bar(bar_id: int, db: AsyncSession = Depends(get_db_connection)):
    bar = await bars_service.get_bar_by_id(bar_id, db=db)
    if bar is None:
        raise HTTPException(status_code=404, detail="Bar not found")
    return bar


@router.put("/", response_model=BarResponse)
async def update_bar(
    bar_update: BarUpdate,
    barID_and_db: Tuple[int, AsyncSession] = Depends(validate_and_get_bar_id),
):
    bar_id, db = barID_and_db
    updated_bar = await bars_service.update_bar(bar_id, bar_update, db=db)
    if updated_bar is None:
        raise HTTPException(status_code=404, detail="Bar not found")
    return updated_bar


@router.delete("/")
async def delete_bar(
    barID_and_db: Tuple[int, AsyncSession] = Depends(validate_and_get_bar_id),
):
    bar_id, db = barID_and_db
    try:
        await bars_service.delete_bar(bar_id, db=db)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Bar delete error: {e}")
    return {"message": "Bar deleted successfully"}


add_pagination(router)
