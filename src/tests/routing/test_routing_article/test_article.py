import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from src.app import app
from src.depends import get_articles_service, get_session



@pytest.fixture
def mock_articles_service():
    mock_service = AsyncMock()
    return mock_service


@pytest.fixture
def mock_session():
    mock_session = AsyncMock()
    return mock_session

article_data = {
            "id": 1,
            "title": "testtitle1",
            "text": "testtext1",
            "author_id": "71367bfa-b122-4c9a-ba45-afabdf646998",
            "rating": 0,
            "id": 1,
            "created_at": "2025-01-26T15:41:36.954484",
            "updated_at": None
        }


@pytest.mark.asyncio
def test_get_article_success(mock_articles_service, mock_session):

    app.dependency_overrides[get_articles_service] = lambda: mock_articles_service
    app.dependency_overrides[get_session] = lambda: mock_session
    mock_articles_service.get_article_by_id.return_value = article_data

    client = TestClient(app)
    response = client.get("/article/1")

    app.dependency_overrides ={}

    assert response.status_code == 200
    assert response.json() == article_data



@pytest.mark.asyncio
def test_get_article_fail(mock_articles_service, mock_session):

    app.dependency_overrides[get_articles_service] = lambda: mock_articles_service
    app.dependency_overrides[get_session] = lambda: mock_session
    mock_articles_service.get_article_by_id.return_value = None

    client = TestClient(app)
    response = client.get("/article/1")

    app.dependency_overrides = {}

    assert response.status_code == 404
    assert response.json() == {"detail": "Article not found"}
