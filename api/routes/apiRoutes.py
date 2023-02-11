
from fastapi import APIRouter

from api.controllers import ticker_kline_controller, task_schedular

routers = APIRouter(
    prefix="/api/v1",
    tags=["dataHandler"],
    responses={404: {"description": "Not found"}},
)

routers.include_router(ticker_kline_controller.router)
routers.include_router(task_schedular.router)