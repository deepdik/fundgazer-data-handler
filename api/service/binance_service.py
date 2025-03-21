import re

import pytz
from datetime import datetime, timedelta
from typing import List

from pydantic.error_wrappers import ValidationError
from pydantic.tools import parse_obj_as

from api.models.binance_models import BinanceKline
from api.models.celery_models import DataRefreshRetryQueue
from api.models.general_models import Platforms, InternalStatusCode
from api.repository.binance_repo import save_binance_ticker, retrieve_latest_ticker, \
    save_candle_stick, get_candle_stick
from api.repository.celery_repo import data_refresh_retry_queue, get_data_refresh_retry_status
from api.service.symbol_service import get_supported_symbol_mapping
from api.utils.api_client.third_party.binance.binance_client import binance_kline_client, binance_ticker_client
from api.utils.datetime_convertor import convert_utc_to_local, get_current_local_time
from api.validators.binance_validator import PriceTickerValidator, \
    CandlestickDataModel, validate_ticker_range, klineValidator, get_symbol_mapping
from api.validators.fyers_validator import symbol_validator
from main import settings
from utils.logger import logger_config
from fastapi.encoders import jsonable_encoder

from utils.response_handler import response

logger = logger_config(__name__)


async def save_binance_price_ticker_service(symbols):
    try:
        if isinstance(symbols, str):
            symbols = symbols.split(",")

        mapped_symbol = []
        # get binance supported symbol mapping
        supp_symbols_list = await get_supported_symbol_mapping()
        not_supported_symb = []
        symbol_mapping = {}
        for symbol in symbols:
            if supp_symbols_list.get(symbol) and supp_symbols_list.get(symbol).get("binance"):
                mapped_symbol.append(supp_symbols_list.get(symbol).get("binance"))
                symbol_mapping[supp_symbols_list.get(symbol).get("binance")] = symbol
            else:
                not_supported_symb.append(symbol)

        if not mapped_symbol:
            return {"success": False, "not_supported_symb": not_supported_symb}
        print(supp_symbols_list, not_supported_symb)
        resp, status = await binance_ticker_client(mapped_symbol)
        print(f"{resp} =>>>>>>>>{status}")
        if not status:
            # Retry Logic - Error handler than can push event to rabbitmq
            return {"success": False, "not_supported_symb": not_supported_symb}
        # data validation start
        pre_data = await retrieve_latest_ticker(mapped_symbol)
        v_data = parse_obj_as(List[PriceTickerValidator], resp)
        # converting external symbol to internal symbol mapping
        v_data = get_symbol_mapping(v_data, symbol_mapping)
        j_data = jsonable_encoder(v_data)
        validate_ticker_range(j_data, pre_data)
        await save_binance_ticker(j_data)
        return {"success": True, "not_supported_symb": not_supported_symb}
    except Exception as e:
        logger.error(e)
        # Retry Logic - Error handler than can push event to rabbitmq
        return {"success": False, "detail": str(e)}


async def get_binance_ticker_price_service(symbols: str):
    if isinstance(symbols, str):
        symbols = symbols.split(",")

    mapped_symbol = []
    # get binance supported symbol mapping
    supp_symbols_list = await get_supported_symbol_mapping()
    not_supported_symb = []
    symbol_mapping = {}
    for symbol in symbols:
        if supp_symbols_list.get(symbol) and supp_symbols_list.get(symbol).get("binance"):
            mapped_symbol.append(supp_symbols_list.get(symbol).get("binance"))
            symbol_mapping[supp_symbols_list.get(symbol).get("binance")] = symbol
        else:
            not_supported_symb.append(symbol)

    if not_supported_symb:
        return response(message=f"Symbols not supported {not_supported_symb}", status_code=400)

    resp, status = await binance_ticker_client(mapped_symbol)
    print(f"{resp} =>>>>>>>>{status}")
    if not status:
        return response(message="please try after some time", status_code=503, error=resp)

    # data validation start
    # pre_data = await retrieve_latest_ticker(mapped_symbol)
    v_data = parse_obj_as(List[PriceTickerValidator], resp)

    # converting external symbol to internal symbol mapping
    v_data = jsonable_encoder(get_symbol_mapping(v_data, symbol_mapping))
    return response(data=v_data, message="success", success=True)


async def get_binance_candle_stick_service(params):
    # get binance supported symbol mapping
    await symbol_validator(params["symbols"], Platforms.BINANCE)
    local_time = get_current_local_time()
    data, got_symbols = await get_candle_stick(params["symbols"], params["interval"], local_time)
    # if any of the candle is missing
    if not len(params["symbols"]) == len(data):
        # check for missing symbol
        diff_symbols = set(params["symbols"]) - got_symbols
        if diff_symbols:
            # check in retry queue
            # if symbol retry exceeded max retry then halt the strategy
            if not await get_data_refresh_retry_status(list(diff_symbols), params["interval"], Platforms.BINANCE):
                # internal_status_code. Halt strategy
                return response(
                    internal_status_code=InternalStatusCode.HALT_STRATEGY,
                    message=f"No data found for some symbols. Halt the strategies",
                    data=list(diff_symbols),
                    status_code=503,
                    success=True
                )
            return response(
                internal_status_code=InternalStatusCode.RETRY_AFTER_SOME_TIME,
                message=f"No data found for some symbols. Please try after some time.",
                data=list(diff_symbols),
                status_code=503,
                success=True
            )

    return data


async def save_binance_candle_stick_service(symbols, exchange: str, interval: str = "1d",
                                            limit: int = None):
    if interval not in ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h",
                        "6h", "8h", "12h", "1d", "3d", "1w"]:
        return {"success": False, "message": "Invalid Interval value"}

    if isinstance(symbols, str):
        symbols = symbols.split(",")

    failed_symbols = []
    mapped_symbol = []
    supp_symbols_list = await get_supported_symbol_mapping()
    not_supported_symb = []
    symbol_mapping = {}
    completed = []
    for symbol in symbols:
        if supp_symbols_list.get(symbol) and supp_symbols_list.get(symbol).get("binance"):
            mapped_symbol.append(supp_symbols_list.get(symbol).get("binance"))
            symbol_mapping[supp_symbols_list.get(symbol).get("binance")] = symbol
        else:
            not_supported_symb.append(symbol)

    for symbol in mapped_symbol:
        print(f"started for {symbol}")
        candle_data, status = await binance_kline_client(symbol, interval, limit)

        if not status:
            failed_symbols.append(symbol)
            logger.error(f"Error in getting data for {symbol} /r Error - {candle_data}")
            continue

        dict_data = []
        try:
            fields = CandlestickDataModel.__fields__.keys()
            for data in candle_data:
                dict_data.append(dict(zip(fields, data)))
            # sort candles based on their time
            dict_data.sort(key=lambda item: item['open_time'])
            data = parse_obj_as(List[CandlestickDataModel], dict_data)
            klineValidator(data, limit)
            # pop out last candle
            data.pop()
            local_time = get_current_local_time()
            # valid_upto = > second last candle close time + timeframe - 1
            candle_close_time = data[-1].close_time
            print(f"candle_close_time {candle_close_time}")
            int_interval = int(re.search(r'\d+', interval).group())
            if "m" in interval:
                valid_upto = candle_close_time + timedelta(minutes=int_interval - 1)
            elif "h" in interval:
                valid_upto = candle_close_time + timedelta(minutes=int_interval * 60 - 1)
            elif "d" in interval:
                valid_upto = candle_close_time + timedelta(minutes=int_interval * 60 * 24 - 1)
            elif "w" in interval:
                valid_upto = candle_close_time + timedelta(minutes=int_interval * 60 * 24 * 7 - 1)
            else:
                raise ValueError("Invalid interval value")

            f_data = BinanceKline(kline_data=data, symbol=symbol_mapping.get(symbol),
                                  created_at=local_time, updated_at=local_time,
                                  interval=interval,
                                  valid_upto=valid_upto)

            await save_candle_stick(f_data)
            completed.append(symbol_mapping.get(symbol))
        except Exception as e:
            logger.error(e)
            failed_symbols.append(symbol)

    if not failed_symbols and not not_supported_symb:
        return {"success": True}
    if failed_symbols:
        for symbol in failed_symbols:
            # Retry Logic - Error handler than can push event to rabbitmq
            retry_data = DataRefreshRetryQueue(
                symbol=symbol,
                exchange=Platforms.BINANCE,
                max_retry=settings.DATA_REFRESH_MAX_RETRY,
                cron_syntax=settings.DATA_REFRESH_CRON,
                retry_count=0,
                interval=interval
            )
            await data_refresh_retry_queue(retry_data, "SAVE")

    return {"success": False, "failed": failed_symbols, "completed": completed,
            "not_supported_symb": not_supported_symb}
