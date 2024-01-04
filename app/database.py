from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.declarative import declarative_base

from .config import settings

engine = create_async_engine(
    settings.DATABASE_DSN.unicode_string(),
    echo=True,
)
async_session = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with async_session() as session:
        yield session


DataBaseSession = Annotated[AsyncGenerator, Depends(get_session)]
