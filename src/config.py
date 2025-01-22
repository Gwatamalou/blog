from pydantic import BaseModel
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


logger.add(
    "log.log",
    format="{time} {level} {message}",
    level="DEBUG",
    rotation="100 MB",
    compression="zip",
)

class DbSettings(BaseModel):
    url: str = f"postgresql+asyncpg://{os.getenv("DB_LOGIN")}:{os.getenv("DB_PASSWORD")}@localhost:5432/blog"
    echo: bool = True


class AuthJWT:
    PRIVATE_JWT: str = os.getenv("PRIVATE_JWT")
    PUBLIC_JWT: str = os.getenv("PUBLIC_JWT")
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TIMEDELTA: int = os.getenv("ACCESS_TIMEDELTA")
    REFRESH_TIMEDELTA: int = os.getenv("REFRESH_TIMEDELTA")


class Settings(BaseSettings):
    db: DbSettings = DbSettings()
    auth_jwt: AuthJWT = AuthJWT()



auth_jwt = AuthJWT()
settings = Settings()