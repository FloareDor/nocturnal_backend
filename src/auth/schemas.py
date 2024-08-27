# schema.py
import re
from typing import Optional
from uuid import UUID

from pydantic import EmailStr, Field, field_validator, model_validator

from src.models import CustomModel

STRONG_PASSWORD_PATTERN = re.compile(r"^(?=.*[\d])(?=.*[!@#$%^&*])[\w!@#$%^&*]{6,128}$")


class UserCreate(CustomModel):
    email: EmailStr
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

    class Config:
        json_schema_extra = {
            "example": {
                "username": "example_username",
                "email": "user@example.com",
                "password": "StrongP@ssw0rd",
            }
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
    user_id: int = Field(alias="sub")
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
                "preferred_language": "spanish",
                "preferred_currency": "eur",
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
