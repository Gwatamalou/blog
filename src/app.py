from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from config import logger

from src.repositories import db, Base
from src.routing import router as article_router


@logger.catch
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    yield

app = FastAPI(lifespan=lifespan)
app.include_router(article_router)



@app.get("")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run("src.app:app", host="localhost", port=8000)