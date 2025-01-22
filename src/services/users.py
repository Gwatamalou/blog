from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories import UserRepository
from src.schemas import UserOut


class UserService:

    def __init__(self, repository: UserRepository):
        self.repository = repository


    async def get_user(self, username: str, session: AsyncSession) -> UserOut:
        user = await self.repository.get_user(username=username, session=session)
        return user

    async def get_users(self, session: AsyncSession) -> list[UserOut]:
        users =  await self.repository.get_users(session=session)
        return users