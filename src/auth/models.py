from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    LargeBinary,
    String,
    Table,
    func,
)
from sqlalchemy.dialects.postgresql import UUID

from ..database import metadata

Users = Table(
    "users",
    metadata,
    Column("id", UUID, primary_key=True),
    Column("username", String, server_default="", nullable=False),
    Column("email", String, unique=True, nullable=False),
    Column("password", LargeBinary, nullable=False),
    Column("full_name", String, server_default="", nullable=False),
    Column(
        "profile_picture_url",
        String,
        server_default="https://example.com/default-profile-picture.jpg",
        nullable=False,
    ),
    Column("is_admin", Boolean, server_default="false", nullable=False),
    Column(
        "created_at", DateTime(timezone=True), server_default=func.now(), nullable=False
    ),
    Column("updated_at", DateTime(timezone=True), onupdate=func.now()),
)
