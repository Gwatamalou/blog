from typing import Annotated
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, EmailStr
from uuid import uuid4, UUID
from enum import Enum


class AccessLevel(Enum):
    superuser = "superuser"
    admin = "admin"
    user = "user"


class UserBase(BaseModel):
    name: Annotated[str, Field(min_length=3, max_length=50)]
    email: Annotated[EmailStr, Field(min_length=5, max_length=100)]


class UserIn(UserBase):
    password: Annotated[str, Field(alias="password_hash")]



class UserOut(UserBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    uuid: Annotated[UUID, Field(default_factory=uuid4)]
    role: Annotated[AccessLevel, Field(default=AccessLevel.user)]
    created_at: datetime
    deleted_at: datetime | None


class UserAll(UserBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    password_hash: Annotated[str, Field(alias="password_hash")]
    uuid: Annotated[UUID, Field(default_factory=uuid4)]
    role: Annotated[AccessLevel, Field(default=AccessLevel.user)]
    created_at: datetime
    deleted_at: datetime | None

