from urllib.parse import urljoin

import httpx
import pytest

from app.config import settings
from app.currency_converter.clients import ExchangerateClient

test_url = 'http://test-url'


class TestExchangerateClientGet:
    """Testing method _get of ExchangerateClient."""

    async def test_params_none(self, mock_httpx_client):
        """Call without provided params."""
        await ExchangerateClient()._get(test_url, client=mock_httpx_client)

        mock_httpx_client.get.assert_awaited_once_with(
            test_url,
            params={'access_key': settings.EXCHANGERATE_ACCESS_KEY},
        )

    async def test_params_provided(self, mock_httpx_client):
        """Call with provided params."""
        await ExchangerateClient()._get(
            test_url,
            client=mock_httpx_client,
            params={'test_param': 'test_value'},
        )

        mock_httpx_client.get.assert_awaited_once_with(
            test_url,
            params={'access_key': settings.EXCHANGERATE_ACCESS_KEY, 'test_param': 'test_value'},
        )

    async def test_successful_response(self, mock_httpx_client):
        """Successful response."""
        response = await ExchangerateClient()._get(test_url, client=mock_httpx_client)

        assert response == {
            'success': True,
            'quotes': {'USDEUR': 1.278342},
        }

    async def test_unsuccessful_response(self, mock_httpx_client):
        """Unsuccessful expected response."""
        mock_httpx_client.get.return_value = httpx.Response(
            status_code=200,
            json={
                'success': False,
                'error': {
                    'code': 404,
                    'info': 'User requested a resource which does not exist.',
                },
            },
        )

        with pytest.raises(ExchangerateClient.ClientError) as exc:
            await ExchangerateClient()._get(test_url, client=mock_httpx_client)
        assert exc.value.message == 'User requested a resource which does not exist.'

    @pytest.mark.parametrize('json', [
        {'success': False, 'wrong_key': 'wrong_value'},
        {'wrong_key': 'wrong_value'},
        {'success': False, 'error': {'wrong_key': 'wrong_value'}},
        {'success': False, 'error': 'wrong_value_structure'},
    ])
    async def test_wrong_json_response(self, mock_httpx_client, json):
        """Unsuccessful response with unexpected json."""
        mock_httpx_client.get.return_value = httpx.Response(
            status_code=200,
            json=json,
        )

        with pytest.raises(ExchangerateClient.UnknownClientError) as exc:
            await ExchangerateClient()._get(test_url, client=mock_httpx_client)
        assert exc.value.message == 'Unknown error from third party service.'


class TestExchangerateClientGetRate:
    """Testing method get_rate of ExchangerateClient."""

    base = 'USD'
    target = 'EUR'

    async def test_successful_response(self, mock_client_get, mock_httpx_client):
        """Successful response."""
        result = await ExchangerateClient().get_rate(base=self.base, target=self.target)
        assert result == 1.278342
        mock_client_get.assert_awaited_once_with(
            urljoin(settings.EXCHANGERATE_URL.unicode_string(), 'live'),
            client=mock_httpx_client,
            params={'source': self.base, 'currencies': self.target},
        )

    @pytest.mark.parametrize('json', [
        {'success': True, 'wrong_key': 'wrong_value'},
        {'success': True, 'quotes': {'wrong_key': 'wrong_value'}},
    ])
    async def test_wrong_json_response(self, mock_client_get, json):
        """Unsuccessful response with unexpected json."""
        mock_client_get.return_value = json
        with pytest.raises(ExchangerateClient.UnknownClientError) as exc:
            await ExchangerateClient().get_rate(base=self.base, target=self.target)
        assert exc.value.message == 'Unknown error from third party service.'

    @pytest.mark.parametrize('exc_class', [
        ExchangerateClient.ClientError,
        ExchangerateClient.UnknownClientError,
    ])
    async def test_exception_from_method_get(self, mock_client_get, exc_class):
        """Exception occurred in method _get."""
        mock_client_get.side_effect = exc_class('message')
        with pytest.raises(exc_class):
            await ExchangerateClient().get_rate(base=self.base, target=self.target)


class TestExchangerateClientGetAvailable:
    """Testing method get_available_currencies of ExchangerateClient."""

    async def test_successful_response(self, mock_client_get, mock_httpx_client):
        """Successful response."""
        mock_client_get.return_value = {
            'success': True,
            'currencies': {
                'USD': 'USD description',
                'EUR': 'EUR description',
            },
        }
        result = await ExchangerateClient().get_available_currencies()

        mock_client_get.assert_awaited_once_with(
            urljoin(settings.EXCHANGERATE_URL.unicode_string(), 'list'),
            client=mock_httpx_client,
        )
        assert result == {'USD': 'USD description', 'EUR': 'EUR description'}

    async def test_wrong_json_response(self, mock_client_get):
        """Unsuccessful response with unexpected json."""
        mock_client_get.return_value = {'wrong_key': 'wrong_value'}
        with pytest.raises(ExchangerateClient.UnknownClientError) as exc:
            await ExchangerateClient().get_available_currencies()
        assert exc.value.message == 'Unknown error from third party service.'

    @pytest.mark.parametrize('exc_class', [
        ExchangerateClient.ClientError,
        ExchangerateClient.UnknownClientError,
    ])
    async def test_exception_from_method_get(self, mock_client_get, exc_class):
        """Exception occurred in method _get."""
        mock_client_get.side_effect = exc_class('message')
        with pytest.raises(exc_class):
            await ExchangerateClient().get_available_currencies()
