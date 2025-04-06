from pydantic import BaseModel


class BadRequest(BaseModel):
    """Bad request response."""

    detail: str = 'Bad request'


class CurrencyNotAvailable(BaseModel):
    """Currency is not available response."""

    detail: str = 'Provided currency is not available'


class FavoritePairsCreated(BaseModel):
    """Favorite pairs were created response."""

    detail: str = 'Favorite currencies were saved'


class FavoritePairsDeleted(BaseModel):
    """Favorite pairs were deleted response."""

    detail: str = 'Favorite currencies were deleted'
