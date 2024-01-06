from fastapi import HTTPException


class CustomApiError(HTTPException):
    """Custom API exception class."""

    status_code: int

    def __init__(self) -> None:
        super().__init__(status_code=self.status_code, detail=self.detail)


class BaseServiceError(Exception):
    """Base exception for services."""


class BaseClientError(Exception):
    """Base exception class for clients."""
