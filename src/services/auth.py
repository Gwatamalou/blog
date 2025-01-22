from datetime import datetime, timedelta
from dotenv import load_dotenv
from functools import wraps
from passlib.context import CryptContext

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import ExpiredSignatureError, PyJWTError

from sqlalchemy.ext.asyncio import AsyncSession

from src.config import auth_jwt
from src.repositories import db, Refresh, AuthenticationRepository, User
from src.schemas import UserIn, UserOut
from .user import get_user
from uuid import UUID



load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



class TokenService:

    @staticmethod
    def create_token(data: dict, expires_delta: timedelta) -> str:
        to_encode = data.copy()
        to_encode.update({"exp": datetime.now() + expires_delta})
        return jwt.encode(
            to_encode,
            auth_jwt.PRIVATE_JWT,
            algorithm=auth_jwt.ALGORITHM,
        )

    @staticmethod
    def decode_token(token: str, verify_exp: bool = True) -> dict:
        try:
            return jwt.decode(
                token,
                auth_jwt.PUBLIC_JWT,
                algorithms=[auth_jwt.ALGORITHM],
                options={"verify_exp": verify_exp},
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
            )
        except jwt.PyJWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            ) from e




class UserService:

    def __init__(self, repository: AuthenticationRepository):
        self.repository = repository

    async def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)



class RegistrationService(UserService):

    async def create_new_user(self, user_in: UserIn, session: AsyncSession) -> UserOut:
        user_in.password = await self.get_password_hash(user_in.password)
        new_user = User(**user_in.model_dump(by_alias=True))
        return await self.repository.create_new_user(new_user, session)



class AuthenticationService(UserService, TokenService):

    async def verify_user(self, user_data: UserIn, session: AsyncSession) -> UserOut:
        user = await self.repository.get_user_data(session=session, username=user_data.username)

        if not user or not await self.verify_password(user_data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Incorrect user or password")

        return UserOut.model_validate(user)


    async def create_access_token(self, data: dict) -> str:
        encoded_jwt = self.create_token(data=data, expires_delta=timedelta(minutes=int(auth_jwt.ACCESS_TIMEDELTA)))
        to_encode = data.copy()

        expire = datetime.now() + timedelta(minutes=int(auth_jwt.ACCESS_TIMEDELTA))
        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            to_encode,
            auth_jwt.PRIVATE_JWT,
            algorithm=auth_jwt.ALGORITHM,
        )

        return encoded_jwt


    async def verify_access_token(self, access_token: str = Depends(oauth2_scheme)) -> UUID:

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                access_token,
                auth_jwt.PUBLIC_JWT,
                algorithms=[auth_jwt.ALGORITHM],
                options={"verify_exp": True}
            )
            user_uuid = payload.get("sub")
            if user_uuid is None:
                raise credentials_exception
            return UUID(user_uuid)
        except ExpiredSignatureError as e:
            raise credentials_exception
        except PyJWTError as e:
            raise credentials_exception



    async def save_refresh_token(self, token: Refresh, session: AsyncSession) -> None:
        await self.repository.save_refresh_token(token=token, session=session)


    async def  create_refresh_token(self, data: dict, session: AsyncSession) -> str:
        to_encode = data.copy()
        expire = datetime.now() + + timedelta(days=int(auth_jwt.REFRESH_TIMEDELTA))
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            auth_jwt.PRIVATE_JWT,
            algorithm=auth_jwt.ALGORITHM,
        )

        refresh_token = Refresh(
            user_uuid=to_encode["sub"],
            token=encoded_jwt,
            expires_at=expire,
        )

        await self.save_refresh_token(refresh_token, session)

        return encoded_jwt



    async def verify_refresh_token(self, refresh_token: str, session: AsyncSession) -> str:
        try:
            payload = jwt.decode(
                refresh_token,
                auth_jwt.PUBLIC_JWT,
                algorithms=auth_jwt.ALGORITHM,
                options={"verify_exp": True}
            )
            user_uuid = payload.get("sub")
            if not user_uuid:
                raise HTTPException(status_code=401, detail="Could not validate")
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))

        try:
            token = await self.repository.get_refresh_token(user_uuid=user_uuid, session=session)

            if token is None or token.expires_at < datetime.now():
                raise HTTPException(status_code=401, detail="Token is expired or invalid")
        except ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        except PyJWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        return await self.create_access_token(data={"sub": user_uuid})





def authorization(role):
    def wrapper(func):
        @wraps(func)
        async def inner(**kwargs):

            auth_service: AuthenticationService = kwargs['auth_service']
            auth_repository = AuthenticationRepository()
            x_access_token = kwargs['x_access_token']
            session: AsyncSession = kwargs['session']

            uuid = await auth_service.verify_access_token(x_access_token)
            user = await auth_repository.get_user_data(session=session, user_uuid=uuid)
            user_role = user.role.value

            if role == "user" and user_role not in ['user', 'admin', 'superuser']:
                raise HTTPException(status_code=401, detail="Unauthorized")

            if role == 'admin' and user_role not in ['admin', 'superuser']:
                raise HTTPException(status_code=401, detail="not enough rights")

            if role == 'superuser' and user_role not in ['superuser']:
                raise HTTPException(status_code=401, detail="not enough rights")

            return await func(**kwargs)
        return inner
    return wrapper



async def get_current_user(token: str = Depends(oauth2_scheme),
                           session: AsyncSession = Depends(db.session_dependency)
                           ):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            auth_jwt.PUBLIC_JWT,
            algorithms=[auth_jwt.ALGORITHM],
        )
        user_name = payload.get("sub")
        if user_name is None:
            raise credentials_exception
    except Exception as e:
        raise credentials_exception

    user = await get_user(session, user_name)

    if user is None:
        raise credentials_exception

    return user
