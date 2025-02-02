from fastapi import HTTPException, status
from unittest.mock import AsyncMock
from src.depends import get_registration_service, get_session
import pytest
from fastapi.testclient import TestClient
from src.app import app



@pytest.fixture
def mock_registration_service():
    mock_service = AsyncMock()
    return mock_service


@pytest.fixture
def mock_session():
    mock_session = AsyncMock()
    return mock_session



@pytest.mark.asyncio
async def test_auth_register_success(mock_registration_service, mock_session):
    user_data = {
        "name": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword"
    }
    test_user = {
        "name": "testuser",
        "email": "testuser@example.com",
        "uuid": "c846b311-23cb-4a61-a96a-bd48e39402e1",
        "role": "user",
        "created_at": "2025-01-26T18:39:00",
        "deleted_at": None
    }

    app.dependency_overrides[get_registration_service] = lambda: mock_registration_service
    app.dependency_overrides[get_session] = lambda: mock_session

    mock_registration_service.create_new_user.return_value = test_user

    client = TestClient(app)
    response = client.post("/auth/register", data=user_data)

    app.dependency_overrides = {}

    assert response.status_code == 201
    assert response.json() == test_user


@pytest.mark.asyncio
async def test_auth_register_user_name_already_exists(mock_registration_service, mock_session):
    user_data = {
        "name": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword"
    }
    app.dependency_overrides[get_registration_service] = lambda: mock_registration_service
    app.dependency_overrides[get_session] = lambda: mock_session

    mock_registration_service.create_new_user.side_effect  = HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with the name already exists")

    client = TestClient(app)
    response = client.post("/auth/register", data=user_data)

    app.dependency_overrides = {}

    assert response.status_code == 409
    assert response.json() == {"detail": "User with the name already exists"}



@pytest.mark.asyncio
async def test_auth_register_user_email_already_exists(mock_registration_service, mock_session):
    user_data = {
        "name": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword"
    }
    app.dependency_overrides[get_registration_service] = lambda: mock_registration_service
    app.dependency_overrides[get_session] = lambda: mock_session

    mock_registration_service.create_new_user.side_effect  = HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with the email already exists")

    client = TestClient(app)
    response = client.post("/auth/register", data=user_data)

    app.dependency_overrides = {}

    assert response.status_code == 409
    assert response.json() == {"detail": "User with the email already exists"}



@pytest.mark.asyncio
async def test_auth_register_unexpected(mock_registration_service, mock_session):
    user_data = {
        "name": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword"
    }
    app.dependency_overrides[get_registration_service] = lambda: mock_registration_service
    app.dependency_overrides[get_session] = lambda: mock_session

    mock_registration_service.create_new_user.side_effect  = HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")

    client = TestClient(app)
    response = client.post("/auth/register", data=user_data)

    app.dependency_overrides = {}

    assert response.status_code == 500
    assert response.json() == {"detail": "An unexpected error occurred"}