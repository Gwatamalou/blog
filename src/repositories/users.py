from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Sequence
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from src.repositories import User


class UserRepository:

    async def get_user(self, username: str, session: AsyncSession) -> User:
        stmt = select(User).where(User.name == username).limit(1)
        try:
            result = await session.execute(stmt)
            user = result.scalars().first()
            return user
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def get_users(self, session: AsyncSession) -> Sequence[User]:
        stmt = select(User).order_by(User.uuid)
        try:
            res = await session.execute(stmt)
            users = res.scalars().all()
            return users
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
