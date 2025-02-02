import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from src.app import app
from src.depends import get_authentication_service, get_session


@pytest.fixture
def mock_authentication_service():
    mock_service = AsyncMock()
    return mock_service


@pytest.fixture
def mock_session():
    mock_session = AsyncMock()
    return mock_session


@pytest.mark.asyncio
async def test_auth_refresh_success(mock_authentication_service, mock_session):
    refresh_token = "valid_refresh_token"
    new_access_token = "new_valid_access_token"

    app.dependency_overrides[get_authentication_service] = lambda: mock_authentication_service
    app.dependency_overrides[get_session] = lambda: mock_session

    mock_authentication_service.verify_refresh_token.return_value = new_access_token

    client = TestClient(app)
    response = client.post("/auth/refresh", headers={"X-Refresh-Token": refresh_token})

    app.dependency_overrides = {}

    assert response.status_code == 200
    assert response.json() == {"messages": "success"}
    assert response.headers["X-Access-Token"] == new_access_token


async def test_auth_refresh_invalid(mock_authentication_service, mock_session):
    refresh_token = "invalid_refresh_token"

    app.dependency_overrides[get_authentication_service] = lambda: mock_authentication_service
    app.dependency_overrides[get_session] = lambda: mock_session

    mock_authentication_service.verify_refresh_token.side_effect = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED)

    client = TestClient(app)
    response = client.post("/auth/refresh", headers={"X-Refresh-Token": refresh_token})

    app.dependency_overrides = {}

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_missing():
    client = TestClient(app)
    response = client.post("/auth/refresh")

    assert response.status_code == 401
    assert "X-Refresh-Token" not in response.headers


#
@pytest.mark.asyncio
async def test_refresh_token_no_token_in_header(mock_authentication_service, mock_session):
    client = TestClient(app)
    response = client.post("/auth/refresh", headers={"X-Refresh-Token": ""})

    app.dependency_overrides = {}

    assert response.status_code == 422
