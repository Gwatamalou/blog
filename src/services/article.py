from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories import Article, ArticleRepository
from src.schemas.articles import ArticleCreate, ArticleUpdate

class ArticleService:

    def __init__(self, repository: ArticleRepository):
        """
        Инициализация сервиса статей

        :param repository: Репозиторий для работы с данными статей
        """
        self.repository = repository

    async def create_article(self, session: AsyncSession, article_in: ArticleCreate) -> Article:
        """Создает новую статью в базе данных"""
        return await self.repository.create_article(session=session, article_in=article_in)


    async def get_articles(self, session: AsyncSession) -> list[Article]:
        """Получает список всех статей"""
        result = await self.repository.get_articles(session)
        return list(result)

    async def get_article_by_id(self, session: AsyncSession, article_id: int) -> Article | None:
        """Получает статью по ее ID"""
        return await self.repository.get_article_by_id(session=session, article_id=article_id)

    async def update_article(self, session: AsyncSession, article_update: ArticleUpdate, article_id: int) -> Article:
        """Обновляет статью по её ID"""
        result = await self.repository.update_article(session=session, article_update=article_update, article_id=article_id)
        return result

    async def delete_article(self, session: AsyncSession, article_id: int) -> None:
        """
        Удаляет статью по её ID
        """
        await self.repository.delete_article(session=session, article_id=article_id)

