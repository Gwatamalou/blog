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




@pytest.mark.asyncio
def test_get_articles_success(mock_articles_service, mock_session):


    articles_data = [
        {
            "id": 1,
            "title": "testtitle1",
            "text": "testtext1",
            "author_id": "71367bfa-b122-4c9a-ba45-afabdf646998",
            "rating": 0,
            "id": 1,
            "created_at": "2025-01-26T15:41:36.954484",
            "updated_at": None
        },
        {
            "title": "testtitle",
            "text": "testtext",
            "author_id": "71367bfa-b122-4c9a-ba45-afabdf646998",
            "rating": 0,
            "id": 2,
            "created_at": "2025-01-26T15:41:36.954484",
            "updated_at": None
        },
        {
            "title": "testtitle",
            "text": "testtext",
            "author_id": "71367bfa-b122-4c9a-ba45-afabdf646998",
            "rating": 0,
            "id": 3,
            "created_at": "2025-01-26T15:41:36.954484",
            "updated_at": None
        }
    ]
    app.dependency_overrides[get_session] = lambda: mock_session
    app.dependency_overrides[get_articles_service] = lambda: mock_articles_service

    mock_articles_service.get_articles.return_value = articles_data

    client = TestClient(app)
    response = client.get("/article")

    app.dependency_overrides = {}

    print(response.json())

    assert response.status_code == 200
    assert response.json() == articles_data