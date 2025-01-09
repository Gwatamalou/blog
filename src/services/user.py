from src.repositories.model import User, Article
from src.schemas.auth import UserIn, UserOut
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from sqlalchemy import select
from ..config import logger


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@logger.catch
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

@logger.catch
async def create_user(user_in: UserIn, session: AsyncSession) -> User | None:
        user_in.password = get_password_hash(user_in.password)
        new_user = User(**user_in.model_dump())
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user

@logger.catch
async def get_users(session: AsyncSession):
        stmt = select(User).order_by(User.uuid)
        res = await session.execute(stmt)
        users = res.scalars().all()
        return list(users)

@logger.catch
async def get_user(session, username) -> User:
    stmt = select(User).where(User.name == username)
    user = await session.execute(stmt)
    user = user.scalars().first()

    return user