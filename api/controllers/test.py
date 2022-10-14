import os
from typing import List

from fastapi import APIRouter
from pydantic.error_wrappers import ValidationError
from pydantic.tools import parse_obj_as

from api.service.binance_service import price_ticker_service, candle_stick_service
from api.utils.asyncApiUtil import request_url
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


@router.get("/hello", response_description="Hello world")
async def read_root():
    return {"Hello": "World"}


@router.get("/price", response_description="")
async def symbol_price_ticker():
    url = BINANCE_SERVER_1+SYMBOL_PRICE_TICKER

    #resp = await request_url(url)

    resp = [{"symbol": "ETHBTC","price": "-1.00000000"}, {"symbol": "LTCBTC","price": "12.00265100"}]

    response = await price_ticker_service(resp)
    return response


@router.get("/kline", response_description="")
async def symbol_price_ticker():
    url = BINANCE_SERVER_1+SYMBOL_PRICE_TICKER

    #resp = await request_url(url)

    resp = [[1499040000000,"0.01634790", "0.80000000", "0.01575800", "0.01577100",
             "148976.11427815", 1499644799999, "2434.19055334", 308, "1756.87402397", "28.46694368", "0"],[1499040000000,"0.01634790", "0.80000000", "0.01575800", "0.01577100",
             "148976.11427815", 1499644799999, "2434.19055334", 308, "1756.87402397", "28.46694368", "0"]]

    response = await candle_stick_service(resp)
    return response
