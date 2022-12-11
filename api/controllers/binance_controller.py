import enum
import os
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic.error_wrappers import ValidationError
from pydantic.tools import parse_obj_as
from fastapi.responses import Response, JSONResponse

from api.service.binance_service import (get_candle_stick_service, save_candle_stick_service, get_price_ticker_service,
                                         save_price_ticker_service)
from api.utils.asyncApiUtil import get_request_url
from dotenv import load_dotenv
from utils.response_handler import response
from api.validators.binance_validator import PriceTickerValidator

# APIRouter creates path operations for product module
router = APIRouter(
    prefix="/api/v1",
    tags=["dataHandler"],
    responses={404: {"description": "Not found"}},
)

load_dotenv('config/environ/.env')
BINANCE_SERVER_1 = os.environ["BINANCE_SERVER_1"]
SYMBOL_PRICE_TICKER = os.environ["SYMBOL_PRICE_TICKER"]
CANDLESTICK_DATA = os.environ["CANDLESTICK_DATA"]


@router.get("/binance/ticker/price", response_description="")
async def symbol_price_ticker(symbols: str):
    print(symbols)
    data = await get_price_ticker_service(symbols)
    return data


@router.get("/binance/kline", response_description="")
async def save_symbol_kline(symbol: str, interval: str):
    url = BINANCE_SERVER_1 + CANDLESTICK_DATA

    if interval not in ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"]:
        raise HTTPException(status_code=400, detail="Invalid interval argument")

    params = {"symbol": symbol, "interval": interval}
    rp = await get_candle_stick_service(params)
    return rp


@router.get("/binance/save/ticker", response_description="")
async def save_symbol_price_ticker():
    resp = await save_price_ticker_service()
    return resp


@router.get("/binance/save/kline", response_description="")
async def save_kline():
    resp = await save_candle_stick_service()
    return resp
