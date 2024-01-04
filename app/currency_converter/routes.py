from typing import Annotated

from fastapi import APIRouter, Query

from .exceptions import ExchangerateApiError
from .schemas import RateOutput
from .services import CurrencyService


converter_router = APIRouter()


@converter_router.get('/rate', response_model=RateOutput)
async def get_rate(
    base: Annotated[str, Query(max_length=3)],
    target: Annotated[str, Query(max_length=3)],
):
    """Get currency rate."""
    service = CurrencyService()
    try:
        rate = await service.get_rate(base=base, target=target)
    except CurrencyService.ExchangerateClientError as exc:
        raise ExchangerateApiError(detail=exc.message) from exc

    return rate
