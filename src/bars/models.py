from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import (
    ARRAY,
    DECIMAL,
    UUID,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Identity,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.auth.models import Users
from src.bar_reports.models import BarReport
from src.database import Base


class Bars(Base):
    __tablename__ = "bars"

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(start=1, increment=1, always=True),
        primary_key=True,
        unique=True,
    )
    admin_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(100))
    address: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(20))
    image_url: Mapped[Optional[str]] = mapped_column(String(255))
    latitude: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 8))
    longitude: Mapped[Optional[float]] = mapped_column(DECIMAL(11, 8))
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    rating: Mapped[Optional[float]] = mapped_column(DECIMAL(3, 2))
    rating_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    # New fields for averaged line length and cover information
    line_length: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), default=10)
    line_length_category: Mapped[Optional[str]] = mapped_column(
        Enum("small", "medium", "long", name="line_length_categories"), default="medium"
    )
    line_length_distribution: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String), default=["medium"]
    )

    cover_category: Mapped[Optional[str]] = mapped_column(
        Enum("free", "cheap", "moderate", "expensive", name="cover_categories"),
        default="moderate",
    )
    cover_category_distribution: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String), default=["moderate"]
    )
    cover_price: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), default=10.00)

    admin: Mapped["Users"] = relationship(back_populates="administered_bars")
    posts: Mapped[List["Posts"]] = relationship(back_populates="bar")  # noqa: F821
    bar_reports: Mapped[List["BarReport"]] = relationship(back_populates="bar")


Bars_Table = Bars.__table__
