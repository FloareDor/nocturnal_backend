from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    DECIMAL,
    UUID,
    DateTime,
    Enum,
    ForeignKey,
    Identity,
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class BarReport(Base):
    __tablename__ = "bar_reports"

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(start=1, increment=1, always=True),
        primary_key=True,
        unique=True,
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    bar_id: Mapped[int] = mapped_column(ForeignKey("bars.id", ondelete="CASCADE"))
    line_length: Mapped[Optional[int]] = mapped_column(Integer)
    line_length_category: Mapped[str] = mapped_column(
        Enum("small", "medium", "long", name="line_length_categories"), nullable=False
    )
    wait_time: Mapped[Optional[int]] = mapped_column(Integer)
    cover_category: Mapped[Optional[str]] = mapped_column(
        Enum("free", "cheap", "moderate", "expensive", name="cover_categories")
    )
    cover_price: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc)
    )

    user: Mapped["Users"] = relationship(back_populates="bar_reports")  # noqa: F821
    bar: Mapped["Bars"] = relationship(back_populates="bar_reports")  # noqa: F821


BarReport_Table = BarReport.__table__
