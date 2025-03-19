from unittest import mock

import pytest
from sqlalchemy import select

from app.currency_converter.clients import ExchangerateClient
from app.currency_converter.schemas import CurrencyPair
from app.currency_converter.schemas import RateOutput
from app.currency_converter.services import CurrencyService
from app.redis import redis_client
from app.users.models import FavoritePair
from app.users.models import User


@pytest.mark.asyncio
class TestCurrencyServiceGetAvailableCurrencies:
    """Testing method get_available_currencies_from_external_api of CurrencyService."""

    async def test_success(self, mock_client_get_available_currencies):
        """Successful execution."""
        service = CurrencyService()
        assert service._available_currencies is None
        assert await service._redis_client.exists('available_currencies') == 0

        result = await service._get_available_currencies_from_external_api()
        expected_result = {
            'USD': 'United States Dollar',
            'AMD': 'Armenian Dram',
        }

        assert result == expected_result
        assert (await service._redis_client.hgetall('available_currencies')
                == expected_result)  # type: ignore
        assert service._available_currencies == expected_result

    @pytest.mark.parametrize('exc_class', [
        ExchangerateClient.ClientError,
        ExchangerateClient.UnknownClientError,
    ])
    async def test_client_error(self, mock_client_get_available_currencies, exc_class):
        """Client raises error."""
        service = CurrencyService()
        assert service._available_currencies is None
        assert await service._redis_client.exists('available_currencies') == 0

        mock_client_get_available_currencies.side_effect = exc_class('message')
        with pytest.raises(CurrencyService.ExchangerateClientError):
            await service._get_available_currencies_from_external_api()

        assert service._available_currencies is None
        assert await service._redis_client.exists('available_currencies') == 0


@pytest.mark.asyncio
class TestCurrencyServiceIsCurrencyAvailable:
    """Testing method is_currency_available of CurrencyService."""

    currencies_list = {
        'USD': 'United States Dollar',
        'AMD': 'Armenian Dram',
    }

    async def test_service_instance_has_attribute(self):
        """Instance of CurrencyService has attribute _available_currencies."""
        service = CurrencyService()
        service._available_currencies = self.currencies_list

        await service.is_currency_available(code='USD')

    async def test_currencies_in_redis(self):
        """No instance attribute _available_currencies, but redis has necessary hash."""
        await redis_client.hset(
            'available_currencies',
            mapping=self.currencies_list,  # type: ignore[arg-type]
        )
        service = CurrencyService()

        await service.is_currency_available(code='USD')

    async def test_no_saved_currencies(self, mock_client_get_available_currencies):
        """No saved currencies at all."""
        service = CurrencyService()
        await service.is_currency_available(code='USD')
        mock_client_get_available_currencies.assert_awaited_once()

    async def test_currency_not_available(
        self,
        mock_client_get_available_currencies,
    ):
        """Currency is not available."""
        service = CurrencyService()
        with pytest.raises(CurrencyService.CurrencyNotAvailableError):
            await service.is_currency_available(code='LOL')


@pytest.mark.asyncio
class TestCurrencyServiceGetRate:
    """Testing method get_rate of CurrencyService."""

    base = 'EUR'
    target = 'USD'

    async def test_success(
        self,
        mock_is_currency_available,
        mock_client_get_rate,
    ):
        """Successful execution."""
        service = CurrencyService()
        expected_result = RateOutput(
            pair=self.base + self.target,
            rate=0.55,
            description=f'1 {self.base} = 0.55 {self.target}',
        )

        assert await service.get_rate(base=self.base, target=self.target) == expected_result
        mock_is_currency_available.assert_any_await(code=self.base)
        mock_is_currency_available.assert_any_await(code=self.target)
        mock_client_get_rate.assert_awaited_once_with(base=self.base, target=self.target)

    async def test_currency_not_available(self, mock_is_currency_available):
        """Provided currency is not available."""
        mock_is_currency_available.side_effect = CurrencyService.CurrencyNotAvailableError()

        with pytest.raises(CurrencyService.CurrencyNotAvailableError):
            await CurrencyService().get_rate(base=self.base, target=self.target)

    @pytest.mark.parametrize('exc_class', [
        ExchangerateClient.ClientError,
        ExchangerateClient.UnknownClientError,
    ])
    async def test_client_error(
        self,
        mock_is_currency_available,
        mock_client_get_rate,
        exc_class,
    ):
        """ExchangerateClient raises error."""  # noqa: D403
        service = CurrencyService()
        mock_client_get_rate.side_effect = exc_class('message')

        with pytest.raises(CurrencyService.ExchangerateClientError):
            await service.get_rate(base=self.base, target=self.target)


@pytest.mark.asyncio
class TestCurrencyServiceCreateFavoriteList:
    """Testing method create_favorite_list of CurrencyService."""

    default_pairs = [
        CurrencyPair(base='USD', target='AMD'),
        CurrencyPair(base='GEL', target='USD'),
    ]

    async def test_success(self, db_session, mock_is_currency_available, user_factory):
        """Successful creation."""
        user = await user_factory()

        await CurrencyService().add_favorite_list(
            user=user,
            db_session=db_session,
            pairs=self.default_pairs,
        )

        result = await db_session.execute(select(FavoritePair).where(User.username == 'user0'))
        pairs = result.scalars().all()
        pair1 = pairs[0]
        pair2 = pairs[1]

        assert pair1.base == 'USD'
        assert pair1.target == 'AMD'
        assert pair1.user_id == user.id

        assert pair2.base == 'GEL'
        assert pair2.target == 'USD'
        assert pair2.user_id == user.id

    async def test_currency_not_available(
        self,
        db_session,
        mock_is_currency_available,
        user_factory,
    ):
        """Provided currency is not available."""
        user = await user_factory()
        mock_is_currency_available.side_effect = CurrencyService.CurrencyNotAvailableError()

        with pytest.raises(CurrencyService.CurrencyNotAvailableError):
            await CurrencyService().add_favorite_list(
                user=user,
                db_session=db_session,
                pairs=self.default_pairs,
            )

    async def test_create_duplicate_pair(
        self,
        db_session,
        mock_is_currency_available,
        user_factory,
        favorite_pair_factory,
    ):
        """User already has provided favorite pair."""
        user = await user_factory()
        await favorite_pair_factory(user=user, base='USD', target='AMD')

        await CurrencyService().add_favorite_list(
            user=user,
            db_session=db_session,
            pairs=self.default_pairs,
        )

        result = await db_session.execute(select(FavoritePair).where(User.username == 'user0'))
        pairs = result.scalars().all()
        pair1 = pairs[0]
        pair2 = pairs[1]

        assert len(pairs) == 2

        assert pair1.base == 'USD'
        assert pair1.target == 'AMD'
        assert pair1.user_id == user.id

        assert pair2.base == 'GEL'
        assert pair2.target == 'USD'
        assert pair2.user_id == user.id


@pytest.mark.asyncio
class TestCurrencyServiceGetFavoritePairs:
    """Testing method get_favorite_list of CurrencyService."""

    async def test_success(
        self,
        db_session,
        favorite_pair_factory,
        user_factory,
        mock_client_get_rate,
    ):
        """Succesful execution with single user."""
        user = await user_factory()
        await favorite_pair_factory(user=user)
        mock_client_get_rate.return_value = {
            'base': 'BTC',
            'target': 'USD',
            'pair': 'BTCUSD',
            'rate': 40000,
        }

        result = await CurrencyService().get_favorite_rates(user=user, db_session=db_session)
        pair = result[0]

        assert mock_client_get_rate.call_count == 1
        mock_client_get_rate.assert_awaited_with(base='BTC', target='USD')

        assert pair.pair == 'BTCUSD'
        assert pair.rate == 40000
        assert pair.description == '1 BTC = 40000 USD'

    async def test_another_user_has_pairs(
        self,
        db_session,
        favorite_pair_factory,
        user_factory,
        mock_client_get_rate,
    ):
        """Another user has favorite pair."""
        mock_client_get_rate.side_effect = [
            {'base': 'USD', 'target': 'AMD', 'pair': 'USDAMD', 'rate': 400.0},
            {'base': 'GEL', 'target': 'USD', 'pair': 'GELUSD', 'rate': 0.38},
        ]
        await favorite_pair_factory()
        user = await user_factory()
        await favorite_pair_factory(user=user, base='USD', target='AMD')
        await favorite_pair_factory(user=user, base='GEL', target='USD')

        result = await CurrencyService().get_favorite_rates(user=user, db_session=db_session)
        pair1 = result[0]
        pair2 = result[1]

        assert mock_client_get_rate.call_count == 2
        mock_client_get_rate.assert_has_awaits([
            mock.call(base='USD', target='AMD'),
            mock.call(base='GEL', target='USD'),
        ])

        assert pair1.pair == 'USDAMD'
        assert pair1.rate == 400.0
        assert pair1.description == '1 USD = 400.0 AMD'

        assert pair2.pair == 'GELUSD'
        assert pair2.rate == 0.38
        assert pair2.description == '1 GEL = 0.38 USD'

    async def test_no_favorite_list(self, db_session, user_factory, mock_client_get_rate):
        """User has no favorite rates list."""
        user = await user_factory()
        result = await CurrencyService().get_favorite_rates(user=user, db_session=db_session)

        mock_client_get_rate.assert_not_awaited()
        assert not result

    @pytest.mark.parametrize('exc_class', [
        ExchangerateClient.ClientError,
        ExchangerateClient.UnknownClientError,
    ])
    async def test_cleint_error(
        self,
        db_session,
        user_factory,
        favorite_pair_factory,
        mock_client_get_rate,
        exc_class,
    ):
        """Clien raises error."""
        mock_client_get_rate.side_effect = exc_class('message')
        user = await user_factory()
        await favorite_pair_factory(user=user)

        with pytest.raises(CurrencyService.ExchangerateClientError):
            await CurrencyService().get_favorite_rates(user=user, db_session=db_session)
