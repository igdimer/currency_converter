from pydantic import BaseModel


class UserAlreadyExists(BaseModel):

    detail: str = 'User already exists'


class UserNotFound(BaseModel):

    detail: str = 'User was not found'


class Unauthorized(BaseModel):

    detail: str = 'Authentication failed'


class InvalidToken(BaseModel):

    detail: str = 'Invalid token was provided'
