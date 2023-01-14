from datetime import timedelta, datetime, date

from fastapi import APIRouter, HTTPException, Body

from api.service.fyers_service import save_stocks_service, get_candle_stick_service
from api.validators.fyers_validator import  GetStockParamsValidator

router = APIRouter(
    prefix="/fyers",
    tags=["dataHandler"],
    responses={404: {"description": "Not found"}},
)


@router.get("/save/kline", response_description="")
async def symbol_price_ticker(symbols: str, date_from: date, date_to: date, interval: str):
    return await save_stocks_service(symbols, date_from, date_to, interval)


@router.get("/save/latest/price", response_description="")
async def symbol_price_ticker(symbols: str, date_from: date, date_to: date, interval: str):
    return await save_stocks_service(symbols, date_from, date_to, interval)


@router.get("/kline", response_description="")
async def get_symbol_kline(symbols: str, interval: str):
    params = GetStockParamsValidator(
        symbols=symbols,
        interval=interval
    )
    # check for supported symbols
    params = {"symbols": params.symbols, "interval": params.interval}
    rp = await get_candle_stick_service(params)
    return rp