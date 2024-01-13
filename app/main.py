from fastapi import FastAPI

from app.currency_converter.routes import converter_router
from app.users.routes import users_router

from .exception_handlers import internal_exception_handler

app = FastAPI()

app.include_router(converter_router, prefix='/api')
app.include_router(users_router, prefix='/api')

app.add_exception_handler(500, internal_exception_handler)
