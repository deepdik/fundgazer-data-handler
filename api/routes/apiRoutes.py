from fastapi import APIRouter

from api.controllers import test

routers = APIRouter()
routers.include_router(test.router)
