from datetime import timedelta, datetime

from fastapi import APIRouter, HTTPException, Body

from api.service.binance_service import (get_candle_stick_service,
                                         save_candle_stick_service, get_price_ticker_service, save_price_ticker_service)

from api.validators.binance_validator import TaskSchedulerValidator


# APIRouter creates path operations for product module
router = APIRouter(
    prefix="/api/v1",
    tags=["dataHandler"],
    responses={404: {"description": "Not found"}},
)


@router.get("/binance/ticker/price", response_description="")
async def symbol_price_ticker(symbols: str):
    symbols_list = symbols.split(",")
    return await get_price_ticker_service(symbols_list)


@router.get("/binance/kline", response_description="")
async def get_symbol_kline(symbols: str, interval: str):
    if interval not in ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"]:
        raise HTTPException(status_code=400, detail="Invalid interval argument")

    symbols = symbols.split(",")
    # check for supported symbols
    params = {"symbols": symbols, "interval": interval}
    rp = await get_candle_stick_service(params)
    return rp


@router.get("/binance/save/ticker", response_description="")
async def save_symbol_price_ticker(symbols: str):
    resp = await save_price_ticker_service(symbols)
    return resp


@router.get("/binance/save/kline", response_description="")
async def save_kline(symbols: str, interval: str, exchange: str = "binance"):
    resp = await save_candle_stick_service(symbols, exchange, interval)
    return resp


@router.post("/add/celery-task", response_description="")
async def add_refresh_task(data: TaskSchedulerValidator):
    """"""
    from api.service.celery_service import task_scheduler

    await task_scheduler(data)
    return True
