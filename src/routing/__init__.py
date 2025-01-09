from  fastapi import APIRouter

from .blog import router as article_router
from .auth import router as user_router

router = APIRouter()
router.include_router(article_router, prefix="/article")
router.include_router(user_router, prefix="/auth")