import pytz
from datetime import datetime, timedelta
from typing import List

from pydantic.error_wrappers import ValidationError
from pydantic.tools import parse_obj_as

from api.models.binance_models import BinanceTicker, BinanceKline
from api.repository.binance_repo import save_binance_ticker, retrieve_latest_ticker, \
    save_candle_stick, get_candle_stick
from api.utils.api_client.third_party.binance_client import binance_kline_client, binance_ticker_client
from api.utils.datetime_convertor import convert_utc_to_local
from api.validators.binance_validator import PriceTickerValidator, \
    CandlestickDataModel, validate_ticker_range, klineValidator
from main import settings
from utils.exception_handler import internal_server_error, validation_exception_handler
from utils.logger import logger_config
from fastapi.encoders import jsonable_encoder
from utils.response_handler import response

logger = logger_config(__name__)


async def save_price_ticker_service(symbols):
    try:
        if isinstance(symbols, str):
            symbols = symbols.split(",")

        resp, status = await binance_ticker_client(symbols)
        print(resp, status, 'Service')
        if not status:
            # Retry Logic - Error handler than can push event to rabbitmq
            return {"success": False}
        # data validation start
        symbols = [data["symbol"] for data in resp]
        pre_data = await retrieve_latest_ticker(symbols)
        v_data = parse_obj_as(List[PriceTickerValidator], resp)
        j_data = jsonable_encoder(v_data)
        validate_ticker_range(j_data, pre_data)
        await save_binance_ticker(j_data)
        return {"success": True}
    except Exception as e:
        logger.error(e)
        # Retry Logic - Error handler than can push event to rabbitmq
        return {"success": False}


async def get_price_ticker_service(symbols: list):
    try:
        data = await retrieve_latest_ticker(symbols)
        if data:
            return parse_obj_as(List[BinanceTicker], data)
        return []
    except ValidationError as e:
        logger.error(e)
        raise internal_server_error


async def get_candle_stick_service(params):
    try:
        local_dt = datetime.now()
        dt_utc = local_dt.astimezone(pytz.UTC)
        local_time = convert_utc_to_local(dt_utc)
        data = await get_candle_stick(params["symbols"], params["interval"], local_time)
        if data:
            return parse_obj_as(List[BinanceKline], data)
        else:
            return []
    except ValidationError as e:
        logger.error(e)
        raise internal_server_error


async def save_candle_stick_service(symbols, exchange: str, interval: str = "1d",
                                    limit: int = None):
    if interval not in ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h",
                        "6h", "8h", "12h", "1d", "3d", "1w", "1M"]:
        raise validation_exception_handler
    symbol_list = []
    if isinstance(symbols, str):
        symbol_list = symbols.split(",")

    failed_symbols = []
    for symbol in symbol_list:
        print(f"started for {symbol}")
        candle_data, status = await binance_kline_client(symbol, interval, limit)

        if not status:
            failed_symbols.append(symbol)
            logger.error(f"Error in getting data for {symbol} /r Error - {candle_data}")
            # raise HTTPException(f"Binance API error: {candle_data}")
            continue

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
            f_data = BinanceKline(kline_data=data, symbol=symbol,
                                  created_at=local_time, updated_at=local_time,
                                  interval=interval,
                                  valid_upto=local_time + timedelta(settings.KLINE_DEFAULT_VALID))
            await save_candle_stick(jsonable_encoder(f_data), latest_time)
        except ValidationError as e:
            logger.error(e)
            failed_symbols.append(symbol)
            # Retry Logic - Error handler than can push event to rabbitmq

    if not failed_symbols:
        return {"success": True}
    return {"success": False, "data": failed_symbols}
