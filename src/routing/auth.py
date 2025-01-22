from fastapi import APIRouter, status, Depends, HTTPException, Header, Form
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from sqlalchemy.ext.asyncio import AsyncSession
from ..depends import get_authentication_service, get_session


from src.repositories.model import User

from ..schemas import UserOut, UserIn
from ..services import (
    get_users,
    get_current_user
)

router = APIRouter(tags=["auth"])

@router.post("/")
async def auth(user_data: OAuth2PasswordRequestForm = Depends(),
               auth_service = Depends(get_authentication_service),
               session: AsyncSession = Depends(get_session)
               ):
    user = await auth_service.verify_user(user_data=user_data, session=session)

    if user:
        access_token = await auth_service.create_access_token(data={"sub": str(user.uuid)})
        refresh_token = await auth_service.create_refresh_token(data={"sub": str(user.uuid)}, session=session)
        json_user_data = jsonable_encoder(user)

        return JSONResponse(
            headers={"X-Access-Token": access_token, "x-Refresh-Token": refresh_token},
            content=json_user_data
        )

    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@router.post("/register",
             response_model=UserOut,
             status_code=status.HTTP_201_CREATED,
             )
async def register(name: str = Form(...),
                   email: EmailStr = Form(...),
                   password: str = Form(...),
                   auth_service=Depends(get_authentication_service),
                   session: AsyncSession = Depends(get_session)
                   ):
    new_user = UserIn(name=name, email=email, password_hash=password)
    return await auth_service.create_new_user(user_in=new_user, session=session)



@router.post("/refresh")
async def refresh(
                x_refresh_token: str = Header(None),
                auth_service = Depends(get_authentication_service),
                session: AsyncSession = Depends(get_session)
                ):
    new_access_token = await auth_service.verify_refresh_token(refresh_token=x_refresh_token, session=session)
    return JSONResponse(
        headers={"X-Access-Token": new_access_token},
        content={"messages": "success"}
    )



@router.get("/protect")
async def protect(user: User = Depends(get_current_user)):
    return {"message": f"Hi {user.name}"}




#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@router.get("/users")
async def get_all_users(
        session: AsyncSession = Depends(get_session),
):
    return await get_users(session = session)