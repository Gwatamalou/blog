from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.model import Article
from src.schemas.articles import ArticleCreate, ArticleUpdate
from ..config import logger
from ..repositories import ArticleRepository


class ArticleService:

    def __init__(self, repository: ArticleRepository):
        self.repository = repository

    async def create_article(self, session: AsyncSession, article_in: ArticleCreate) -> Article:
        result = await self.repository.create_article(session=session, article_in=article_in)
        return result

    async def get_articles(self, session: AsyncSession) -> list[Article]:
        result = await self.repository.get_articles(session)
        return list(result)

    async def get_article_by_id(self, session: AsyncSession, article_id: int) -> Article | None:
        result = await self.repository.get_article_by_id(session=session, article_id=article_id)
        return result

    async def update_article(self, session: AsyncSession, article_update: ArticleUpdate, article_id: int) -> Article:
        result = await self.repository.update_article(session=session, article_update=article_update, article_id=article_id)
        return result

    async def delete_article(self, session: AsyncSession, article_id: int) -> None:
        await self.repository.delete_article(session=session, article_id=article_id)

