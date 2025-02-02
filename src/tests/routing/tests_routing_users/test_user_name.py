import pytest
from pydantic import BaseModel
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from src.app import app
from src.depends import get_users_service, get_authentication_service, get_session


@pytest.fixture
def mock_users_service():
    mock_service = AsyncMock()
    return mock_service


@pytest.fixture
def mock_authentication_service():
    mock_service = AsyncMock()
    return mock_service


@pytest.fixture
def mock_session():
    mock_session = AsyncMock()
    return mock_session

class User(BaseModel):
    name: str = "testname"
    email: str = "testemail"
    uuid: str = "test_uuid"



@pytest.mark.asyncio
def test_users_name_success_owner(mock_users_service, mock_authentication_service, mock_session):
    user_data = {
        "name": "testname",
        "email":"test@emial.com",
        "uuid": "test_uuid"
    }
    access_token = "test_token"

    app.dependency_overrides[get_session] = lambda: mock_session
    app.dependency_overrides[get_authentication_service] = lambda: mock_authentication_service
    app.dependency_overrides[get_users_service] = lambda: mock_users_service


    mock_users_service.get_user.return_value = User()
    mock_authentication_service.verify_access_token.return_value = "test_uuid"

    client = TestClient(app)
    response = client.get("/users/name", headers={"x-access-token": "test_token"})

    assert response.status_code == 200
    assert response.json() == {'user': {'name': 'testname', 'email': 'testemail', 'uuid': 'test_uuid'}, 'is_owner': True}

    app.dependency_overrides = {}




@pytest.mark.asyncio
def test_users_name_success_not_owner(mock_users_service, mock_authentication_service, mock_session):
    user_data = {
        "name": "testname",
        "email":"test@emial.com",
        "uuid": "test_uuid"
    }
    access_token = "test_token"

    app.dependency_overrides[get_session] = lambda: mock_session
    app.dependency_overrides[get_authentication_service] = lambda: mock_authentication_service
    app.dependency_overrides[get_users_service] = lambda: mock_users_service


    mock_users_service.get_user.return_value = User()
    mock_authentication_service.verify_access_token.return_value = "faild_uuid"

    client = TestClient(app)
    response = client.get("/users/name", headers={"x-access-token": "test_token"})

    assert response.status_code == 200
    assert response.json() == {'user': {'name': 'testname', 'email': 'testemail', 'uuid': 'test_uuid'}, 'is_owner': False}

    app.dependency_overrides = {}




@pytest.mark.asyncio
def test_users_name_success_not_token(mock_users_service, mock_authentication_service, mock_session):
    user_data = {
        "name": "testname",
        "email":"test@emial.com",
        "uuid": "test_uuid"
    }
    access_token = "test_token"

    app.dependency_overrides[get_session] = lambda: mock_session
    app.dependency_overrides[get_authentication_service] = lambda: mock_authentication_service
    app.dependency_overrides[get_users_service] = lambda: mock_users_service


    mock_users_service.get_user.return_value = User()
    mock_authentication_service.verify_access_token.return_value = "faild_uuid"

    client = TestClient(app)
    response = client.get("/users/name", headers={"x-access-token": ""})


    assert response.status_code == 200
    assert response.json() == {'user': {'name': 'testname', 'email': 'testemail', 'uuid': 'test_uuid'}, 'is_owner': False}

    app.dependency_overrides = {}




@pytest.mark.asyncio
def test_users_name_success_not_header(mock_users_service, mock_authentication_service, mock_session):
    user_data = {
        "name": "testname",
        "email":"test@emial.com",
        "uuid": "test_uuid"
    }
    access_token = "test_token"

    app.dependency_overrides[get_session] = lambda: mock_session
    app.dependency_overrides[get_authentication_service] = lambda: mock_authentication_service
    app.dependency_overrides[get_users_service] = lambda: mock_users_service


    mock_users_service.get_user.return_value = User()
    mock_authentication_service.verify_access_token.return_value = "faild_uuid"

    client = TestClient(app)
    response = client.get("/users/name")

    assert response.status_code == 200
    assert response.json() == {'user': {'name': 'testname', 'email': 'testemail', 'uuid': 'test_uuid'}, 'is_owner': False}

    app.dependency_overrides = {}

