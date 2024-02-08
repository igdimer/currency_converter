import asyncio

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BaseServiceError
from app.redis import redis_client
from app.users.models import FavoritePair, User

from .clients import ExchangerateClient
from .schemas import CurrencyPair, RateOutput


class CurrencyService:
    """Service for working with currencies and converter."""

    class ExchangerateClientError(BaseServiceError):
        """Exception class for errors from ExchangerateClient."""

        def __init__(self, message) -> None:
            self.message = message

    class CurrencyNotAvailableError(BaseServiceError):
        """Provided currency is not available on external API."""

    def __init__(self) -> None:
        self._available_currencies: dict[str, str] | None = None
        self._redis_client = redis_client

    async def _get_available_currencies_from_external_api(self) -> dict[str, str]:
        """Get available currencies from Exchangerate API and save into cache."""
        async with ExchangerateClient() as client:
            try:
                currencies = await client.get_available_currencies()
            except (ExchangerateClient.ClientError, ExchangerateClient.UnknownClientError) as exc:
                raise self.ExchangerateClientError(message=exc.message) from exc

        await self._redis_client.hset(
            'available_currencies',
            mapping=currencies,
        )
        await self._redis_client.aclose()  # type: ignore[attr-defined]

        self._available_currencies = currencies

        return currencies

    async def is_currency_available(self, *, code: str) -> None:
        """Check whether currency is available."""
        currencies = self._available_currencies
        if not currencies:
            currencies = await self._redis_client.hgetall('available_currencies')
            if not currencies:
                currencies = await self._get_available_currencies_from_external_api()
            await self._redis_client.aclose()  # type: ignore[attr-defined]

        if code not in currencies:
            raise self.CurrencyNotAvailableError()

    async def get_rate(self, *, base: str, target: str):
        """Get currency rate."""
        for code in [base, target]:
            await self.is_currency_available(code=code)

        async with ExchangerateClient() as client:
            try:
                result = await client.get_rate(base=base, target=target)
            except (ExchangerateClient.ClientError, ExchangerateClient.UnknownClientError) as exc:
                raise self.ExchangerateClientError(message=exc.message) from exc

        rate = result['rate']

        return RateOutput(
            pair=result['pair'],
            rate=rate,
            description=f'1 {base} = {rate} {target}',
        )

    async def add_favorite_list(
        self,
        *,
        user: User,
        db_session: AsyncSession,
        pairs: list[CurrencyPair],
    ):
        """Add favorite currency pairs."""
        pairs_dicts = []
        currencies_set = set()

        for pair in pairs:
            for currency_code in (pair.base, pair.target):

                if currency_code not in currencies_set:
                    await self.is_currency_available(code=currency_code)
                    currencies_set.add(currency_code)

            pairs_dicts.append({'user_id': user.id, 'base': pair.base, 'target': pair.target})

        await db_session.execute(insert(FavoritePair).on_conflict_do_nothing(), pairs_dicts)
        await db_session.commit()

    async def get_favorite_rates(self, *, user: User, db_session: AsyncSession):
        """Get currency rates from favorite list."""
        favorite_pairs = await db_session.scalars(
            select(FavoritePair).where(FavoritePair.user_id == user.id),
        )

        tasks = []
        async with ExchangerateClient() as client:
            for pair in favorite_pairs:
                tasks.append(client.get_rate(base=pair.base, target=pair.target))

            try:
                result_rates = await asyncio.gather(*tasks)
            except (ExchangerateClient.ClientError, ExchangerateClient.UnknownClientError) as exc:
                raise self.ExchangerateClientError(message=exc.message) from exc

        result = []
        for item in result_rates:
            rate = item['rate']
            base = item['base']
            target = item['target']

            result.append(RateOutput(
                pair=item['pair'],
                rate=rate,
                description=f'1 {base} = {rate} {target}',
            ))

        return result
