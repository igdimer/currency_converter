from starlette import status

from app.core.exceptions import CustomApiError


class UserAlreadyExistsError(CustomApiError):
    """User with provided username already exists."""

    detail = 'The username is already in use.'
    status_code = status.HTTP_409_CONFLICT


class UserNotFoundError(CustomApiError):
    """No user with provided username."""

    detail = 'No user with provided username.'
    status_code = status.HTTP_404_NOT_FOUND


class UnauthorizedError(CustomApiError):
    """Authentication failed."""

    detail = 'Authentication failed.'
    status_code = status.HTTP_401_UNAUTHORIZED


class InvalidToken(CustomApiError):
    """Invalid token was provided."""

    detail = 'Invalid token was provided.'
    status_code = status.HTTP_401_UNAUTHORIZED
