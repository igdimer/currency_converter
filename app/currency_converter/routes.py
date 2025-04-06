from fastapi import APIRouter
from fastapi import Depends

from app.database import DataBaseSession
from app.users.services import AuthenticateUser
from app.users.responses import Unauthorized

from app.core.utils import parse_query_parameters_as_list_int
from . import exceptions
from .schemas import CurrencyPair
from .schemas import FavoritePairListCreate
from .schemas import RateOutput, FavoritePairOutput
from .services import CurrencyService
from .responses import CurrencyNotAvailable, FavoritePairsCreated, BadRequest, FavoritePairsDeleted

converter_router = APIRouter(prefix='/currencies', tags=['Currencies'])


@converter_router.get(
    '/rate',
    response_model=RateOutput,
    responses={
        400: {'model': BadRequest},
    },
)
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


@converter_router.post(
    '/favorite_rates/create',
    responses={
        200: {'model': FavoritePairsCreated},
        400: {'model': CurrencyNotAvailable},
        401: {'model': Unauthorized, 'description': 'Authentication failed'},
    },
)
async def add_favorite_pairs(
    user: AuthenticateUser,
    db_session: DataBaseSession,
    favorite_list: FavoritePairListCreate,
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


@converter_router.get(
    '/favorite_rates',
    response_model=list[FavoritePairOutput],
    responses={
        400: {'model': BadRequest},
        401: {'model': Unauthorized, 'description': 'Authentication failed'},
    },
)
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


@converter_router.delete(
    '/favorite_rates/remove',
    responses={
        200: {'model': FavoritePairsDeleted},
        401: {'model': Unauthorized, 'description': 'Authentication failed'},
    },
)
async def delete_favorite_pairs(
    user: AuthenticateUser,
    db_session: DataBaseSession,
    favorite_list: list[int] = Depends(parse_query_parameters_as_list_int),
    service: CurrencyService = Depends(),
):
    """Delete favorite currency pair."""
    result = await service.delete_favorite_pairs(
        user=user,
        db_session=db_session,
        pairs=favorite_list,
    )

    return {'detail': result}
