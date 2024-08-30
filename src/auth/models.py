from typing import List

from sqlalchemy import (
    DateTime,
    Enum,
    LargeBinary,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Users(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True)
    username: Mapped[str] = mapped_column(
        String, server_default="", nullable=False, unique=True
    )
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    full_name: Mapped[str] = mapped_column(String, server_default="", nullable=False)
    profile_picture_url: Mapped[str] = mapped_column(
        String,
        server_default="https://example.com/default-profile-picture.jpg",
        nullable=False,
    )
    role: Mapped[str] = mapped_column(
        Enum("user", "bar_admin", "superuser", name="user_roles")
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
    administered_bars: Mapped[List["Bars"]] = relationship(back_populates="admin")  # noqa: F821
    posts: Mapped[List["Posts"]] = relationship(back_populates="user")  # noqa: F821
    likes: Mapped[List["Likes"]] = relationship(back_populates="user")  # noqa: F821
    rsvps: Mapped[List["RSVP"]] = relationship(back_populates="user")  # noqa: F821
    bar_reports: Mapped[List["BarReport"]] = relationship(back_populates="user")  # noqa: F821


Users_Table = Users.__table__
