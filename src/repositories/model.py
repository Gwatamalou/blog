from sqlalchemy import String, Float, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from datetime import datetime




class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls):
        return f'{cls.__name__.lower()}s'


class User(Base):
    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4, unique=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)

    articles = relationship("Article", back_populates="user")


class Article(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    text: Mapped[str] = mapped_column(String(10000), nullable=False)
    author_id: Mapped[UUID] = mapped_column(ForeignKey('users.uuid'), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)

    user = relationship("User", back_populates="articles")


class Refresh(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.uuid'), nullable=False)
    token: Mapped[str] = mapped_column(String(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

