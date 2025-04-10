from typing import Annotated
from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base

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


DataBaseSession = Annotated[AsyncSession, Depends(get_session)]
