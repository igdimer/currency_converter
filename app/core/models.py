import datetime

from sqlalchemy import BigInteger, Column, DateTime
from sqlalchemy.orm import configure_mappers

from app.database import Base


class BaseModel(Base):
    """Base model class."""

    __abstract__ = True

    id = Column(BigInteger, primary_key=True)
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.datetime.now,
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
        nullable=False,
    )


configure_mappers()
