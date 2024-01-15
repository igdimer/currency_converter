from fastapi import APIRouter, Depends
from app.database import DataBaseSession
from app.users.services import AuthenticateUser

from . import exceptions
from .schemas import RateOutput, FavoritePairList, CurrencyPair
from .services import CurrencyService

converter_router = APIRouter()


@converter_router.get('/rate', response_model=RateOutput)
async def get_rate(
    currency_pair: CurrencyPair = Depends(),
):
    """Get currency rate."""
    service = CurrencyService()
    try:
        rate = await service.get_rate(base=currency_pair.base, target=currency_pair.target)
    except CurrencyService.ExchangerateClientError as exc:
        raise exceptions.ExchangerateApiError(detail=exc.message) from exc
    except CurrencyService.CurrencyNotAvailableError as exc:
        raise exceptions.CurrencyNotAvailableError() from exc

    return rate


@converter_router.post('/favorite_rates')
async def create_favorite_pairs(
    user: AuthenticateUser,
    db_session: DataBaseSession,
    favorite_list: FavoritePairList,
):
    """Create list of favorite currency pairs."""
    try:
        await CurrencyService().create_favorite_list(
            user=user,
            db_session=db_session,
            pairs=favorite_list.pairs,
        )
    except CurrencyService.CurrencyNotAvailableError as exc:
        raise exceptions.CurrencyNotAvailableError from exc

    return {'detail': 'Favorite currencies were saved.'}
