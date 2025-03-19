from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.models import BaseModel


class User(BaseModel):
    """User model class."""

    __tablename__ = 'user'

    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(64), nullable=False)

    favorite_pairs = relationship('FavoritePair', back_populates='user')


class FavoritePair(BaseModel):
    """Model class for storing users favorite pairs."""

    __tablename__ = 'favorite_pair'

    user_id = Column(
        BigInteger,
        ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    base = Column(String(3), nullable=False)
    target = Column(String(3), nullable=False)

    user = relationship('User', back_populates='favorite_pairs')

    __table_args__ = (
        UniqueConstraint('user_id', 'base', 'target'),
    )
