from typing import TypedDict
from urllib.parse import urljoin

import httpx

from app.config import settings
from app.core.exceptions import BaseClientError

ResponseDict = TypedDict('ResponseDict', {
    'success': str,
    'quotes': dict[str, float],
    'currencies': dict[str, str],
})


class ExchangerateClient:
    """The client for interaction with Exchangerate API."""

    class ClientError(BaseClientError):

        def __init__(self, message) -> None:
            self.message = message

    class UnknownClientError(BaseClientError):

        message = 'Unknown error from third party service.'

    def __init__(self) -> None:
        self.url = settings.EXCHANGERATE_URL.unicode_string()
        self.access_key = settings.EXCHANGERATE_ACCESS_KEY
        self._httpx_client = httpx.AsyncClient()

    async def __aenter__(self):
        """Return client instance."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close _httpx_client."""
        await self._httpx_client.aclose()

    async def _get(self, url: str, *, params=None) -> ResponseDict:
        """Send GET request."""
        if not params:
            params = {}
        params.update({'access_key': self.access_key})

        response = await self._httpx_client.get(url, params=params)
        response_data = response.json()

        try:
            if not response_data['success']:
                raise self.ClientError(message=response_data['error']['info'])
        except (KeyError, TypeError):
            raise self.UnknownClientError()

        return response_data

    async def get_available_currencies(self) -> dict[str, str]:
        """Get list of available currencies."""
        url = urljoin(self.url, 'list')
        response_data = await self._get(url)

        try:
            currencies = response_data['currencies']
        except KeyError:
            raise self.UnknownClientError()

        return currencies

    async def get_rate(self, *, base: str, target: str) -> dict[str, str | float]:
        """Get currency rate."""
        params = {
            'source': base,
            'currencies': target,
        }
        url = urljoin(self.url, 'live')
        response_data = await self._get(url, params=params)

        pair = base + target
        try:
            rate = response_data['quotes'][pair]
        except KeyError:
            raise self.UnknownClientError()

        return {'base': base, 'target': target, 'pair': pair, 'rate': rate}
