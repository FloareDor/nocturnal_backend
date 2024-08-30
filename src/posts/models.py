from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import (
    DECIMAL,
    UUID,
    DateTime,
    Enum,
    ForeignKey,
    Identity,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.auth.models import Users
from src.bars.models import Bars
from src.database import Base


class Posts(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(start=1, increment=1, always=True),
        primary_key=True,
        unique=True,
    )
    bar_id: Mapped[int] = mapped_column(ForeignKey("bars.id", ondelete="CASCADE"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    content: Mapped[str] = mapped_column(Text)
    photo_url: Mapped[Optional[str]] = mapped_column(String(255))
    post_type: Mapped[str] = mapped_column(Enum("regular", "event", name="post_types"))
    title: Mapped[Optional[str]] = mapped_column(String(100))
    event_datetime: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    cover_category: Mapped[Optional[str]] = mapped_column(String(50))
    cover_price: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    bar: Mapped["Bars"] = relationship(back_populates="posts")
    user: Mapped["Users"] = relationship(back_populates="posts")
    likes: Mapped[List["Likes"]] = relationship(back_populates="post")
    rsvps: Mapped[List["RSVP"]] = relationship(back_populates="post")


class Likes(Base):
    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc)
    )

    user: Mapped["Users"] = relationship(back_populates="likes")
    post: Mapped["Posts"] = relationship(back_populates="likes")


class RSVP(Base):
    __tablename__ = "rsvps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc)
    )

    user: Mapped["Users"] = relationship(back_populates="rsvps")
    post: Mapped["Posts"] = relationship(back_populates="rsvps")


Posts_Table = Posts.__table__
Likes_Table = Likes.__table__
RSVP_Table = RSVP.__table__
