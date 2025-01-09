from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from ..config import auth_jwt
from src.repositories import db
import jwt
from passlib.context import CryptContext
from .user import get_user
from src.repositories import Refresh
from dotenv import load_dotenv


load_dotenv()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def save_refresh_token(
    token: Refresh,
    session: AsyncSession = Depends(db.session_dependency)
):
        session.add(token)
        await session.commit()


async def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now() + timedelta(minutes=int(auth_jwt.ACCESS_TIMEDELTA))
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        auth_jwt.PRIVATE_JWT,
        algorithm=auth_jwt.ALGORITHM,
    )

    return encoded_jwt


async def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now() + + timedelta(days=int(auth_jwt.REFRESH_TIMEDELTA))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        auth_jwt.PRIVATE_JWT,
        algorithm=auth_jwt.ALGORITHM,
    )

    refresh_token = Refresh(
        user_id=to_encode["sub"],
        token=encoded_jwt,
        expires_at=expire
    )

    await save_refresh_token(refresh_token)

    return encoded_jwt



async def verify_user(user_data, session) -> bool:
    user = get_user(session, user_data.username)

    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect user or password")

    return True


async def verify_refresh_token(refresh_token: str,
                               session: AsyncSession = Depends(db.session_dependency())
):
    try:
        payload = jwt.decode(
            refresh_token,
            auth_jwt.PRIVATE_JWT,
            algorithms=auth_jwt.ALGORITHM,
        )
        user_name = payload.get("sub")
        if not user_name:
            raise HTTPException(status_code=401, detail="Could not validate")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

    try:
        token = await session.get(Refresh, {"token": refresh_token})

        if token is None or token.expires_at < datetime.now():
            raise HTTPException(status_code=401, detail="Token is expired or invalid")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    new_access_token = create_access_token(data={"sub": user_name})

    return {"access_token": new_access_token, "token_type": "bearer"}




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
            raise  credentials_exception
    except Exception as e:
        raise credentials_exception

    user = await get_user(session, user_name)

    if user is None:
        raise credentials_exception

    return user




