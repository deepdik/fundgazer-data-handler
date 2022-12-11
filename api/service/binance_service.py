import os
import pytz
from datetime import datetime, timedelta
from http.client import HTTPException
from typing import List

from pydantic.error_wrappers import ValidationError
from pydantic.tools import parse_obj_as

from api.models.binance_models import BinanceTicker, BinanceKline
from api.repository.binance_repo import save_binance_ticker, retrieve_latest_ticker, save_candle_stick, get_candle_stick
from api.utils.asyncApiUtil import get_request_url
from api.utils.datetime_convertor import convert_utc_to_local
from api.validators.binance_validator import PriceTickerValidator, CandlestickDataModel, validate_ticker_range, \
    klineValidator
from utils.logger import logger_config
from dotenv import load_dotenv
from fastapi.encoders import jsonable_encoder
from config.config import get_config

logger = logger_config(__name__)
setting = get_config()

load_dotenv('config/environ/.env')
BINANCE_SERVER_1 = os.environ["BINANCE_SERVER_1"]
SYMBOL_PRICE_TICKER = os.environ["SYMBOL_PRICE_TICKER"]
CANDLESTICK_DATA = os.environ["CANDLESTICK_DATA"]


async def save_price_ticker_service():
    try:
        url = BINANCE_SERVER_1 + SYMBOL_PRICE_TICKER
        params = {}
        # status, resp = await get_request_url(url, params)
        resp = [{"symbol": "LTCBTC", "price": "10.00265100"}]
        if isinstance(resp, list):
            symbols = [data["symbol"] for data in resp]
            pre_data = await retrieve_latest_ticker(symbols)
            v_data = parse_obj_as(List[PriceTickerValidator], resp)

        elif isinstance(resp, dict):
            symbols = list(resp["symbol"])
            pre_data = await retrieve_latest_ticker(symbols)
            v_data = PriceTickerValidator.parse_obj(resp)
        j_data = jsonable_encoder(v_data)
        validate_ticker_range(pre_data, j_data)
        await save_binance_ticker(j_data)
        return v_data
    except Exception as e:
        logger.error(e)
        print(e)


async def get_price_ticker_service(symbols):
    try:
        symbols = symbols.split(",")
        data = await retrieve_latest_ticker(symbols)
        if data:
            if len(data) == 1:
                return BinanceTicker(**data[0])
            elif len(data) > 1:
                return parse_obj_as(List[BinanceTicker], data)
        return []
    except ValidationError as e:
        logger.error(e)
        print(e)


async def get_candle_stick_service(parms):
    try:
        local_dt = datetime.now()
        dt_utc = local_dt.astimezone(pytz.UTC)
        local_time = convert_utc_to_local(dt_utc)
        data = await get_candle_stick(parms["symbol"], parms["interval"], local_time)
        if data:
            return BinanceKline(**data)
        else:
            return {}
    except ValidationError as e:
        logger.error(e)
        print(e)


async def save_candle_stick_service(limit=1000):
    url = BINANCE_SERVER_1 + CANDLESTICK_DATA
    symbol = "LTCBTC"
    interval = "1h"
    if interval not in ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"]:
        raise HTTPException("Invalid interval argument")

    params = {"symbol": symbol, "interval": interval, "limit": 1000}
    status, candle_data = await get_request_url(url, params)
    if not status:
        raise HTTPException(f"Binance API error: {candle_data}")
    # candle_data = [[
    #     1666562400000,
    #     "0.06840900",
    #     "0.06980000",
    #     "0.06836400",
    #     "0.06968900",
    #     "17495.15210000",
    #     1666565999999,
    #     "1213.58473223",
    #     32492,
    #     "10787.94610000",
    #     "748.47236209",
    #     "0"
    # ], [
    #     1666566000000,
    #     "0.06968900",
    #     "0.06981900",
    #     "0.06963500",
    #     "0.06970900",
    #     "5121.48490000",
    #     1666569599999,
    #     "357.10187059",
    #     8928,
    #     "2701.87820000",
    #     "188.40223381",
    #     "0"
    # ]]

    dict_data = []
    try:
        fields = CandlestickDataModel.__fields__.keys()
        for data in candle_data:
            dict_data.append(dict(zip(fields, data)))
        data = parse_obj_as(List[CandlestickDataModel], dict_data)

        latest_time = klineValidator(data, limit)
        local_dt = datetime.now()
        dt_utc = local_dt.astimezone(pytz.UTC)
        local_time = convert_utc_to_local(dt_utc)
        f_data = BinanceKline(kline_data=data, symbol=symbol, created_at=local_time, updated_at=local_time,
                              interval=interval, valid_upto=local_time + timedelta(setting.KLINE_DEFAULT_VALID))
        await save_candle_stick(jsonable_encoder(f_data), latest_time)
    except ValidationError as e:
        logger.error(e)
        print(e)
