from sqlalchemy import String, Float, DateTime, ForeignKey, Enum as SqlAlchemyEnum
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column, relationship

from src.schemas import AccessLevel

from uuid import uuid4, UUID
from datetime import datetime



class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls):
        return f'{cls.__name__.lower()}s'


class User(Base):
    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4, unique=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[AccessLevel] = mapped_column(SqlAlchemyEnum(AccessLevel), nullable=False, default=AccessLevel.user)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(),  nullable=False)
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    articles = relationship("Article", back_populates="user")


class Article(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    text: Mapped[str] = mapped_column(String(10000), nullable=False)
    author_id: Mapped[UUID] = mapped_column(ForeignKey('users.uuid'), nullable=True)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    user = relationship("User", back_populates="articles")


class Refresh(Base):
    user_uuid: Mapped[UUID] = mapped_column(ForeignKey('users.uuid'), unique=True, primary_key=True, nullable=False)
    token: Mapped[str] = mapped_column(String(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

