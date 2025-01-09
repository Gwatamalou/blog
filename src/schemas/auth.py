from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, EmailStr
from uuid import uuid4, UUID


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class UserBase(BaseModel):
    name: Annotated[str, Field(min_length=3, max_length=50)]
    email: Annotated[EmailStr, Field(min_length=5, max_length=100)]


class UserIn(UserBase):
    model_config = ConfigDict(strict=True)

    password: str



class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)
    uuid: Annotated[UUID, Field(default_factory=uuid4)]
