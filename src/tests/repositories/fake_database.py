import asyncio
import os
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import random
from src.repositories import Base, User, Article, Refresh
from src.schemas import AccessLevel
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()


class FakeDatabase:
    db_created = False

    def __init__(self):
        self.test_db_url = f"postgresql+asyncpg://{os.getenv('DB_LOGIN')}:{os.getenv('DB_PASSWORD')}@localhost:5432/test_db"
        self.admin_db_url = f"postgresql+asyncpg://{os.getenv('DB_LOGIN')}:{os.getenv('DB_PASSWORD')}@localhost:5432/postgres"

        self.engine = create_async_engine(self.test_db_url, echo=False)
        self.admin_engine = create_async_engine(self.admin_db_url, isolation_level="AUTOCOMMIT")

        self.test_session = async_sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)

    async def __create_test_database(self):
        async with self.admin_engine.begin() as conn:
            await conn.execute(text("DROP DATABASE IF EXISTS test_db"))
            await conn.execute(text("CREATE DATABASE test_db"))

    async def __create_schemas_database(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def __populate_database(self):
        async with self.test_session() as session:
            users = [
                User(
                    uuid=uuid4(),
                    name=f"User{i + 1}",
                    email=f"user{i + 1}@example.com",
                    password_hash="password",
                    role=random.choice([AccessLevel.user, AccessLevel.admin]),
                    created_at=datetime.now(),
                    deleted_at=None if random.random() > 0.1 else datetime.now()
                )
                for i in range(10)
            ]
            session.add_all(users)
            await session.commit()

            user_ids = [user.uuid for user in users]

            articles = [
                Article(
                    title=f"Article {i + 1}",
                    text=f"Text {i + 1}",
                    author_id=random.choice(user_ids),
                    rating=round(random.uniform(1.0, 5.0), 2),
                    created_at=datetime.now(),
                    updated_at=None if random.random() > 0.3 else datetime.now()
                )
                for i in range(10)
            ]
            session.add_all(articles)
            await session.commit()

            refresh_tokens = [
                Refresh(
                    user_uuid=user.uuid,
                    token=str(uuid4()),
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(days=30)
                )
                for user in users
            ]
            session.add_all(refresh_tokens)
            await session.commit()

    async def init_test_database(self):
        if self.db_created is False:
            await self.__create_test_database()
            await self.__create_schemas_database()
            await self.__populate_database()
            self.db_created = True

    async def drop_test_database(self):
        async with self.admin_engine.begin() as conn:
            await conn.execute(text("DROP DATABASE IF EXISTS test_db"))
            self.db_created = False
