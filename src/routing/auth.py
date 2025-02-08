from fastapi import APIRouter, status, Depends, HTTPException, Header, Form
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from pydantic import EmailStr

from sqlalchemy.ext.asyncio import AsyncSession

from src.depends import get_session, get_authentication_service, get_registration_service
from src.schemas import UserOut, UserIn


router = APIRouter(tags=["auth"])

@router.post("/")
async def auth(user_data: OAuth2PasswordRequestForm = Depends(),
               authentication_service = Depends(get_authentication_service),
               session: AsyncSession = Depends(get_session)
               ):
        """Выполняет аутентификацию пользователя и возвращает токены доступа и обновления"""
        user = await authentication_service.verify_user(user_data=user_data, session=session)

        if user:
            access_token = await authentication_service.create_access_token(data={"sub": user.uuid})
            refresh_token = await authentication_service.create_refresh_token(data={"sub": user.uuid}, session=session)
            json_user_data = jsonable_encoder(user)
            return JSONResponse(
                headers={"X-Access-Token": access_token, "X-Refresh-Token": refresh_token},
                content=json_user_data
            )

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@router.post("/register",
             response_model=UserOut,
             status_code=status.HTTP_201_CREATED,
             )
async def register(name: str = Form(...),
                   email: EmailStr = Form(...),
                   password: str = Form(...),
                   registration_service=Depends(get_registration_service),
                   session: AsyncSession = Depends(get_session)
                   ):
    """ Регистрирует нового пользователя"""
    new_user = UserIn(name=name, email=email, password_hash=password)

    return await registration_service.create_new_user(user_in=new_user, session=session)


@router.post("/refresh")
async def refresh(
                x_refresh_token: str = Header(None),
                authentication_service = Depends(get_authentication_service),
                session: AsyncSession = Depends(get_session)
                ):
    """Обновляет access token с использованием refresh token"""
    if x_refresh_token is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    new_access_token = await authentication_service.verify_refresh_token(refresh_token=x_refresh_token, session=session)
    return JSONResponse(
        headers={"X-Access-Token": new_access_token},
        content={"messages": "success"}
    )