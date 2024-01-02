from sqlalchemy import BigInteger, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from app.core.models import BaseModel


class User(BaseModel):
    """User model class."""

    __tablename__ = 'users'

    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(64), nullable=False)
    favorite_pairs = relationship('FavoritePair', back_populates='user')


class FavoritePair(BaseModel):
    """Model class for storing users favorite pairs."""

    __tablename__ = 'favorite_pairs'

    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'))
    user = relationship('User', back_populates='favorite_pairs')
