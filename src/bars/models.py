from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import (
    DECIMAL,
    UUID,
    Boolean,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    String,
)

# CheckConstraint
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

    admin: Mapped["Users"] = relationship(back_populates="administered_bars")
    posts: Mapped[List["Posts"]] = relationship(back_populates="bar")  # noqa: F821
    bar_reports: Mapped[List["BarReport"]] = relationship(back_populates="bar")

    # __table_args__ = (
    #     CheckConstraint(
    #         "admin_id IN (SELECT id FROM users WHERE role IN ('superuser', 'bar_admin'))", # noqa: E501
    #         name="check_admin_role",
    #     ),
    # )


Bars_Table = Bars.__table__
