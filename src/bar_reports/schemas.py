from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class LineLengthCategory(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LONG = "long"


class CoverCategory(str, Enum):
    FREE = "free"
    CHEAP = "cheap"
    MODERATE = "moderate"
    EXPENSIVE = "expensive"


class ReportType(str, Enum):
    LINE = "line"
    COVER = "cover"
    BOTH = "both"


class BarReportCreate(BaseModel):
    bar_id: int
    line_length_category: LineLengthCategory
    line_length: Optional[int] = None
    wait_time: Optional[int] = None
    cover_category: Optional[CoverCategory] = None
    cover_price: Optional[float] = None


class BarReportResponse(BarReportCreate):
    id: int
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
