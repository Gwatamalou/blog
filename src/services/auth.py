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
    """
    Сервис для работы с JWT токенами.
    """

    @staticmethod
    async def create_token(data: dict, expires: datetime) -> str:
        """
        Создает JWT токен с заданными данными и временем истечения срока.

        :param data: Данные для токена (должен быть ключ 'sub' с UUID пользователя).
        :param expires: Время истечения токена.
        :return: Созданный токен в формате строки.
        :raises KeyError: Если в данных отсутствует ключ 'sub'.
        :raises ValueError: Если значение 'sub' отсутствует.
        :raises HTTPException: Если возникла ошибка при создании токена.
        """
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
        """
        Декодирует JWT токен и возвращает данные.

        :param token: JWT токен для декодирования.
        :param verify_exp: Проверять ли срок действия токена.
        :return: Декодированные данные из токена.
        :raises HTTPException: Если токен истек или невалиден.
        """
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
    """
    Базовый сервис для аутентификации, включающий операции с паролями.
    """

    def __init__(self, repository: AuthenticationRepository):
        """
        Инициализация базового сервиса аутентификации.

        :param repository: Репозиторий для работы с данными пользователей.
        """
        self.repository = repository

    async def get_password_hash(self, password: str) -> str:
        """ Генерирует хэш пароля"""
        return pwd_context.hash(password)

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """ Проверяет, совпадает ли введенный пароль с хэшированным"""
        return pwd_context.verify(plain_password, hashed_password)


class RegistrationService(BaseAuthService):
    """
    Сервис для регистрации пользователей.
    """

    async def create_new_user(self, user_in: UserIn, session: AsyncSession) -> UserOut:
        """Регистрирует нового пользователя в системе"""
        user_in.password = await self.get_password_hash(user_in.password)
        new_user = User(**user_in.model_dump(by_alias=True))
        return await self.repository.create_new_user(new_user, session)


class AuthenticationService(BaseAuthService):
    """
    Сервис для аутентификации пользователей и работы с токенами.
    """

    def __init__(self, repository: AuthenticationRepository):
        super().__init__(repository)
        self.token_service = TokenService()

    async def verify_user(self, user_data, session: AsyncSession) -> UserOut:
        """
        Проверяет данные пользователя (логин и пароль).

        :param user_data: Данные для аутентификации (username, password).
        :param session: Асинхронная сессия для работы с базой данных.
        :return: Данные пользователя, если аутентификация успешна.
        :raises HTTPException: Если данные пользователя некорректны.
        """
        user = await self.repository.get_user_data(session=session, username=user_data.username)

        if not user or not await self.verify_password(user_data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Incorrect user or password")

        return UserOut.model_validate(user)

    async def create_access_token(self, data: dict) -> str:
        """
         Создает новый токен доступа (JWT).
        """

        expires = datetime.now() + timedelta(minutes=int(auth_jwt.ACCESS_TIMEDELTA))
        encoded_jwt = await self.token_service.create_token(data=data, expires=expires)
        return encoded_jwt

    async def verify_access_token(self, access_token: str = Depends(oauth2_scheme)) -> UUID:
        """
        Проверяет и декодирует токен доступа, возвращая UUID пользователя.
        """
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
        """Сохраняет refresh токен в базе данных"""
        await self.repository.save_refresh_token(token=token, session=session)

    async def create_refresh_token(self, data: dict, session: AsyncSession) -> str:
        """Создает новый refresh токен и сохраняет его в базе данных"""
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
        """Проверяет refresh токен и создает новый access токен"""
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
    """
    Сервис для проверки ролей и авторизации пользователей.
    """
    @staticmethod
    def require_role(role):
        """
        Декоратор для проверки роли пользователя перед выполнением функции.

        :param role: Требуемая роль для доступа (например, "user", "admin", "superuser").
        :return: Функция с дополнительной логикой авторизации.
        """
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
