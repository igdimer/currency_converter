from app.core.exceptions import BaseServiceError
from app.redis import redis_client

from .clients import ExchangerateClient
from .schemas import RateOutput


class CurrencyService:
    """Service for working with currencies and converter."""

    class ExchangerateClientError(BaseServiceError):
        """Exception class for errors from ExchangerateClient."""

        def __init__(self, message) -> None:
            self.message = message

    class CurrencyNotAvailableError(BaseServiceError):
        """Provided currency is not available on external API."""

    def __init__(self) -> None:
        self.__available_currencies: dict[str, str] | None = None
        self._redis_client = redis_client

    async def get_available_currencies_from_external_api(self) -> dict[str, str]:
        """Get available currencies from Exchangerate API and save into cache."""
        client = ExchangerateClient()
        try:
            currencies = await client.get_available_currencies()
        except (ExchangerateClient.ClientError, ExchangerateClient.UnknownClientError) as exc:
            raise self.ExchangerateClientError(message=exc.message) from exc

        await self._redis_client.hset(
            'available_currencies',
            mapping=currencies,  # type: ignore[arg-type]
        )
        await self._redis_client.aclose()  # type: ignore[attr-defined]

        self.__available_currencies = currencies

        return currencies

    async def is_currency_available(self, *, code: str) -> bool:
        """Check whether currency is available."""
        upper_code = code.upper()

        currencies = self.__available_currencies
        if not currencies:
            currencies = await self._redis_client.hgetall('available_currencies')
            if not currencies:
                currencies = await self.get_available_currencies_from_external_api()
            await self._redis_client.aclose()  # type: ignore[attr-defined]

        result = upper_code in currencies

        return result

    async def get_rate(self, *, base: str, target: str):
        """Get currency rate."""
        for code in [base, target]:
            if not await self.is_currency_available(code=code):
                raise self.CurrencyNotAvailableError()

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
