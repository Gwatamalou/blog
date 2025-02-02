from datetime import datetime, timedelta
from dotenv import load_dotenv
from functools import wraps
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import decode as jwt_decode, encode as jwt_encode, ExpiredSignatureError, PyJWTError
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import auth_jwt
from src.repositories import Refresh, AuthenticationRepository, User
from src.schemas import UserIn, UserOut
from uuid import UUID

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



class TokenService:

    @staticmethod
    async def create_token(data: dict, expires: datetime) -> str:
        if "sub" not in data:
            raise KeyError("Missing required key 'sub' in data")
        if data["sub"] is None:
            raise ValueError("Missing required value 'sub' in data")
        try:
            to_encode = data.copy()
            to_encode.update({"sub": str(data["sub"])})
            to_encode.update({"exp": expires})

            return jwt_encode(
                to_encode,
                auth_jwt.PRIVATE_JWT,
                algorithm=auth_jwt.ALGORITHM,
            )
        except PyJWTError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token access creating error",
            )

    @staticmethod
    async def decode_token(token: str, verify_exp: bool = True) -> dict:
        try:
            return jwt_decode(
                token,
                auth_jwt.PUBLIC_JWT,
                algorithms=[auth_jwt.ALGORITHM],
                options={"verify_exp": verify_exp},
            )
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except PyJWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e


class BaseAuthService:

    def __init__(self, repository: AuthenticationRepository):
        self.repository = repository

    async def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)


class RegistrationService(BaseAuthService):

    async def create_new_user(self, user_in: UserIn, session: AsyncSession) -> UserOut:
        user_in.password = await self.get_password_hash(user_in.password)
        new_user = User(**user_in.model_dump(by_alias=True))
        return await self.repository.create_new_user(new_user, session)


class AuthenticationService(BaseAuthService):
    def __init__(self, repository: AuthenticationRepository):
        super().__init__(repository)
        self.token_service = TokenService()

    async def verify_user(self, user_data, session: AsyncSession) -> UserOut:
        user = await self.repository.get_user_data(session=session, username=user_data.username)

        if not user or not await self.verify_password(user_data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Incorrect user or password")

        return UserOut.model_validate(user)

    async def create_access_token(self, data: dict) -> str:
        expires = datetime.now() + timedelta(minutes=int(auth_jwt.ACCESS_TIMEDELTA))
        encoded_jwt = await self.token_service.create_token(data=data, expires=expires)
        return encoded_jwt

    async def verify_access_token(self, access_token: str = Depends(oauth2_scheme)) -> UUID:
        payload = await self.token_service.decode_token(access_token)
        user_uuid = payload.get("sub")

        if user_uuid is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return UUID(user_uuid)

    async def save_refresh_token(self, token: Refresh, session: AsyncSession) -> None:
        await self.repository.save_refresh_token(token=token, session=session)

    async def create_refresh_token(self, data: dict, session: AsyncSession) -> str:
        expire = datetime.now() + timedelta(days=int(auth_jwt.REFRESH_TIMEDELTA))
        encoded_jwt = await self.token_service.create_token(data=data, expires=expire)

        refresh_token = Refresh(
            user_uuid=data['sub'],
            token=encoded_jwt,
            expires_at=expire,
        )

        await self.save_refresh_token(refresh_token, session)

        return encoded_jwt

    async def verify_refresh_token(self, refresh_token: str, session: AsyncSession) -> str:

        payload = await self.token_service.decode_token(refresh_token)
        user_uuid = payload.get("sub")

        if not user_uuid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate")

        try:
            token = await self.repository.get_refresh_token(user_uuid=user_uuid, session=session)

            if token is None or token.expires_at < datetime.now():
                raise HTTPException(status_code=401, detail="Token is expired or invalid")
        except ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        except PyJWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        return await self.create_access_token(data={"sub": user_uuid})


class AuthorizationService:

    @staticmethod
    def require_role(role):
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


authorization = AuthorizationService()
