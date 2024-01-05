from unittest import mock

import pytest_asyncio
import httpx


@pytest_asyncio.fixture
async def mock_httpx_client_get():
    """Mock fixture of method httpx.AsyncClient.get()."""
    with mock.patch(
            'app.currency_converter.clients.httpx.AsyncClient.get',
            return_value=httpx.Response(
                status_code=200,
                json={
                    'success': True,
                    'quotes': {'USDEUR': 1.278342},
                },
            ),
    ) as method:
        yield method


@pytest_asyncio.fixture
async def mock_exchangerate_client_get():
    """Mock fixture of method ExchangerateClient._get()."""
    with mock.patch(
            'app.currency_converter.clients.ExchangerateClient._get',
            return_value={
                'success': True,
                'quotes': {'USDEUR': 1.278342},
            },
    ) as method:
        yield method
