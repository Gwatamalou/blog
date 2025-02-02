from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories import db
from src.repositories import ArticleRepository, AuthenticationRepository, UserRepository
from src.services import ArticleService, AuthenticationService, UserService, RegistrationService, TokenService


async def get_session() -> AsyncSession:
    async for session in db.session_dependency():
        yield session


article_repository = ArticleRepository()
article_service = ArticleService(article_repository)
async def get_articles_service() -> ArticleService:
    return article_service


users_repository = UserRepository()
users_service = UserService(users_repository)
async def get_users_service() -> UserService:
    return users_service



authentication_repository = AuthenticationRepository()
authentication_service = AuthenticationService(authentication_repository)
async def get_authentication_service() -> AuthenticationService:
    return authentication_service


registration_service = RegistrationService(authentication_repository)
async def get_registration_service() -> RegistrationService:
    return registration_service


token_service = TokenService()
async def get_token_service() -> TokenService:
    return token_service