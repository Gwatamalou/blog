import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from pydantic import BaseModel, EmailStr
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


class User(BaseModel):
    name: str = "username"
    email: EmailStr = "user@email.com"
    uuid: str = "user_uuid"
    role: str = "user"


@pytest.mark.asyncio
async def test_auth_success(mock_authentication_service, mock_session):
    user_data = {
        "username": "test_user",
        "password": "test_password"
    }

    app.dependency_overrides[get_authentication_service] = lambda: mock_authentication_service
    app.dependency_overrides[get_session] = lambda: mock_session

    mock_authentication_service.verify_user.return_value = User()
    mock_authentication_service.create_access_token.return_value = "access_token"
    mock_authentication_service.create_refresh_token.return_value = "refresh_token"

    client = TestClient(app)
    response = client.post("/auth", data=user_data)

    app.dependency_overrides = {}

    assert response.status_code == 200
    assert "X-Access-Token" in response.headers
    assert "X-Refresh-Token" in response.headers
    assert response.json() == {'name': 'username', 'email': 'user@email.com', 'uuid': 'user_uuid', 'role': 'user'}




@pytest.mark.asyncio
async def test_auth_fail(mock_authentication_service, mock_session):
    user_data = {
        "username": "wrong_user",
        "password": "wrong_password"
    }

    app.dependency_overrides[get_authentication_service] = lambda: mock_authentication_service
    app.dependency_overrides[get_session] = lambda: mock_session

    mock_authentication_service.verify_user.return_value = False

    client = TestClient(app)
    response = client.post("/auth", data=user_data)

    app.dependency_overrides = {}

    assert response.status_code == 401
