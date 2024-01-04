from fastapi import HTTPException


class CustomApiError(HTTPException):
    """Custom API exception class."""


class BaseServiceError(Exception):
    """Base exception for services."""


class BaseClientError(Exception):
    """Base exception class for clients."""
