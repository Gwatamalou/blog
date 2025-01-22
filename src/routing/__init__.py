from  fastapi import APIRouter

from .articles import router as article_router
from .auth import router as auth_router
from .users import router as users_router

router = APIRouter()
router.include_router(article_router, prefix="/article")
router.include_router(auth_router, prefix="/auth")
router.include_router(users_router, prefix="/users")