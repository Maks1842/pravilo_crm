from typing import AsyncGenerator

from sqlalchemy import Column, String, Integer, Boolean, TIMESTAMP, ForeignKey
from datetime import datetime

from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# Base: DeclarativeMeta = declarative_base()


class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTable[int], Base):
    id = Column(Integer, primary_key=True)
    username = Column(String(20), nullable=False, unique=True)
    hashed_password: str = Column(String(length=1024), nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
    last_name = Column(String(length=20), nullable=False)
    first_name = Column(String(length=50), nullable=False)
    birthday = Column(TIMESTAMP)
    date_registered = Column(TIMESTAMP, default=datetime.utcnow)
    email: str = Column(String(length=320), unique=True, index=True, nullable=False)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_verified: bool = Column(Boolean, default=False, nullable=False)


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)