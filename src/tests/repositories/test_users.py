from fastapi import HTTPException, status
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories import UserRepository
from .fake_database import FakeDatabase




@pytest.fixture(scope="module", autouse=True)
async def init_db():
    fake_db = FakeDatabase()
    await fake_db.init_test_database()
    yield
    fake_db.drop_test_database()


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session")
async def get_session():
    fake_db = FakeDatabase()
    yield fake_db.test_session


@pytest.fixture(scope="function")
async def db_session(get_session) -> AsyncSession:
    async with get_session() as session:
        yield session


@pytest.mark.anyio
async def test_get_user(db_session):
    user_repo = UserRepository()
    username = "User5"

    user = await user_repo.get_user(username, db_session)

    assert user is not None
    assert user.name == username


@pytest.mark.anyio
async def test_get_user_none(db_session):
    user_repo = UserRepository()
    username = ""

    user = await user_repo.get_user(username, db_session)
    assert user is None



@pytest.mark.anyio
async def test_get_users(db_session):
    user_repo = UserRepository()

    users = await user_repo.get_users(db_session)

    assert isinstance(users, list)



@pytest.mark.anyio
async def test_get_user_faild_db(db_session):
    user_repo = AsyncMock()
    user_repo.get_user.side_effect = HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    with pytest.raises(HTTPException) as exc_info:
        await user_repo.get_user("User5", db_session)

    assert exc_info.value.status_code == 500


@pytest.mark.anyio
async def test_get_users_faild_db(db_session):
    user_repo = AsyncMock()
    user_repo.get_users.side_effect = HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    with pytest.raises(HTTPException) as exc_info:
        await user_repo.get_users(db_session)

    assert exc_info.value.status_code == 500