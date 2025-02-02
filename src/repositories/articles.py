from typing import Type
from sqlalchemy.exc import SQLAlchemyError
from src.schemas import ArticleCreate, ArticleUpdate, Article
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .model import Article as ArticleModel
from fastapi import HTTPException, status


class ArticleRepository:

    async def create_article(self, session: AsyncSession, article_in: ArticleCreate) -> Article:
        article = ArticleModel(**article_in.model_dump())
        try:
            session.add(article)
            await session.commit()
            await session.refresh(article)
            return article
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def get_articles(self, session: AsyncSession) -> list[Article]:
        stmt = select(ArticleModel)
        try:
            res = await session.execute(stmt)
            articles = res.scalars().all()
            return list(articles)
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


    async def get_article_by_id(self, session: AsyncSession, article_id: int) -> Type[Article] | None:
        try:
            result = await session.get(ArticleModel, article_id)

            if result is not None:
                return result

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found"
            )
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


    async def update_article(self, session: AsyncSession, article_update: ArticleUpdate, article_id: int) -> Article | None:
        try:
            article = await self.get_article_by_id(session=session, article_id=article_id)

            if not article:
                return None

            for key, value in article_update.model_dump().items():
                setattr(article, key, value)

            await session.commit()
            return article_update
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


    async def delete_article(self, session: AsyncSession, article_id: int) -> None:
        try:
            article = await self.get_article_by_id(session=session, article_id=article_id)

            if article:
                await session.delete(article)
                await session.commit()

            return None
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)