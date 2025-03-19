import pytest
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from factory.declarations import Sequence
from factory.declarations import SubFactory

from app.users.models import FavoritePair
from app.users.models import User


@pytest.fixture
def user_factory(db_session):
    """User factory fixture."""
    class UserFactory(AsyncSQLAlchemyFactory):
        """User factory fixture."""

        class Meta:
            model = User
            sqlalchemy_session = db_session

        username = Sequence(lambda n: f'user{n}')  # type: ignore[no-untyped-call]
        password = 'hashed_password'  # noqa: S105

    return UserFactory


@pytest.fixture
def favorite_pair_factory(db_session, user_factory):
    """Favorite pair factory fixture."""
    class FavoritePairFactory(AsyncSQLAlchemyFactory):
        """Favorite pair factory fixture."""

        class Meta:
            model = FavoritePair
            sqlalchemy_session = db_session

        base = 'BTC'
        target = 'USD'
        user = SubFactory(user_factory)  # type: ignore[no-untyped-call]

    return FavoritePairFactory
