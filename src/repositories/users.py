from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.repositories import User


class UserRepository:

    async def get_user(self, username: str, session: AsyncSession) -> User:
        stmt = select(User).where(User.name == username).limit(1)
        result = await session.execute(stmt)
        user = result.scalars().first()
        return user

    async def get_users(self, session: AsyncSession) -> list[User]:
        stmt = select(User).order_by(User.uuid)
        res = await session.execute(stmt)
        users = res.scalars().all()
        return list(users)