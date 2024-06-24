from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, declarative_base
from sqlalchemy.orm import sessionmaker

from config import config

DATABASE_URL = config.db_uri
Base: DeclarativeBase = declarative_base()

engine = create_async_engine(
    config.db_uri,
    echo=True,
)

sessionmaker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker() as session:
        yield session
