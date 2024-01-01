from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

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
    try:
        rate = await client.get_rate(base, target)
    except (ExchangerateClient.ClientError, ExchangerateClient.UnknownClientError) as exc:
        raise HTTPException(status_code=400, detail=exc.message)

    return RateOutput(
        pair=base + target,
        rate=rate,
        description=f'1 {base} = {rate} {target}',
    )
