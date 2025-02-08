from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories import UserRepository
from src.schemas import UserOut


class UserService:
    """
    Сервис для работы с пользователями.
    Этот сервис предоставляет методы для получения информации о пользователях.
    """
    def __init__(self, repository: UserRepository):
        """
        Инициализация сервиса с репозиторием.

        :param repository: Репозиторий для работы с данными пользователей.
        """
        self.repository = repository


    async def get_user(self, username: str, session: AsyncSession) -> UserOut:
        """Получает информацию о пользователе по имени"""
        return await self.repository.get_user(username=username, session=session)

    async def get_users(self, session: AsyncSession) -> list[UserOut]:
        """ Получает список всех пользователей"""
        return await self.repository.get_users(session=session)