from pydantic import BaseModel


class UserAlreadyExists(BaseModel):
    """User already exists response."""

    detail: str = 'User already exists'


class UserNotFound(BaseModel):
    """User was not found response."""

    detail: str = 'User was not found'


class Unauthorized(BaseModel):
    """Unauthorized response."""

    detail: str = 'Authentication failed'


class InvalidToken(BaseModel):
    """Invalid token response."""

    detail: str = 'Invalid token was provided'
