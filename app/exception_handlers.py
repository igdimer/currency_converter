from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse


async def internal_exception_handler(request: Request, exc: Exception):
    """Return 500 errors as JSON."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder({'detail': 'Internal Server Error'}),
    )
