from unittest import mock

import pytest
import pytest_asyncio

from app.currency_converter.clients import ExchangerateClient
from app.currency_converter.schemas import RateOutput
from app.currency_converter.services import CurrencyService
from app.redis import redis_client


async def setup_module():
    """Clear redis cache before all tests in module."""
    await redis_client.flushdb()


class TestCurrencyServiceGetAvailableCurrencies:
    """Testing method get_available_currencies_from_external_api of CurrencyService."""

    async def test_success(
        self,
        mock_client_get_available_currencies,
        teardown_method,
    ):
        """Successful execution."""
        service = CurrencyService()
        assert service._available_currencies is None
        assert await service._redis_client.exists('available_currencies') == 0

        result = await service.get_available_currencies_from_external_api()
        expected_result = {
            'USD': 'United States Dollar',
            'AMD': 'Armenian Dram',
        }

        assert result == expected_result
        assert await service._redis_client.hgetall('available_currencies') == expected_result
        assert service._available_currencies == expected_result

    @pytest.mark.parametrize('exc_class', [
        ExchangerateClient.ClientError,
        ExchangerateClient.UnknownClientError,
    ])
    async def test_client_error(
        self,
        mock_client_get_available_currencies,
        teardown_method,
        exc_class,
    ):
        """ExchangerateClient raises error."""  # noqa: D403
        service = CurrencyService()
        assert service._available_currencies is None
        assert await service._redis_client.exists('available_currencies') == 0

        mock_client_get_available_currencies.side_effect = exc_class('message')
        with pytest.raises(CurrencyService.ExchangerateClientError):
            await service.get_available_currencies_from_external_api()

        assert service._available_currencies is None
        assert await service._redis_client.exists('available_currencies') == 0


class TestCurrencyServiceIsCurrencyAvailable:
    """Testing method is_currency_available of CurrencyService."""

    currencies_list = {
        'USD': 'United States Dollar',
        'AMD': 'Armenian Dram',
    }

    async def test_service_instance_has_attribute(self, teardown_method):
        """Instance of CurrencyService has attribute _available_currencies."""
        service = CurrencyService()
        service._available_currencies = self.currencies_list

        await service.is_currency_available(code='USD')

    async def test_currencies_in_redis(self, teardown_method):
        """No instance attribute _available_currencies, but redis has necessary hash."""
        await redis_client.hset(
            'available_currencies',
            mapping=self.currencies_list,  # type: ignore[arg-type]
        )
        service = CurrencyService()

        await service.is_currency_available(code='USD')

    async def test_no_saved_currencies(
        self,
        teardown_method,
        mock_client_get_available_currencies,
    ):
        """No saved currencies at all."""
        service = CurrencyService()
        await service.is_currency_available(code='USD')
        mock_client_get_available_currencies.assert_awaited_once()

    async def test_currency_not_available(
        self,
        teardown_method,
        mock_client_get_available_currencies,
    ):
        """Currency is not available."""
        service = CurrencyService()
        with pytest.raises(CurrencyService.CurrencyNotAvailableError):
            await service.is_currency_available(code='LOL')


class TestCurrencyServiceGetRate:
    """Testing method get_rate of CurrencyService."""

    base = 'EUR'
    target = 'USD'

    @classmethod
    async def teardown_class(cls):
        """Clear redis cache after tests in class."""
        await redis_client.flushdb()

    @pytest_asyncio.fixture
    async def mock_is_currency_available(self):
        """Mock fixture of method CurrencyService.is_currency_available()."""
        with mock.patch(
            'app.currency_converter.services.CurrencyService.is_currency_available',
            return_value=True,
        ) as method:
            yield method

    async def test_success(
        self,
        mock_is_currency_available,
        mock_client_get_rate,
        teardown_method,
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

    @pytest.mark.parametrize('exc_class', [
        ExchangerateClient.ClientError,
        ExchangerateClient.UnknownClientError,
    ])
    async def test_client_error(
        self,
        mock_is_currency_available,
        mock_client_get_rate,
        exc_class,
        teardown_method,
    ):
        """ExchangerateClient raises error."""  # noqa: D403
        service = CurrencyService()
        mock_client_get_rate.side_effect = exc_class('message')

        with pytest.raises(CurrencyService.ExchangerateClientError):
            await service.get_rate(base=self.base, target=self.target)
