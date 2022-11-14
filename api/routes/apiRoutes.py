from fastapi import APIRouter

from api.controllers import binance_controller

routers = APIRouter()
routers.include_router(binance_controller.router)
