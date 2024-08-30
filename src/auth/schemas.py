import enum
import re
from typing import Optional
from uuid import UUID

from pydantic import EmailStr, Field, field_validator, model_validator
from sqlalchemy.ext.asyncio import AsyncSession

from src.bars.schemas import BarBase
from src.models import CustomModel

STRONG_PASSWORD_PATTERN = re.compile(r"^(?=.*[\d])(?=.*[!@#$%^&*])[\w!@#$%^&*]{6,128}$")


class UserRole(str, enum.Enum):
    USER = "user"
    BAR_ADMIN = "bar_admin"


class BarDetails(BarBase):
    pass


class UserCreate(CustomModel):
    email: EmailStr
    username: str = Field(default=None)
    password: str = Field(min_length=6, max_length=128)
    role: UserRole = UserRole.USER
    bar_details: Optional[BarDetails] = None

    @model_validator(mode="after")
    def validate_role_and_bar_details(self):
        if self.role == UserRole.BAR_ADMIN and not self.bar_details:
            raise ValueError("Bar details are required for bar admin registration")
        if self.role == UserRole.USER and self.bar_details:
            raise ValueError(
                "Bar details should not be provided for regular user registration"
            )
        return self

    @field_validator("password")
    @classmethod
    def valid_password(cls, password: str) -> str:
        if not re.match(STRONG_PASSWORD_PATTERN, password):
            raise ValueError(
                "Password must contain at least "
                "one lower character, "
                "one upper character, "
                "digit or "
                "special symbol"
            )
        return password

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "StrongP@ssw0rd",
                "role": "bar_admin",
                "username": "example_username",
                "bar_details": {
                    "address": "123 Main St, City, Country",
                    "name": "Example Bar",
                    "phone": "+1234567890",
                },
            },
            "example 2": {
                "email": "user@example.com",
                "password": "StrongP@ssw0rd",
                "role": "user",
                "username": "example_username",
            },
        }


class UserLogin(CustomModel):
    email: EmailStr
    username: Optional[str] = Field(default=None, exclude=True)
    password: str = Field(min_length=6, max_length=128)

    @field_validator("password", mode="after")
    @classmethod
    def valid_password(cls, password: str) -> str:
        if not re.match(STRONG_PASSWORD_PATTERN, password):
            raise ValueError(
                "Password must contain at least "
                "one lower character, "
                "one upper character, "
                "digit or "
                "special symbol"
            )

        return password

    @model_validator(mode="after")
    def check_email_or_username(self) -> "UserLogin":
        if not self.email and not self.username:
            raise ValueError("Either email or username must be provided")
        return self

    class Config:
        json_schema_extra = {
            "example": {"email": "user@example.com", "password": "StrongP@ssw0rd"}
        }


class AuthorizeCreds(CustomModel):
    email: Optional[EmailStr] = None
    username: str = Field(default=None, exclude=True)
    password: str = Field(min_length=6, max_length=128)

    @field_validator("password", mode="after")
    @classmethod
    def valid_password(cls, password: str) -> str:
        if not re.match(STRONG_PASSWORD_PATTERN, password):
            raise ValueError(
                "Password must contain at least "
                "one lower character, "
                "one upper character, "
                "digit or "
                "special symbol"
            )

        return password

    @model_validator(mode="after")
    def check_email_or_username(self) -> "AuthorizeCreds":
        if not self.email and not self.username:
            raise ValueError("Either email or username must be provided")
        return self

    class Config:
        json_schema_extra = {
            "example": {"email": "user@example.com", "password": "StrongP@ssw0rd"}
        }


class JWTData(CustomModel):
    user_id: UUID = Field(alias="sub")
    is_admin: bool = False


class AccessTokenResponse(CustomModel):
    access_token: str
    refresh_token: str


class UserResponse(CustomModel):
    id: UUID
    email: EmailStr
    username: str
    full_name: str
    profile_picture_url: str


class UserUpdate(CustomModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    profile_picture_url: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "username": "new_username",
                "full_name": "New Full Name",
                "profile_picture_url": "https://example.com/new-profile-picture.jpg",
            }
        }


class SocialLogin(CustomModel):
    provider: str
    token: str

    class Config:
        json_schema_extra = {
            "example": {
                "provider": "google",
                "token": "google_access_token",
            }
        }


class UserAndDB(CustomModel):
    user: dict
    db: AsyncSession

    class Config:
        arbitrary_types_allowed = True
