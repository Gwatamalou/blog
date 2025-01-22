from fastapi import APIRouter, HTTPException, status, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.articles import Article, ArticleCreate, ArticleUpdate
from ..services import ArticleService, AuthenticationService, authorization
from src.depends import get_articles_service, get_session, get_authentication_service



router = APIRouter(tags=["article"])


@router.get("/",
            response_model=list[Article])
async def get_articles(article_service: ArticleService = Depends(get_articles_service),
                       session: AsyncSession = Depends(get_session)
                       ):
    return await article_service.get_articles(session)


@router.get("/{article_id}",
            response_model=Article)
async def get_article(article_id: int,
                      article_service: ArticleService = Depends(get_articles_service),
                      session: AsyncSession = Depends(get_session)
                      ):
    article = await article_service.get_article_by_id(session=session, article_id=article_id)

    if article is not None:
        return article

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Article not found"
    )


@router.post("/",
             response_model=Article)
@authorization("user")
async def create_article(article_in: ArticleCreate,
                         articles_service: ArticleService = Depends(get_articles_service),
                         x_access_token: str = Header(None),
                         auth_service: AuthenticationService = Depends(get_authentication_service),
                         session: AsyncSession = Depends(get_session)
                         ):
    return await articles_service.create_article(session=session, article_in=article_in)


@router.put("/",
            response_model=Article)
async def update_article(article_update: ArticleUpdate,
                         articles_service: ArticleService = Depends(get_articles_service),
                         session: AsyncSession = Depends(get_session)
                         ):
    return await articles_service.update_article(session=session, article_update=article_update,
                                                 article_id=article_update.id)


@router.delete("/")
async def delete_article(article_id: int,
                         articles_service: ArticleService = Depends(get_articles_service),
                         session: AsyncSession = Depends(get_session)):
    return await articles_service.delete_article(session=session, article_id=article_id)
