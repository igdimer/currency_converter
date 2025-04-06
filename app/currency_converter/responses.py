from pydantic import BaseModel


class BadRequest(BaseModel):

    detail: str = 'Bad request'


class CurrencyNotAvailable(BaseModel):

    detail: str = 'Provided currency is not available'


class FavoritePairsCreated(BaseModel):

    detail: str = 'Favorite currencies were saved'


class FavoritePairsDeleted(BaseModel):

    detail: str = 'Favorite currencies were deleted'
