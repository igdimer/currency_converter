from app.core.schemas import BaseSchema


class RateOutput(BaseSchema):
    """Response model for currency rate."""

    pair: str
    rate: float
    description: str
