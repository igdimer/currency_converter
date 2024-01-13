from typing import Annotated

from fastapi import APIRouter, Body

from app.database import DataBaseSession

from . import exceptions
from .schemas import TokensOutput
from .services import AuthService

users_router = APIRouter()


@users_router.post('/signup', response_model=TokensOutput)
async def signup(
    db_session: DataBaseSession,
    username: Annotated[str, Body()],
    password: Annotated[str, Body()],
):
    """Registration on service."""
    try:
        tokens = await AuthService.signup(
            username=username,
            password=password,
            db_session=db_session,
        )
    except AuthService.UserAlreadyExists as exc:
        raise exceptions.UserAlreadyExistsError from exc

    return tokens


@users_router.post('/login', response_model=TokensOutput)
async def login(
    db_session: DataBaseSession,
    username: Annotated[str, Body()],
    password: Annotated[str, Body()],
):
    """Login and get tokens."""
    try:
        tokens = await AuthService.login(
            username=username,
            password=password,
            db_session=db_session,
        )
    except AuthService.UserNotFoundError as exc:
        raise exceptions.UserNotFoundError from exc
    except AuthService.Unauthorized as exc:
        raise exceptions.UnauthorizedError from exc

    return tokens


@users_router.post('/refresh_token', response_model=TokensOutput)
async def refresh_tokens(
    db_session: DataBaseSession,
    refresh_token: Annotated[str, Body(embed=True)],
):
    """Refresh tokens by refresh token."""
    try:
        tokens = await AuthService.refresh_token(
            refresh_token=refresh_token,
            db_session=db_session,
        )
    except AuthService.InvalidTokenError as exc:
        raise exceptions.InvalidToken() from exc
    except AuthService.UserNotFoundError as exc:
        raise exceptions.UserNotFoundError() from exc

    return tokens
