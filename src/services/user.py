from src.repositories.model import User
from src.schemas import UserOut
from src.schemas.users import UserIn
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from sqlalchemy import select
from ..config import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@logger.catch
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def create_user(user_in: UserIn, session: AsyncSession):
    user_in.password = get_password_hash(user_in.password)
    new_user = User(**user_in.model_dump(by_alias=True))

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


@logger.catch
async def get_users(session: AsyncSession) -> list[UserOut] | None:
    stmt = select(User).order_by(User.uuid)
    res = await session.execute(stmt)
    users = res.scalars().all()
    return list(users)


@logger.catch
async def get_user(session, username) -> UserOut:
    stmt = select(User).where(User.name == username)
    user = await session.execute(stmt)
    user = user.scalars().first()

    return user
