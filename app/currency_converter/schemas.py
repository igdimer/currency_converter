from pydantic import field_validator
from pydantic import model_validator

from app.core.schemas import BaseSchema

from .exceptions import CustomValidationError


class RateOutput(BaseSchema):
    """Response model for currency rate."""

    pair: str
    rate: float
    description: str


class FavoritePairOutput(BaseSchema):
    """Response model for favorite currency rate."""

    id: int
    pair: str
    rate: float
    description: str


class CurrencyPair(BaseSchema):
    """Schema for a pair of currencies."""

    base: str
    target: str

    @field_validator('base', 'target')
    @classmethod
    def code_upper(cls, value):
        """Return a copy of the string converted to uppercase."""
        return value.upper()

    @field_validator('base', 'target')
    @classmethod
    def length_validator(cls, value):
        """
        Check if length of provided code equals 3 letters.

        This validator and returning HTTPException instead Pydantic ValidationError is necessary
        because this schema is used for Query parameters as Depends.
        https://stackoverflow.com/a/75998823
        """
        if len(value) != 3:
            raise CustomValidationError(detail='Length of code must be equal 3 letters.')

        return value


class FavoritePairListCreate(BaseSchema):
    """Schema for creating favorite currency pairs."""

    pairs: list[CurrencyPair]

    @model_validator(mode='before')
    @classmethod
    def pairs_not_empty(cls, data):
        """Check provided pairs list is not empty."""
        if not data['pairs']:
            raise ValueError('Provided pairs list is empty.')

        return data

    @model_validator(mode='after')
    def remove_duplicates(self):
        """Remove duplicate pairs from list."""
        duplicates = []
        for pair in self.pairs:
            if pair in duplicates:
                self.pairs.remove(pair)
            duplicates.append(pair)

        return self
