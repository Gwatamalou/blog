from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from watchfiles import awatch

from ..schemas.auth import UserOut, UserIn
from ..repositories import db, User
from ..services import (
    create_user,
    get_users,
    get_user,
    create_access_token,
    get_current_user,
    verify_refresh_token,
)
from ..config import auth_jwt
router = APIRouter(tags=["auth"])



@router.post("/register",
            response_model=UserOut,
            status_code=status.HTTP_201_CREATED
)
async def register(
        user_in: UserIn,
        session: AsyncSession = Depends(db.session_dependency),
):
    return await create_user(user_in = user_in, session = session)





@router.post("/")
async def auth(user_data: OAuth2PasswordRequestForm = Depends(),
               session: AsyncSession = Depends(db.session_dependency)
               ):
    user = await get_user(session, user_data.username)

    access_token = await create_access_token(data={"sub": str(user.name)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh")
async def refresh(refresh_token: str):
    return await verify_refresh_token(refresh_token)


@router.get("/protect")
async def protect(user: User = Depends(get_current_user)):
    return {"message": f"Hi {user.name}"}




#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@router.get("/users")
async def get_all_users(
        session: AsyncSession = Depends(db.session_dependency),
):
    return await get_users(session = session)