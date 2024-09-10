from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.bar_reports.schemas import CoverCategory, LineLengthCategory


class BarBase(BaseModel):
    name: str = Field(..., example="The Cozy Corner")
    address: Optional[str] = Field(None, example="123 Main St, Cityville, State 12345")
    phone: str = Field(..., example="+1 (555) 123-4567")
    image_url: Optional[str] = Field(None, example="https://example.com/bar-image.jpg")
    latitude: Optional[float] = Field(None, example=40.7128)
    longitude: Optional[float] = Field(None, example=-74.0060)


class BarCreate(BarBase):
    class Config:
        json_schema_extra = {
            "example": {
                "name": "The Cozy Corner",
                "address": "123 Main St, Cityville, State 12345",
                "phone": "+1 (555) 123-4567",
                "image_url": "https://example.com/bar-image.jpg",
                "latitude": 40.7128,
                "longitude": -74.0060,
            }
        }


class BarUpdate(BaseModel):
    name: Optional[str] = Field(None, example="The Cozy Corner Lounge")
    address: Optional[str] = Field(None, example="124 Main St, Cityville, State 12345")
    phone: Optional[str] = Field(None, example="+1 (555) 987-6543")
    image_url: Optional[str] = Field(
        None, example="https://example.com/updated-bar-image.jpg"
    )
    latitude: Optional[float] = Field(None, example=40.7129)
    longitude: Optional[float] = Field(None, example=-74.0061)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "The Cozy Marston Lounge",
                "phone": "+1 (555) 987-6543",
                "image_url": "https://example.com/updated-bar-image.jpg",
                "address": "124 Main St, Cityville, State 12345",
                "longitude": -80,
            }
        }


class BarResponse(BarBase):
    id: int = Field(..., example=1)
    verified: bool = Field(..., example=True)
    rating: Optional[float] = Field(None, example=4.5)
    rating_count: int = Field(..., example=128)
    created_at: datetime = Field(..., example="2023-08-30T14:30:00Z")
    updated_at: datetime = Field(..., example="2023-08-30T14:30:00Z")

    # Updated fields for line length and cover information
    line_length: Optional[float] = Field(None, example=15.5)
    line_length_category: Optional[LineLengthCategory] = Field(
        None, example=LineLengthCategory.MEDIUM
    )
    # line_length_distribution: Optional[List[LineLengthCategory]] = Field(
    #     None,
    #     example=[
    #         LineLengthCategory.SMALL,
    #         LineLengthCategory.MEDIUM,
    #         LineLengthCategory.MEDIUM,
    #         LineLengthCategory.LONG,
    #     ],
    # )

    cover_category: Optional[CoverCategory] = Field(
        None, example=CoverCategory.MODERATE
    )
    # cover_category_distribution: Optional[List[CoverCategory]] = Field(
    #     None,
    #     example=[
    #         CoverCategory.CHEAP,
    #         CoverCategory.MODERATE,
    #         CoverCategory.MODERATE,
    #         CoverCategory.EXPENSIVE,
    #     ],
    # )
    cover_price: Optional[float] = Field(None, example=10.50)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "The Cozy Corner",
                "address": "123 Main St, Cityville, State 12345",
                "phone": "+1 (555) 123-4567",
                "image_url": "https://example.com/bar-image.jpg",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "verified": True,
                "rating": 4.5,
                "rating_count": 128,
                "created_at": "2023-08-30T14:30:00Z",
                "updated_at": "2023-08-30T14:30:00Z",
                "line_length": 15.5,
                "line_length_category": "medium",
                "line_length_distribution": ["small", "medium", "medium", "long"],
                "cover_category": "moderate",
                "cover_category_distribution": [
                    "cheap",
                    "moderate",
                    "moderate",
                    "expensive",
                ],
                "cover_price": 10.50,
            }
        }
