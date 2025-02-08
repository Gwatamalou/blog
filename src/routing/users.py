from fastapi import APIRouter, Depends, Header
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession
from ..config import logger
from src.depends import get_session, get_users_service, get_authentication_service
from src.schemas import UserOut
from src.services import UserService, AuthenticationService, authorization

router = APIRouter(tags=["users"])



@router.get("/users/all",
            response_model=list[UserOut])
@authorization.require_role("superuser")
async def get_users(x_access_token: str = Header(None),
                    auth_service: AuthenticationService = Depends(get_authentication_service),
                    users_service: UserService = Depends(get_users_service),
                    session: AsyncSession = Depends(get_session),
                    ):
    """
    Получает список всех пользователей
    Доступно только для пользователей с ролью "superuser"
    """
    logger.info('')
    return await users_service.get_users(session=session)


@router.get("/{name}")
async def get_user(name: str,
                   x_access_token: str = Header(None),
                   users_service: UserService = Depends(get_users_service),
                   auth_service: AuthenticationService = Depends(get_authentication_service),
                   session: AsyncSession = Depends(get_session),
                   ):
    """
    Получает информацию о пользователе по имени
    Если токен доступа предоставлен и совпадает с UUID пользователя, возвращается информация о владельце
    """
    user = await users_service.get_user(username=name, session=session)
    user_data = jsonable_encoder(user)
    if x_access_token:
        token_uuid = await auth_service.verify_access_token(x_access_token)
        if token_uuid == user.uuid:
            return JSONResponse(
                content={"user": user_data, "is_owner": True},
            )

    return JSONResponse(
        content={"user": user_data, "is_owner": False},
    )


