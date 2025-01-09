from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result

from src.repositories.model import Article
from src.schemas.blog import ArticleCreate, ArticleUpdate

from ..config import logger


@logger.catch
async def get_articles(session: AsyncSession) -> list[Article]:
    stmt = select(Article)
    res: Result = await session.execute(stmt)
    articles = res.scalars().all()
    return list(articles)


@logger.catch
async def get_article(session: AsyncSession, article_id: int) -> Article | None:
    return await session.get(Article, article_id)


@logger.catch
async def create_article(session: AsyncSession, article_in: ArticleCreate) -> Article | None:
    article = Article(**article_in.model_dump())
    session.add(article)
    await session.commit()
    await session.refresh(article)
    return article


@logger.catch
async def update_article(session: AsyncSession, article_id: int, article_update: ArticleUpdate) -> Article | None:

    article = await get_article(session, article_id)

    if not article:
        return None

    for key, value in article_update.model_dump().items():
        setattr(article, key, value)

    await session.commit()
    return article_update


@logger.catch
async def delete_article(session: AsyncSession, article_id: int) -> None:
    article = await session.get(Article, article_id)

    if article:
        await session.delete(article)
        await session.commit()

    return None
