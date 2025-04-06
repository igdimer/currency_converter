from typing import Annotated

from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends

from app.database import DataBaseSession

from . import exceptions
from .responses import InvalidToken
from .responses import Unauthorized
from .responses import UserAlreadyExists
from .responses import UserNotFound
from .schemas import TokensOutput
from .services import AuthService

users_router = APIRouter(prefix='/users', tags=['Users'])


@users_router.post(
    '/signup',
    response_model=TokensOutput,
    responses={
        409: {'model': UserAlreadyExists, 'description': 'User already exists'},
    },
)
async def signup(
    db_session: DataBaseSession,
    username: Annotated[str, Body()],
    password: Annotated[str, Body()],
    service: AuthService = Depends(),
):
    """Registration on service."""
    try:
        tokens = await service.signup(
            username=username,
            password=password,
            db_session=db_session,
        )
    except AuthService.UserAlreadyExists as exc:
        raise exceptions.UserAlreadyExistsError from exc

    return tokens


@users_router.post(
    '/login',
    response_model=TokensOutput,
    responses={
        401: {'model': Unauthorized, 'description': 'Authentication failed'},
        404: {'model': UserNotFound, 'description': 'User was not found'},
    },
)
async def login(
    db_session: DataBaseSession,
    username: Annotated[str, Body()],
    password: Annotated[str, Body()],
    service: AuthService = Depends(),
):
    """Login and get tokens."""
    try:
        tokens = await service.login(
            username=username,
            password=password,
            db_session=db_session,
        )
    except AuthService.UserNotFoundError as exc:
        raise exceptions.UserNotFoundError from exc
    except AuthService.Unauthorized as exc:
        raise exceptions.UnauthorizedError from exc

    return tokens


@users_router.post(
    '/refresh_token',
    response_model=TokensOutput,
    responses={
        401: {'model': InvalidToken, 'description': 'Invalid refresh token'},
        404: {'model': UserNotFound, 'description': 'User was not found'},
    },
)
async def refresh_tokens(
    db_session: DataBaseSession,
    refresh_token: Annotated[str, Body(embed=True)],
    service: AuthService = Depends(),
):
    """Refresh tokens by refresh token."""
    try:
        tokens = await service.refresh_token(
            refresh_token=refresh_token,
            db_session=db_session,
        )
    except AuthService.InvalidTokenError as exc:
        raise exceptions.InvalidToken() from exc
    except AuthService.UserNotFoundError as exc:
        raise exceptions.UserNotFoundError() from exc

    return tokens
