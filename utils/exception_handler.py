from fastapi import Request, status

from main import app
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from utils.response_handler import response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print("exception handler called...")
    return response(success= False, message= 'Invalid input type!!', error=exc.errors(),
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
)


@app.exception_handler(Exception)
async def internal_server_error(request: Request, exc: RequestValidationError):
    return response(error="Internal server error. Please try after some time", status_code=500)


@app.exception_handler(Exception)
async def invalid_argument(request: Request, exc: RequestValidationError):
    return response(error="", status_code=500)

