from typing import Annotated

from fastapi import APIRouter, Query

from .clients import ExchangerateClient
from .schemas import RateOutput


converter_router = APIRouter()


@converter_router.get('/rate', response_model=RateOutput)
async def get_rate(
    base: Annotated[str, Query(max_length=3)],
    target: Annotated[str, Query(max_length=3)],
):
    """Get currency rate."""
    client = ExchangerateClient()
    rate = await client.get_rate(base, target)

    return RateOutput(
        pair=base + target,
        rate=rate,
        description=f'1 {base} = {rate} {target}',
    )
