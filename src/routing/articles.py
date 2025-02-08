from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.articles import Article, ArticleCreate, ArticleUpdate
from src.services import ArticleService, AuthenticationService, authorization
from src.depends import get_articles_service, get_session, get_authentication_service



router = APIRouter(tags=["article"])


@router.get("/",
            response_model=list[Article],
            )
async def get_articles(article_service: ArticleService = Depends(get_articles_service),
                       session: AsyncSession = Depends(get_session)
                       ):
    """Возращает список всех статей"""
    return await article_service.get_articles(session)


@router.get("/{article_id}",
            response_model=Article,
            )
async def get_article(article_id: int,
                      article_service: ArticleService = Depends(get_articles_service),
                      session: AsyncSession = Depends(get_session)
                      ):
    """Возращает статью по ID"""
    return await article_service.get_article_by_id(session=session, article_id=article_id)


@router.post("/",
             response_model=Article
             )
@authorization.require_role("admin")
async def create_article(article_in: ArticleCreate,
                         articles_service: ArticleService = Depends(get_articles_service),
                         x_access_token: str = Header(None),
                         auth_service: AuthenticationService = Depends(get_authentication_service),
                         session: AsyncSession = Depends(get_session)
                     ):
    """Создает новую статью"""
    return await articles_service.create_article(session=session, article_in=article_in)


@router.put("/",
            response_model=Article
            )
@authorization.require_role("admin")
async def update_article(article_update: ArticleUpdate,
                         x_access_token: str = Header(None),
                         auth_service: AuthenticationService = Depends(get_authentication_service),
                         articles_service: ArticleService = Depends(get_articles_service),
                         session: AsyncSession = Depends(get_session)
                         ):
    """Обновляет существующую статью"""
    return await articles_service.update_article(session=session, article_update=article_update,
                                                 article_id=article_update.id)


@router.delete("/{article_id}",
               response_model=None,
               )
@authorization.require_role("admin")
async def delete_article(article_id: int,
                         x_access_token: str = Header(None),
                         auth_service: AuthenticationService = Depends(get_authentication_service),
                         articles_service: ArticleService = Depends(get_articles_service),
                         session: AsyncSession = Depends(get_session)):
    """Удаляет статью по её ID"""
    await articles_service.delete_article(session=session, article_id=article_id)
    return None
