from typing import Tuple

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, add_pagination
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt import parse_jwt_user_id, validate_bar_admin_access
from src.database import get_db_connection
from src.posts import service as posts_service
from src.posts.dependencies import valid_post_create, validate_post_access
from src.posts.schemas import PostCreate, PostResponse, PostUpdate

router = APIRouter()


@router.post("", response_model=PostResponse)
async def create_post(
    post: PostCreate = Depends(valid_post_create),
    user_and_db: Tuple[dict, AsyncSession] = Depends(validate_bar_admin_access),
):
    current_user, db = user_and_db
    return await posts_service.create_post(post, user_id=current_user["id"], db=db)


@router.get("", response_model=Page[PostResponse])
async def get_posts(db: AsyncSession = Depends(get_db_connection)):
    return await posts_service.get_posts(db_connection=db)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db_connection)):
    post = await posts_service.get_post_by_id(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_update: PostUpdate,
    user_and_db: Tuple[dict, AsyncSession] = Depends(validate_post_access),
):
    current_user, db = user_and_db
    updated_post = await posts_service.update_post(post_id, post_update, db=db)
    if updated_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return updated_post


@router.delete("/{post_id}")
async def delete_post(
    post_id: int, user_and_db: Tuple[dict, AsyncSession] = Depends(validate_post_access)
):
    current_user, db = user_and_db
    try:
        _ = await posts_service.delete_post(post_id, db=db)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Post deletion error: {e}")
    return {"message": "Post deleted successfully"}


@router.post("/{post_id}/like")
async def like_post(
    post_id: int,
    user_id=Depends(parse_jwt_user_id),
    db: AsyncSession = Depends(get_db_connection),
):
    liked = await posts_service.like_post(user_id=user_id, post_id=post_id)
    if not liked:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post liked successfully"}


@router.post("/{post_id}/unlike")
async def unlike_post(
    post_id: int,
    user_id=Depends(parse_jwt_user_id),
    db: AsyncSession = Depends(get_db_connection),
):
    await posts_service.unlike_post(user_id=user_id, post_id=post_id)
    return {"message": "Post unliked successfully"}


@router.post("/{post_id}/rsvp")
async def rsvp_to_event(
    post_id: int,
    user_id: dict = Depends(parse_jwt_user_id),
    db: AsyncSession = Depends(get_db_connection),
):
    rsvped = await posts_service.rsvp_to_event(user_id=user_id, post_id=post_id)
    if not rsvped:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "RSVP successful"}


@router.post("/{post_id}/unrsvp")
async def unrsvp_to_event(
    post_id: int,
    user_id=Depends(parse_jwt_user_id),
    db: AsyncSession = Depends(get_db_connection),
):
    await posts_service.cancel_rsvp(user_id=user_id, post_id=post_id)
    return {"message": "un RSVPed successfully"}


add_pagination(router)
