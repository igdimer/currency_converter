import pytest

from app.currency_converter.clients import ExchangerateClient
from app.currency_converter.services import CurrencyService
from app.redis import redis_client


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

    @classmethod
    async def teardown_class(cls):
        """Clear redis cache after all tests in class."""
        await redis_client.flushdb()

    @pytest.mark.parametrize(('code', 'result'), [
        ('USD', True),
        ('usd', True),
        ('GBP', False),
        ('gbp', False),
    ])
    async def test_service_instance_has_attribute(self, setup_method, code, result):
        """Instance of CurrencyService has attribute _available_currencies."""
        service = CurrencyService()
        service._available_currencies = self.currencies_list

        assert await service.is_currency_available(code=code) is result

    @pytest.mark.parametrize(('code', 'result'), [
        ('USD', True),
        ('usd', True),
        ('GBP', False),
        ('gbp', False),
    ])
    async def test_currencies_in_redis(self, setup_method, code, result):
        """No instance attribute _available_currencies, but redis has necessary hash."""
        await redis_client.hset(
            'available_currencies',
            mapping=self.currencies_list,  # type: ignore[arg-type]
        )
        service = CurrencyService()

        assert await service.is_currency_available(code=code) is result

    @pytest.mark.parametrize(('code', 'result'), [
        ('USD', True),
        ('usd', True),
        ('GBP', False),
        ('gbp', False),
    ])
    async def test_no_saved_currencies(
        self,
        setup_method,
        code,
        result,
        mock_client_get_available_currencies,
    ):
        """No saved currencies at all."""
        service = CurrencyService()
        assert await service.is_currency_available(code=code) is result
        mock_client_get_available_currencies.assert_awaited_once()
