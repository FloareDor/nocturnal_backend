from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


class PostType(str, Enum):
    REGULAR = "regular"
    EVENT = "event"


class CoverCategory(str, Enum):
    FREE = "free"
    CHEAP = "cheap"
    MODERATE = "moderate"
    EXPENSIVE = "expensive"


class PostBase(BaseModel):
    bar_id: int = Field(..., gt=0, example=1)
    content: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        example="Join us for an exciting night of live music!",
    )
    photo_url: Optional[str] = Field(
        None, example="https://example.com/event-photo.jpg"
    )
    post_type: PostType = Field(..., example=PostType.EVENT)
    title: Optional[str] = Field(
        None, min_length=1, max_length=100, example="Live Music Night"
    )
    event_datetime: Optional[datetime] = Field(None, example="2024-09-15T20:00:00Z")
    cover_category: Optional[CoverCategory] = Field(
        None, example=CoverCategory.MODERATE
    )
    cover_price: Optional[float] = Field(None, ge=0, le=1000, example=15.50)


class PostCreate(PostBase):
    photo_url: str = Field(..., example="https://example.com/event-photo.jpg")

    @field_validator("event_datetime")
    def ensure_timezone_aware(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

    @model_validator(mode="after")
    def validate_event_fields(self) -> "PostCreate":
        if self.post_type == PostType.EVENT:
            if self.event_datetime is None:
                raise ValueError("Event datetime is required for event posts")
            if self.event_datetime < datetime.now(timezone.utc):
                raise ValueError("Event datetime must be in the future")
            if self.title is None:
                raise ValueError("Title is required for event posts")
            if self.cover_category is None:
                raise ValueError("Cover category is required for event posts")
            if self.cover_price is None:
                raise ValueError("Cover price is required for event posts")
        return self

    model_config = {
        "json_schema_extra": {
            "example": {
                "bar_id": 1,
                "content": "Join us for an exciting night of live music!",
                "photo_url": "https://example.com/event-photo.jpg",
                "post_type": "event",
                "title": "Live Music Night",
                "event_datetime": "2024-09-15T20:00:00Z",
                "cover_category": "moderate",
                "cover_price": 15.50,
            }
        }
    }


class PostUpdate(BaseModel):
    content: Optional[str] = Field(
        None,
        example="Updated: Join us for an unforgettable night of live music and great drinks!",  # noqa: E501
    )
    photo_url: Optional[str] = Field(
        None, example="https://example.com/updated-event-photo.jpg"
    )
    title: Optional[str] = Field(None, example="Updated: Live Music Extravaganza")
    event_datetime: Optional[datetime] = Field(None, example="2024-09-16T21:00:00Z")
    cover_category: Optional[CoverCategory] = Field(None, example=CoverCategory.CHEAP)
    cover_price: Optional[float] = Field(None, example=10.00)

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Updated: Join us for an unforgettable night of live music and great drinks!",  # noqa: E501
                "title": "Updated: Live Music Extravaganza",
                "cover_category": "cheap",
                "cover_price": 10.00,
            }
        }


class PostResponse(PostBase):
    id: int = Field(..., example=1)
    user_id: UUID = Field(..., example="123e4567-e89b-12d3-a456-426614174000")
    created_at: datetime = Field(..., example="2023-08-30T14:30:00Z")
    updated_at: datetime = Field(..., example="2023-08-30T14:30:00Z")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "bar_id": 1,
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "content": "Join us for an exciting night of live music!",
                "photo_url": "https://example.com/event-photo.jpg",
                "post_type": "event",
                "title": "Live Music Night",
                "event_datetime": "2024-09-15T20:00:00Z",
                "cover_category": "moderate",
                "cover_price": 15.50,
                "created_at": "2023-08-30T14:30:00Z",
                "updated_at": "2023-08-30T14:30:00Z",
            }
        }
