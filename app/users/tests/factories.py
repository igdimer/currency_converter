import factory
import pytest
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory

from app.users.models import FavoritePair, User


@pytest.fixture()
def user_factory(db_session):
    """User factory fixture."""
    class UserFactory(AsyncSQLAlchemyFactory):
        """User factory fixture."""

        class Meta:
            model = User
            sqlalchemy_session = db_session

        username = factory.Sequence(lambda n: f'user{n}')
        password = 'hashed_password'  # noqa: S105

    return UserFactory


@pytest.fixture()
def favorite_pair_factory(db_session, user_factory):
    """Favorite pair factory fixture."""
    class FavoritePairFactory(AsyncSQLAlchemyFactory):
        """User factory fixture."""

        class Meta:
            model = FavoritePair
            sqlalchemy_session = db_session

        base = 'BTC'
        target = 'USD'
        user = factory.SubFactory(user_factory)

    return FavoritePairFactory
