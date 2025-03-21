import datetime as dt
import hashlib
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi import Header
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

    async def _hash_password(self, password: str) -> str:
        """Hash user password to save into database."""
        secret = settings.AUTH_SECRET
        string = secret + password
        hashed_password = hashlib.sha256(string.encode())

        return hashed_password.hexdigest()

    async def _generate_jwt_tokens(self, username: str) -> dict[str, str]:
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

    async def get_user(self, *, username: str, db_session: AsyncSession) -> User:
        """Get user from database."""
        user = await db_session.scalar(select(User).where(User.username == username))
        if not user:
            raise self.UserNotFoundError()

        return user

    async def signup(
        self,
        *,
        username: str,
        password: str,
        db_session: AsyncSession,
    ) -> dict[str, str]:
        """Signup with provided username and password and get tokens."""
        hashed_password = await self._hash_password(password)
        try:
            user = User(username=username, password=hashed_password)
            db_session.add(user)
            await db_session.commit()
        except IntegrityError as exc:
            raise self.UserAlreadyExists() from exc

        return await self._generate_jwt_tokens(username)

    async def login(
        self,
        *,
        username: str,
        password: str,
        db_session: AsyncSession,
    ) -> dict[str, str]:
        """Log in and get tokens."""
        user = await self.get_user(username=username, db_session=db_session)
        hashed_password = await self._hash_password(password=password)
        if user.password != hashed_password:
            raise self.Unauthorized()

        return await self._generate_jwt_tokens(username)

    async def refresh_token(
        self,
        *,
        refresh_token: str,
        db_session: AsyncSession,
    ) -> dict[str, str]:
        """Update tokens by refresh token."""
        try:
            decoded = jwt.decode(refresh_token, settings.JWT_TOKEN_SECRET, algorithms=['HS256'])
        except jwt.InvalidTokenError as exc:
            raise self.InvalidTokenError() from exc

        try:
            username: str = decoded['username']
            token_type: str = decoded['type']
        except KeyError as exc:
            raise self.InvalidTokenError() from exc

        await self.get_user(username=username, db_session=db_session)
        if token_type != 'refresh':  # noqa: S105
            raise self.InvalidTokenError()

        return await self._generate_jwt_tokens(username)

    async def authenticate(
        self,
        authorization: Annotated[str, Header()],
        db_session: DataBaseSession,
    ) -> User:
        """Authenticate user by access token."""
        access_token = authorization.split()[-1]
        try:
            decoded = jwt.decode(access_token, settings.JWT_TOKEN_SECRET, algorithms=['HS256'])
            username: str = decoded['username']
            user = await self.get_user(username=username, db_session=db_session)
        except (jwt.InvalidTokenError, KeyError, self.UserNotFoundError) as exc:
            raise UnauthorizedError from exc

        return user


AuthenticateUser = Annotated[User, Depends(AuthService().authenticate)]
