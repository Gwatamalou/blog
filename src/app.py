from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from sqlalchemy.exc import IntegrityError
from src.config import logger
from src.schemas import AccessLevel
from src.repositories import db, Base
from src.routing import router
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
from src.repositories import User
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

load_dotenv()


@logger.catch
@asynccontextmanager
async def lifespan(app: FastAPI):
    connection = psycopg2.connect(
        user=os.getenv("DB_LOGIN"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port="5432",
    )
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    try:
        with connection.cursor() as cursor:
            db_name = os.getenv("DB_NAME")
            cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
            if cursor.fetchone() is None:
                cursor.execute(f"CREATE DATABASE {db_name}")
                logger.info(f"Database '{db_name}' created successfully.")
            else:
                logger.info(f"Database '{db_name}' already exists.")
    finally:
        connection.close()

    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with db.session_factory() as session:
        try:
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            password_hash = pwd_context.hash(os.getenv("SUPERUSRPASSWORD"))
            superuser = User(
                name=os.getenv("SUPERUSERNAME"),
                email=os.getenv("SUPERUSEREMAIl"),
                password_hash=password_hash,
                role=AccessLevel.superuser
            )
            session.add(superuser)
            await session.commit()
            logger.info(f"superuser created: {os.getenv("SUPERUSERNAME"),} / {(os.getenv("SUPERUSRPASSWORD"))}/n{password_hash}")
        except IntegrityError:
            logger.info(f"superuser already exists")
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)


@app.get("",
         response_model=dict)
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run("src.app:app", host="localhost", port=8000)
