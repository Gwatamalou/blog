from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession

from src.depends import get_session, get_users_service, get_authentication_service
from src.schemas import UserOut
from src.services import UserService, AuthenticationService
router = APIRouter(tags=["user"])




@router.get("/all")
async def get_users(x_access_token: str = Header(None),
                       users_service: UserService = Depends(get_users_service),
                       auth_service: AuthenticationService = Depends(get_authentication_service),
                       session: AsyncSession = Depends(get_session),
                   ) -> list[UserOut]:
    return await users_service.get_users(session=session)

@router.get("/{name}")
async def get_user(name: str,
                   x_access_token: str = Header(None),
                   users_service: UserService = Depends(get_users_service),
                   auth_service: AuthenticationService = Depends(get_authentication_service),
                   session: AsyncSession = Depends(get_session),
                   ):
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

