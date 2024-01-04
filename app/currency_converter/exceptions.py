from starlette import status

from app.core.exceptions import CustomApiError


class ExchangerateApiError(CustomApiError):
    """Error occurred during requesting to Exchangerate API."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        self.status_code = status.HTTP_400_BAD_REQUEST