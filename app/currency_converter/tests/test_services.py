import pytest

from app.currency_converter.clients import ExchangerateClient
from app.currency_converter.services import CurrencyService
from app.redis import redis_client


@pytest.fixture
async def setup_method():
    """Clear redis cache before tests."""
    await redis_client.flushdb()


@pytest.fixture
async def teardown_method():
    """Clear redis cache after tests."""
    await redis_client.flushdb()


class TestCurrencyServiceGetAvailableCurrencies:
    """Testing method get_available_currencies_from_external_api of CurrencyService."""

    @classmethod
    async def teardown_class(cls):
        """Clear redis cache after all tests in class."""
        await redis_client.flushdb()

    async def test_success(
        self,
        mock_client_get_available_currencies,
        setup_method,
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
        setup_method,
        exc_class,
    ):
        """ExchangerateClient raises error."""
        service = CurrencyService()
        assert service._available_currencies is None
        assert await service._redis_client.exists('available_currencies') == 0

        mock_client_get_available_currencies.side_effect = exc_class('message')
        with pytest.raises(CurrencyService.ExchangerateClientError):
            await service.get_available_currencies_from_external_api()

        assert service._available_currencies is None
        assert await service._redis_client.exists('available_currencies') == 0
