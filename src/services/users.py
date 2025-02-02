from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories import UserRepository
from src.schemas import UserOut


class UserService:

    def __init__(self, repository: UserRepository):
        self.repository = repository


    async def get_user(self, username: str, session: AsyncSession) -> UserOut:
        return await self.repository.get_user(username=username, session=session)

    async def get_users(self, session: AsyncSession) -> list[UserOut]:
        return await self.repository.get_users(session=session)