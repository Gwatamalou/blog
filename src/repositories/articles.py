from typing import Type
from src.schemas import ArticleCreate, ArticleUpdate, Article
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .model import Article as ArticleModel


class ArticleRepository:

    async def create_article(self, session: AsyncSession, article_in: ArticleCreate) -> Article:
        article = ArticleModel(**article_in.model_dump())
        session.add(article)
        await session.commit()
        await session.refresh(article)
        return article


    async def get_articles(self, session: AsyncSession) -> list[Article]:
        stmt = select(ArticleModel)
        res = await session.execute(stmt)
        articles = res.scalars().all()
        return list(articles)


    async def get_article_by_id(self, session: AsyncSession, article_id: int) -> Type[Article] | None:
        return await session.get(ArticleModel, article_id)


    async def update_article(self, session: AsyncSession, article_update: ArticleUpdate, article_id: int) -> Article | None:
        article = await self.get_article_by_id(session=session, article_id=article_id)

        if not article:
            return None

        for key, value in article_update.model_dump().items():
            setattr(article, key, value)

        await session.commit()
        return article_update


    async def delete_article(self, session: AsyncSession, article_id: int) -> None:
        article = await self.get_article_by_id(session=session, article_id=article_id)

        if article:
            await session.delete(article)
            await session.commit()

        return None