from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID, uuid4
from datetime import datetime



class ArticleBase(BaseModel):
    title: Annotated[str, Field(max_length=100)]
    text: Annotated[str, Field(max_length=10000)]
    author_id: Annotated[UUID, Field(default_factory=uuid4)]
    rating: Annotated[float, Field(default=0.0, ge=0.0, le=5.0)]



class ArticleCreate(ArticleBase):
    ...


class Article(ArticleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Annotated[datetime, Field(default=datetime.now())]
    updated_at: datetime | None = None


class ArticleUpdate(Article):
    ...
