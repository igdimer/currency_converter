from fastapi.testclient import TestClient

from app.currency_converter.services import CurrencyService
from app.main import app

client = TestClient(app)


class TestGetRate:
    """Test route /currencies/rate."""

    url = 'api/currencies/rate'
    params = {'base': 'BTC', 'target': 'USD'}

    def test_success(self, mock_currency_service_get_rate):
        """Successful response."""
        response = client.get(self.url, params=self.params)

        mock_currency_service_get_rate.assert_awaited_with(base='BTC', target='USD')
        assert response.status_code == 200
        assert response.json() == {
            'pair': 'BTCUSD',
            'rate': 40000,
            'description': '1 BTC = 40000 USD',
        }

    def test_exchangerate_client_error(self, mock_currency_service_get_rate):
        """Currency Service raises ExchangerateClientError."""
        mock_currency_service_get_rate.side_effect = CurrencyService.ExchangerateClientError(
            message='message',
        )
        response = client.get(self.url, params=self.params)
        assert response.status_code == 400
        assert response.json() == {
            'detail': 'message',
        }

    def test_currency_not_available(self, mock_currency_service_get_rate):
        """Currency Service raises CurrencyNotAvailableError."""
        mock_currency_service_get_rate.side_effect = CurrencyService.CurrencyNotAvailableError()
        response = client.get(self.url, params=self.params)
        assert response.status_code == 400
        assert response.json() == {
            'detail': 'Provided currency is not available.',
        }
