from datetime import datetime
from uuid import UUID

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories import Article, ArticleRepository
from src.schemas import ArticleCreate, ArticleUpdate
from src.services import ArticleService


@pytest.fixture
def mock_repository():
    return AsyncMock(spec=ArticleRepository)


@pytest.fixture
def article_service(mock_repository):
    return ArticleService(repository=mock_repository)


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


article_in = ArticleCreate(title="Test Article", text="Test Content",
                           author_id=UUID("a0e2049d-d364-40a2-9696-e8af600617c3"), rating=1.0)
article_out = Article(title="Test Article", text="Test Content",
                      author_id=UUID("a0e2049d-d364-40a2-9696-e8af600617c3"), rating=1.0, id=1,
                      created_at=datetime.now(), updated_at=None)
article_update = ArticleUpdate(title="Test Article", text="Test Content Updated",
                      author_id=UUID("a0e2049d-d364-40a2-9696-e8af600617c3"), rating=1.0, id=1,
                      created_at=datetime.now(), updated_at=datetime.now())



@pytest.mark.asyncio
async def test_create_article(article_service, mock_repository, mock_session):
    mock_repository.create_article.return_value = article_out

    result = await article_service.create_article(session=mock_session, article_in=article_in)

    mock_repository.create_article.assert_called_once_with(session=mock_session, article_in=article_in)
    assert result == article_out


@pytest.mark.asyncio
async def test_get_articles(article_service, mock_repository, mock_session):
    articles = [article_out, article_out]
    mock_repository.get_articles.return_value = articles

    result = await article_service.get_articles(session=mock_session)

    mock_repository.get_articles.assert_called_once_with(mock_session)
    assert result == articles



@pytest.mark.asyncio
async def test_get_article_by_id(article_service, mock_repository, mock_session):
    article_id = 1

    mock_repository.get_article_by_id.return_value = article_out

    result = await article_service.get_article_by_id(session=mock_session, article_id=article_id)

    mock_repository.get_article_by_id.assert_called_once_with(session=mock_session, article_id=article_id)
    assert result == article_out


@pytest.mark.asyncio
async def test_update_article(article_service, mock_repository, mock_session):
    article_id = 1
    mock_repository.update_article.return_value = article_out
    result = await article_service.update_article(session=mock_session, article_update=article_update, article_id=article_id)

    mock_repository.update_article.assert_called_once_with(session=mock_session, article_update=article_update, article_id=article_id)
    assert result == article_out


@pytest.mark.asyncio
async def test_delete_article(article_service, mock_repository, mock_session):
    article_id = 1
    mock_repository.delete_article.return_value = None

    result = await article_service.delete_article(session=mock_session, article_id=article_id)
    mock_repository.delete_article.assert_called_once_with(session=mock_session, article_id=article_id)

    assert result is None
