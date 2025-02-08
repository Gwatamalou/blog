from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Sequence
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from src.repositories import User


class UserRepository:
    """
    Репозиторий для работы с пользователями. Содержит методы для получения одного пользователя
    по имени, а также для получения списка всех пользователей.
    """

    async def get_user(self, username: str, session: AsyncSession) -> User:
        """
        Получает пользователя по имени.

        :param username: Имя пользователя для поиска.
        :param session: Асинхронная сессия для работы с базой данных.
        :return: Данные пользователя, если он найден.
        :raises HTTPException: Ошибка сервера, если произошла ошибка при выполнении запроса.
        """
        stmt = select(User).where(User.name == username).limit(1)
        try:
            result = await session.execute(stmt)
            user = result.scalars().first()
            return user
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def get_users(self, session: AsyncSession) -> Sequence[User]:
        """
        Получает список всех пользователей, отсортированных по UUID.

        :param session: Асинхронная сессия для работы с базой данных.
        :return: Список всех пользователей.
        :raises HTTPException: Ошибка сервера, если произошла ошибка при выполнении запроса.
        """
        stmt = select(User).order_by(User.uuid)
        try:
            res = await session.execute(stmt)
            users = res.scalars().all()
            return users
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
