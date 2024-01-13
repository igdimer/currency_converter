from app.core.schemas import BaseSchema


class TokensOutput(BaseSchema):
    """Response model for access and refresh tokens."""

    access_token: str
    refresh_token: str
