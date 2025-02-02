from fastapi import HTTPException, status
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories import ArticleRepository
from src.schemas import ArticleUpdate
from .fake_database import FakeDatabase


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session")
async def get_session():
    fake_db = FakeDatabase()
    await fake_db.init_test_database()
    yield fake_db.test_session


@pytest.fixture(scope="function")
async def db_session(get_session) -> AsyncSession:
    async with get_session() as session:
        yield session


@pytest.mark.anyio
async def test_get_articles(db_session):
    article_repo = ArticleRepository()
    articles = await article_repo.get_articles(db_session)
    assert isinstance(articles, list)
    assert len(articles) > 0


@pytest.mark.anyio
async def test_get_article_by_id(db_session):
    article_repo = ArticleRepository()
    article_id = 1
    article = await article_repo.get_article_by_id(db_session, article_id)
    assert article is not None
    assert article.id == article_id


@pytest.mark.anyio
async def test_get_article_by_id_not_found(db_session):
    article_repo = ArticleRepository()
    article_id = 9999
    with pytest.raises(HTTPException) as exc_info:
        await article_repo.get_article_by_id(db_session, article_id)
    assert exc_info.value.status_code == 404


@pytest.mark.anyio
async def test_delete_article(db_session):
    article_repo = ArticleRepository()
    article_id = 2
    await article_repo.delete_article(db_session, article_id)
    with pytest.raises(HTTPException) as exc_info:
        await article_repo.get_article_by_id(db_session, article_id)
    assert exc_info.value.status_code == 404
