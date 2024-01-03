from fastapi import HTTPException


class CustomApiError(HTTPException):
    """Custom HTTP Exception class."""
