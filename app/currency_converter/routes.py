from typing import Annotated

from fastapi import APIRouter, Query

from . import exceptions
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
        raise exceptions.ExchangerateApiError(detail=exc.message) from exc
    except CurrencyService.CurrencyNotAvailableError as exc:
        raise exceptions.CurrencyNotAvailable() from exc

    return rate
