from typing import TypedDict
from urllib.parse import urljoin

import httpx

from app.config import settings

ResponseDict = TypedDict('ResponseDict', {
    'success': str,
    'quotes': dict[str, float],
})


class BaseClientException(Exception):
    pass


class ExchangerateClient:
    """The client for interaction with exchangerate.host API."""

    class ClientError(BaseClientException):

        def __init__(self, message):
            self.message = message

    class UnknownClientError(BaseClientException):

        message = 'Unknown error'

    def __init__(self) -> None:
        self.url = settings.EXCHANGERATE_URL
        self.access_key = settings.EXCHANGERATE_ACCESS_KEY

    async def _get(self, url, params=None) -> ResponseDict:
        """Send GET request."""
        if not params:
            params = {'access_key': self.access_key}
        else:
            params.update({'access_key': self.access_key})

        async with httpx.AsyncClient() as session:
            response = await session.get(url, params=params)
        response_data = response.json()

        if response_data['success'] != 'true':
            try:
                message = response_data['error']['info']
            except KeyError:
                raise self.UnknownClientError()
            raise self.ClientError(message=message)

        return response_data

    async def get_rate(self, base: str, target: str):
        """Get currency rate."""
        params = {
            'source': base,
            'currencies': target,
        }
        url = urljoin(str(self.url), 'live')
        response_data = await self._get(url, params=params)

        pair = base + target
        try:
            rate = response_data['quotes'][pair]
        except KeyError:
            raise self.UnknownClientError()

        return rate