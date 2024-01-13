import asyncio
from unittest import mock

import httpx
import pytest
import pytest_asyncio

from app.redis import redis_client


@pytest.fixture(scope='module')
def event_loop():
    """Event loop fixture."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
async def setup_method():  # noqa: PT004
    """Clear redis cache before tests."""
    await redis_client.flushdb()


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
async def mock_client_get():
    """Mock fixture of method ExchangerateClient._get()."""
    with mock.patch(
        'app.currency_converter.clients.ExchangerateClient._get',
        return_value={
            'success': True,
            'quotes': {'USDEUR': 1.278342},
        },
    ) as method:
        yield method


@pytest_asyncio.fixture
async def mock_client_get_rate():
    """Mock fixture of method ExchangerateClient.get_rate()."""
    with mock.patch(
        'app.currency_converter.services.ExchangerateClient.get_rate',
        return_value=0.55,
    ) as method:
        yield method


@pytest_asyncio.fixture
async def mock_client_get_available_currencies():
    """Mock fixture of method ExchangerateClient.get_available_currencies()."""
    with mock.patch(
        'app.currency_converter.services.ExchangerateClient.get_available_currencies',
        return_value={
            'USD': 'United States Dollar',
            'AMD': 'Armenian Dram',
        },
    ) as method:
        yield method
