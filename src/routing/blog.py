from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..repositories import db
from ..services import blog
from ..schemas.blog import Article, ArticleCreate, ArticleUpdate

router = APIRouter(tags=["blog"])


@router.get(
    "/",
    response_model=list[Article],
)
async def get_articles(
        session: AsyncSession = Depends(db.session_dependency),
):
    return await blog.get_articles(session=session)


@router.get(
    "/{article_id}",
    response_model=Article,
)
async def get_article(article_id: int,
                      session: AsyncSession = Depends(db.session_dependency),
):
    article = await blog.get_article(article_id=article_id, session=session)
    if article is not None:
        return article

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Article not found"
    )


@router.post(
    "/",
    response_model=Article,
)
async def create_article(
        article_in: ArticleCreate,
        session: AsyncSession = Depends(db.session_dependency),
):
    return await blog.create_article(session=session, article_in=article_in)


@router.put("/",
             response_model=Article,
)
async def update_article(
        article_update: ArticleUpdate,
        session: AsyncSession = Depends(db.session_dependency),
):
    return await blog.update_article(session=session, article_id=article_update.id, article_update=article_update)


@router.delete("/")
async def delete_article(
        article_id: int,
        session: AsyncSession = Depends(db.session_dependency),
):
    return await blog.delete_article(session=session, article_id=article_id)
