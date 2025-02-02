import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta, timezone
from uuid import UUID
from fastapi import HTTPException
from src.services import TokenService, RegistrationService, AuthenticationService, AuthorizationService
from src.repositories import Refresh, AuthenticationRepository
from src.schemas import UserIn, UserOut, UserAll


@pytest.fixture
def mock_repository():
    return AsyncMock(spec=AuthenticationRepository)


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def token_service():
    return TokenService()


@pytest.fixture
def registration_service(mock_repository):
    return RegistrationService(repository=mock_repository)


@pytest.fixture
def authentication_service(mock_repository):
    return AuthenticationService(repository=mock_repository)


"""
TokenService
"""


@pytest.mark.asyncio
async def test_create_token_success(token_service):
    data = {"sub": "user_id"}
    expires = datetime.now(timezone.utc) + timedelta(minutes=15)

    token = await token_service.create_token(data=data, expires=expires)

    assert isinstance(token, str)


async def test_create_token_fail_not_sub(token_service):
    data = {}
    expires = datetime.now(timezone.utc) + timedelta(minutes=15)

    with pytest.raises(ValueError) as exc_info:
        await token_service.create_token(data=data, expires=expires)

    assert str(exc_info.value) == "Missing required key 'sub' in data"


@pytest.mark.asyncio
async def test_decode_valid_token(token_service):
    data = {"sub": "user_id"}
    expires = datetime.now() + timedelta(minutes=15)
    token = await token_service.create_token(data=data, expires=expires)

    decoded = await token_service.decode_token(token=token)

    assert decoded["sub"] == "user_id"


@pytest.mark.asyncio
async def test_decode_expired_token(token_service):
    data = {"sub": "user_id"}
    expires = datetime.now(timezone.utc) - timedelta(minutes=1)
    token = await token_service.create_token(data=data, expires=expires)

    with pytest.raises(HTTPException) as exc_info:
        await token_service.decode_token(token=token, verify_exp=True)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token expired"


@pytest.mark.asyncio
async def test_decode_invalid_token(token_service):
    token = ""

    with pytest.raises(HTTPException) as exc_info:
        await token_service.decode_token(token=token, verify_exp=True)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token"


"""
RegistrationService
"""


@pytest.mark.asyncio
async def test_create_new_user(registration_service, mock_session, mock_repository):
    user_in = UserIn(name="testname", email="email@email.com", password_hash="password")
    user_out = UserOut(name="testname", email="email@email.com",
                       uuid=UUID("c846b311-23cb-4a61-a96a-bd48e39402e1"), role="user",
                       created_at=datetime.now(timezone.utc), deleted_at=None)

    mock_repository.create_new_user.return_value = user_out

    result = await registration_service.create_new_user(user_in=user_in, session=mock_session)

    assert result == user_out



"""
AuthenticationService
"""

class UserData:
    ...

@pytest.mark.asyncio
async def test_verify_user_success(authentication_service, mock_session, mock_repository):
    user_in = UserData()
    user_in.username = "testname"
    user_in.password ="password"
    user_out = UserAll(
        name="testname",
        email="email@email.com",
        password_hash="password",
        uuid=UUID("e16c5d2d-3959-476a-833e-6bbe720df2ef"),
        role="user",
        created_at=datetime.now(timezone.utc),
        deleted_at=None
    )

    mock_repository.get_user_data.return_value = user_out
    authentication_service.verify_password = AsyncMock(return_value=True)

    result = await authentication_service.verify_user(user_data=user_in, session=mock_session)

    assert result == UserOut(**user_out.model_dump())


@pytest.mark.asyncio
async def test_verify_user_incorrect_password(authentication_service, mock_session, mock_repository):
    user_in = UserData()
    user_in.username = "testname"
    user_in.password = "password_fial"
    user_out = UserAll(
        name="testname",
        email="email@email.com",
        password_hash="password",
        uuid=UUID("e16c5d2d-3959-476a-833e-6bbe720df2ef"),
        role="user",
        created_at=datetime.now(timezone.utc),
        deleted_at=None
    )

    mock_repository.get_user_data.return_value = user_out
    authentication_service.verify_password = AsyncMock(return_value=False)

    with pytest.raises(HTTPException) as exc_info:
        await authentication_service.verify_user(user_data=user_in, session=mock_session)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Incorrect user or password"

@pytest.mark.asyncio
async def test_create_access_token(authentication_service):
    data = {"sub": "user_id"}

    token = await authentication_service.create_access_token(data=data)

    assert isinstance(token, str)



@pytest.mark.asyncio
async def test_verify_access_token(authentication_service):
    token_service = authentication_service.token_service
    data = {"sub": "123e4567-e89b-12d3-a456-426614174000"}
    access_token = await token_service.create_token(data=data, expires=datetime.now() + timedelta(minutes=15))

    user_uuid = await authentication_service.verify_access_token(access_token=access_token)

    assert user_uuid == UUID("123e4567-e89b-12d3-a456-426614174000")


@pytest.mark.asyncio
async def test_save_refresh_token(authentication_service, mock_repository, mock_session):
    refresh_token = Refresh(user_uuid="user_id", token="refresh_token", expires_at=datetime.now())

    await authentication_service.save_refresh_token(token=refresh_token, session=mock_session)

    mock_repository.save_refresh_token.assert_called_once_with(token=refresh_token, session=mock_session)


