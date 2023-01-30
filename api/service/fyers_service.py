import re
from datetime import date, datetime, timedelta
from typing import List
import pytz
from pydantic.error_wrappers import ValidationError

from pydantic.tools import parse_obj_as

from api.models.fyers_models import FyersKline
from api.repository.fyers_repo import save_fyers_candle_stick, get_candle_stick
from api.service.symbol_service import get_supported_symbol_mapping
from api.utils.api_client.third_party.fyers.market_data import get_fyers_stocks_client, get_fyers_latest_price_client
from api.utils.datetime_convertor import convert_utc_to_local, get_current_local_time
from api.validators.binance_validator import get_symbol_mapping
from api.validators.fyers_validator import SaveStockQueryValidator, FyersCandlestickDataModel, StockPriceTickerValidator
from main import settings
from utils.logger import logger_config
from fastapi.encoders import jsonable_encoder

from utils.response_handler import response

logger = logger_config(__name__)


async def save_stocks_service(symbols: str, date_from: date, date_to: date, interval: str = "D"):
    """
    """
    try:
        params = SaveStockQueryValidator(
            symbols=symbols,
            date_from=date_from,
            date_to=date_to,
            interval=interval
        )
        symbols = params.symbols
        date_from = params.date_from
        date_to = params.date_to
        interval = params.interval
    except Exception as e:
        return {"success": False, "message": str(e)}

    failed_symbols = []
    mapped_symbol = []
    supp_symbols_list = await get_supported_symbol_mapping()
    not_supported_symb = []
    symbol_mapping = {}
    completed = []
    for symbol in symbols:
        print(supp_symbols_list.get(symbol))
        print(supp_symbols_list.get(symbol).get("fyers"))
        if supp_symbols_list.get(symbol) and supp_symbols_list.get(symbol).get("fyers"):
            mapped_symbol.append(supp_symbols_list.get(symbol).get("fyers"))
            symbol_mapping[supp_symbols_list.get(symbol).get("fyers")] = symbol
        else:
            not_supported_symb.append(symbol)

    for symbol in mapped_symbol:
        print(f"started for {symbol}")
        candle_data, status = await get_fyers_stocks_client(symbol, date_from, date_to, interval)

        if not status:
            failed_symbols.append(symbol)
            logger.error(f"Error in getting data for {symbol} /r Error - {candle_data}")
            continue

        dict_data = []
        try:
            fields = FyersCandlestickDataModel.__fields__.keys()
            for data in candle_data:
                dict_data.append(dict(zip(fields, data)))

            # sort candles based on their time
            dict_data.sort(key=lambda item: item['open_time'])
            data = parse_obj_as(List[FyersCandlestickDataModel], dict_data)
            local_time = get_current_local_time()
            candle_close_time = data[-1].open_time

            if interval == "D":
                valid_upto = candle_close_time + timedelta(minutes=60 * 24 - 1)
            else:
                valid_upto = candle_close_time + timedelta(minutes=int(interval) - 1)

            f_data = FyersKline(kline_data=data, symbol=symbol_mapping.get(symbol),
                                created_at=local_time,
                                date_from=date_from,
                                date_to=date_to,
                                interval=interval,
                                valid_upto=valid_upto)

            await save_fyers_candle_stick(f_data)
            completed.append(symbol_mapping.get(symbol))
        except Exception as e:
            logger.error(e)
            failed_symbols.append(symbol)
            # Retry Logic - Error handler than can push event to rabbitmq
    if not failed_symbols and not not_supported_symb:
        return {"success": True}
    return {"success": False, "failed": failed_symbols, "completed": completed,
            "not_supported_symb": not_supported_symb}


async def get_candle_stick_service(params):
    local_time = get_current_local_time()
    data = await get_candle_stick(params["symbols"], params["interval"], local_time)
    # if any of the candle is missing
    if not len(params["symbols"]) == len(data):
        return []
    if data:
        return parse_obj_as(List[FyersKline], data)
    else:
        return []


async def get_latest_ticker_price_service(symbols: str):
    if isinstance(symbols, str):
        symbols = symbols.split(",")

    mapped_symbol = []
    # get binance supported symbol mapping
    supp_symbols_list = await get_supported_symbol_mapping()
    not_supported_symb = []
    symbol_mapping = {}
    for symbol in symbols:
        if supp_symbols_list.get(symbol) and supp_symbols_list.get(symbol).get("fyers"):
            mapped_symbol.append(supp_symbols_list.get(symbol).get("fyers"))
            symbol_mapping[supp_symbols_list.get(symbol).get("fyers")] = symbol
        else:
            not_supported_symb.append(symbol)

    if not_supported_symb:
        return response(message=f"Symbols not supported {not_supported_symb}", status_code=400)

    resp, status = await get_fyers_latest_price_client(mapped_symbol)
    if not status:
        return response(message="please try after some time", status_code=503, error=resp)

    v_data = parse_obj_as(List[StockPriceTickerValidator], resp)
    # converting external symbol to internal symbol mapping
    v_data = jsonable_encoder(get_symbol_mapping(v_data, symbol_mapping))
    return response(data=v_data, message="success")
