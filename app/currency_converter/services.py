from app.core.exceptions import BaseServiceError
from app.redis import redis

from .clients import ExchangerateClient
from .schemas import RateOutput


class CurrencyService:
    """Service for working with currencies and converter."""

    class ExchangerateClientError(BaseServiceError):
        """Exception class for errors from ExchangerateClient."""

        def __init__(self, message) -> None:
            self.message = message

    def __init__(self) -> None:
        self.__available_currencies: dict[str, str] | None = None

    async def retrieve_available_currencies(self) -> dict[str, str]:
        """Get available currencies from Exchangerate API and save into cache."""
        client = ExchangerateClient()
        try:
            currencies = await client.get_available_currencies()
        except (ExchangerateClient.ClientError, ExchangerateClient.UnknownClientError) as exc:
            raise self.ExchangerateClientError(message=exc.message) from exc

        async with redis.client() as conn:
            await conn.hset('available_currencies', mapping=currencies)

        self.__available_currencies = currencies

        return currencies

    async def get_rate(self, *, base: str, target: str):
        """Get currency rate."""
        client = ExchangerateClient()
        try:
            rate = await client.get_rate(base=base, target=target)
        except (ExchangerateClient.ClientError, ExchangerateClient.UnknownClientError) as exc:
            raise self.ExchangerateClientError(message=exc.message) from exc

        return RateOutput(
            pair=base + target,
            rate=rate,
            description=f'1 {base} = {rate} {target}',
        )
