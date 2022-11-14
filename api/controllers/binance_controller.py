import enum
import os
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic.error_wrappers import ValidationError
from pydantic.tools import parse_obj_as

from api.service.binance_service import price_ticker_service, candle_stick_service
from api.utils.asyncApiUtil import get_request_url
from dotenv import load_dotenv

from api.validators.binance_validator import PriceTickerDataModel

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
async def save_symbol_price_ticker(symbol: str = "", symbols: List[str] = []):
    url = BINANCE_SERVER_1 + SYMBOL_PRICE_TICKER
    print(symbols, symbol)
    if not symbol and not symbols:
        raise HTTPException(status_code=400, detail="symbol and symbols both params can not be blank. Provide at "
                                                    "least one")

    params = {"symbol": symbol} if symbol else {"symbols": symbols}
    resp = await get_request_url(url, params)
    #await price_ticker_service(resp)
    return resp


@router.get("/binance/kline", response_description="")
async def save_symbol_kline(symbol: str, interval: str, limit: str = "", start_time: str= "", end_time: str= ""):
    url = BINANCE_SERVER_1 + CANDLESTICK_DATA

    if interval not in ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h","1d", "3d", "1w", "1M"]:
        raise HTTPException(status_code=400, detail="Invalid interval argument")

    params = {"symbol": symbol, "interval": interval}
    resp = await get_request_url(url, params)
    rp = await candle_stick_service(resp)
    return rp


@router.get("/price-ticker", response_description="")
async def save_symbol_price_ticker():
    url = BINANCE_SERVER_1 + SYMBOL_PRICE_TICKER

    # resp = await request_url(url)

    resp = [{"symbol": "ETHBTC", "price": "1.00000000"}, {"symbol": "LTCBTC", "price": "12.00265100"}]

    response = await price_ticker_service(resp)
    return resp


@router.get("/kline", response_description="")
async def symbol_kline():
    url = BINANCE_SERVER_1 + SYMBOL_PRICE_TICKER

    # resp = await request_url(url)
    resp = [[1499040000000, "0.01634790", "0.80000000", "0.01575800", "0.01577100",
             "148976.11427815", 1499644799999, "2434.19055334", 308, "1756.87402397", "28.46694368", "0"],
            [1499040000000, "0.01634790", "0.80000000", "0.01575800", "0.01577100",
             "148976.11427815", 1499644799999, "2434.19055334", 308, "1756.87402397", "28.46694368", "0"]]

    response = await candle_stick_service(resp)
    return response
