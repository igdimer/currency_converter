import datetime as dt
import hashlib
from typing import Annotated

import jwt
from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import BaseServiceError
from app.database import DataBaseSession

from .exceptions import UnauthorizedError
from .models import User


class AuthService:
    """Registration and authentication service."""

    class Unauthorized(BaseServiceError):
        """Unsuccessful authorization."""

    class UserAlreadyExists(BaseServiceError):
        """User with provided username already exists."""

    class InvalidTokenError(BaseServiceError):
        """Invalid token was provided."""

    class UserNotFoundError(BaseServiceError):
        """No user with provided username."""

    @classmethod
    async def _hash_password(cls, password: str) -> str:
        """Hash user password to save into database."""
        secret = settings.AUTH_SECRET
        string = secret + password
        hashed_password = hashlib.sha256(string.encode())

        return hashed_password.hexdigest()

    @classmethod
    async def _generate_jwt_tokens(cls, username: str) -> dict[str, str]:
        """Generate access and refresh tokens."""
        access_exp_time = (dt.datetime.now(tz=dt.timezone.utc)
                           + dt.timedelta(days=settings.ACCESS_TOKEN_LIFETIME_DAYS))
        refresh_exp_time = (dt.datetime.now(tz=dt.timezone.utc)
                            + dt.timedelta(days=settings.REFRESH_TOKEN_LIFETIME_DAYS))

        access_token = jwt.encode(
            {
                'username': username,
                'type': 'access',
                'exp': access_exp_time,
            },
            settings.JWT_TOKEN_SECRET,
            algorithm='HS256',
        )
        refresh_token = jwt.encode(
            {
                'username': username,
                'type': 'refresh',
                'exp': refresh_exp_time,
            },
            settings.JWT_TOKEN_SECRET,
            algorithm='HS256',
        )

        return {'access_token': access_token, 'refresh_token': refresh_token}

    @classmethod
    async def get_user(cls, *, username: str, db_session: AsyncSession) -> User:
        """Get user from database."""
        user = await db_session.scalar(select(User).where(User.username == username))
        if not user:
            raise cls.UserNotFoundError()

        return user

    @classmethod
    async def signup(
        cls,
        *,
        username: str,
        password: str,
        db_session: AsyncSession,
    ) -> dict[str, str]:
        """Signup with provided username and password and get tokens."""
        hashed_password = await cls._hash_password(password)
        try:
            user = User(username=username, password=hashed_password)
            db_session.add(user)
            await db_session.commit()
        except IntegrityError as exc:
            raise cls.UserAlreadyExists() from exc

        return await cls._generate_jwt_tokens(username)

    @classmethod
    async def login(
        cls,
        *,
        username: str,
        password: str,
        db_session: AsyncSession,
    ) -> dict[str, str]:
        """Log in and get tokens."""
        user = await cls.get_user(username=username, db_session=db_session)
        hashed_password = await cls._hash_password(password=password)
        if user.password != hashed_password:
            raise cls.Unauthorized()

        return await cls._generate_jwt_tokens(username)

    @classmethod
    async def refresh_token(
        cls,
        *,
        refresh_token: str,
        db_session: AsyncSession,
    ) -> dict[str, str]:
        """Update tokens by refresh token."""
        try:
            decoded = jwt.decode(refresh_token, settings.JWT_TOKEN_SECRET, algorithms=['HS256'])
        except jwt.InvalidTokenError as exc:
            raise cls.InvalidTokenError() from exc

        try:
            username: str = decoded['username']
            token_type: str = decoded['type']
        except KeyError as exc:
            raise cls.InvalidTokenError() from exc

        await cls.get_user(username=username, db_session=db_session)
        if token_type != 'refresh':  # noqa: S105
            raise cls.InvalidTokenError()

        return await cls._generate_jwt_tokens(username)

    @classmethod
    async def authenticate(
        cls,
        authorization: Annotated[str, Header()],
        db_session: DataBaseSession,
    ) -> User:
        """Authenticate user by access token."""
        access_token = authorization.split()[-1]
        try:
            decoded = jwt.decode(access_token, settings.JWT_TOKEN_SECRET, algorithms=['HS256'])
            username: str = decoded['username']
            user = await cls.get_user(username=username, db_session=db_session)
        except (jwt.InvalidTokenError, KeyError, cls.UserNotFoundError) as exc:
            raise UnauthorizedError from exc

        return user


AuthenticateUser = Annotated[User, Depends(AuthService.authenticate)]
