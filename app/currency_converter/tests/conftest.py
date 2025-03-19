import asyncio
from unittest import mock

import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings
from app.currency_converter.schemas import RateOutput
from app.database import Base
from app.redis import redis_client
from app.users.tests.factories import favorite_pair_factory  # noqa: F401
from app.users.tests.factories import user_factory  # noqa: F401

db_engine = create_async_engine(settings.DATABASE_TEST_DSN.unicode_string())

async_db_session = async_sessionmaker(db_engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope='session')
def event_loop():
    """Event loop fixture."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


async def create_all(engine) -> None:
    """Create test database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all(engine) -> None:
    """Delete test database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='module', autouse=True)
def migrate_db():
    """Create and delete database tables fixture."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_all(db_engine))
    del loop

    yield None

    loop = asyncio.get_event_loop()
    loop.run_until_complete(drop_all(db_engine))
    del loop


@pytest_asyncio.fixture()
async def db_session():
    """Database session fixture."""
    connection = await db_engine.connect()
    transaction = await connection.begin()
    session = async_db_session(bind=connection, join_transaction_mode='create_savepoint')

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()


@pytest_asyncio.fixture(autouse=True)
async def flush_redis():
    """Clear redis cache after each test."""
    yield None
    await redis_client.flushdb()


@pytest_asyncio.fixture
async def mock_httpx_client():
    """Mock fixture of httpx.AsyncClient."""
    with mock.patch(
            'app.currency_converter.clients.httpx.AsyncClient',
            new=mock.AsyncMock,
    ) as mock_client:
        mock_client.get = mock.AsyncMock(return_value=httpx.Response(
            status_code=200,
            json={
                'success': True,
                'quotes': {'USDEUR': 1.278342},
            },
        ))
        yield mock_client


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
        return_value={
            'base': 'EUR',
            'target': 'USD',
            'pair': 'EURUSD',
            'rate': 0.55,
        },
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


@pytest_asyncio.fixture
async def mock_is_currency_available():
    """Mock fixture of method CurrencyService.is_currency_available()."""
    with mock.patch(
        'app.currency_converter.services.CurrencyService.is_currency_available',
        return_value=True,
    ) as method:
        yield method


@pytest_asyncio.fixture
async def mock_currency_service_get_rate():
    """Mock fixture of method get_rate of CurrencyService."""
    with mock.patch(
        'app.currency_converter.routes.CurrencyService.get_rate',
        return_value=RateOutput(
            pair='BTCUSD',
            rate=40000,
            description='1 BTC = 40000 USD',
        ),
    ) as mock_service:
        yield mock_service
