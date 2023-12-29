from fastapi import FastAPI

from .currency_converter.routes import converter_router


app = FastAPI()

app.include_router(converter_router, prefix='/api')
