from fastapi import APIRouter
from fastapi import Depends

from app.database import DataBaseSession
from app.users.services import AuthenticateUser

from . import exceptions
from .schemas import CurrencyPair
from .schemas import FavoritePairList
from .schemas import RateOutput
from .services import CurrencyService

converter_router = APIRouter(tags=['Rates'])


@converter_router.get('/rate', response_model=RateOutput)
async def get_rate(
    currency_pair: CurrencyPair = Depends(),
    service: CurrencyService = Depends(),
):
    """Get currency rate."""
    try:
        rate = await service.get_rate(
            base=currency_pair.base,
            target=currency_pair.target,
        )
    except CurrencyService.ExchangerateClientError as exc:
        raise exceptions.ExchangerateApiError(detail=exc.message) from exc
    except CurrencyService.CurrencyNotAvailableError as exc:
        raise exceptions.CurrencyNotAvailableError() from exc

    return rate


@converter_router.post('/favorite_rates')
async def add_favorite_pairs(
    user: AuthenticateUser,
    db_session: DataBaseSession,
    favorite_list: FavoritePairList,
    service: CurrencyService = Depends(),
):
    """Add favorite currency pairs."""
    try:
        await service.add_favorite_list(
            user=user,
            db_session=db_session,
            pairs=favorite_list.pairs,
        )
    except CurrencyService.CurrencyNotAvailableError as exc:
        raise exceptions.CurrencyNotAvailableError from exc

    return {'detail': 'Favorite currencies were saved.'}


@converter_router.get('/favorite_rates', response_model=list[RateOutput])
async def get_favorite_pairs(
    user: AuthenticateUser,
    db_session: DataBaseSession,
    service: CurrencyService = Depends(),
):
    """Get currency rates from favorite list."""
    try:
        result = await service.get_favorite_rates(user=user, db_session=db_session)
    except CurrencyService.ExchangerateClientError as exc:
        raise exceptions.ExchangerateApiError(detail=exc.message) from exc

    return result


@converter_router.delete('/favorite_rates')
async def delete_favorite_pairs(
    user: AuthenticateUser,
    db_session: DataBaseSession,
    favorite_list: FavoritePairList,
    service: CurrencyService = Depends(),
):
    """Delete favorite currency pair."""
    result = await service.delete_favorite_pairs(
        user=user,
        db_session=db_session,
        pairs=favorite_list.pairs,
    )

    return {'detail': result}
