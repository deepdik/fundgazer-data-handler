import datetime
from datetime import date

from fastapi import APIRouter

from api.models.general_models import Platforms
from api.repository.celery_repo import delete_data_refresh_retry_queue
from api.service.binance_service import get_binance_ticker_price_service, get_binance_candle_stick_service, \
    save_binance_candle_stick_service
from api.service.fyers_service import get_fyers_ticker_price_service, get_fyers_candle_stick_service, \
    save_fyers_stocks_service
from api.utils.celery_tasks.data_handler import data_refresh_retry
from api.utils.datetime_convertor import get_current_local_time
from api.validators.binance_validator import GetBinanceKlineParamsValidator
from api.validators.fyers_validator import GetStockParamsValidator
from config.database.mongo import MongoManager

router = APIRouter(
    prefix="",
    tags=["dataHandler"],
    responses={404: {"description": "Not found"}},
)


@router.get("/ticker/price", response_description="")
async def symbol_price_ticker(symbols: str, exchange: Platforms):
    if exchange == Platforms.FYERS:
        return await get_fyers_ticker_price_service(symbols)
    elif exchange == Platforms.BINANCE:
        return await get_binance_ticker_price_service(symbols)


@router.get("/kline", response_description="")
async def get_symbol_kline(symbols: str, interval: str, exchange: Platforms):
    if exchange == Platforms.BINANCE:
        params = GetBinanceKlineParamsValidator(
            symbols=symbols,
            interval=interval
        )
        params = {"symbols": params.symbols, "interval": params.interval}
        return await get_binance_candle_stick_service(params)

    elif exchange == Platforms.FYERS:
        params = GetStockParamsValidator(
            symbols=symbols,
            interval=interval
        )
        params = {"symbols": params.symbols, "interval": params.interval}
        return await get_fyers_candle_stick_service(params)


@router.get("/save/kline", response_description="")
async def save_kline(symbols: str, interval: str, exchange: Platforms):
    if exchange == Platforms.BINANCE:
        return await save_binance_candle_stick_service(symbols, exchange, interval)
    elif exchange == Platforms.FYERS:
        date_to = get_current_local_time().date()
        date_from = get_current_local_time() - datetime.timedelta(days=1)
        return await save_fyers_stocks_service(symbols, date_from, date_to, interval)


@router.get("/test", response_description="")
async def test():
    #await data_refresh_retry()
    await delete_data_refresh_retry_queue('ICXUSDT', 'binance', '1d')
    # database = await MongoManager.get_instance()
    # data = {"valid_upto": str(get_current_local_time() + datetime.timedelta(minutes=10))}
    # print(get_current_local_time())
    # query1 = {"valid_upto": {"$gt": str(get_current_local_time())}}
    # # await database.test.insert_one(data)
    # print(await database.fyers_access_token.find(query1).to_list(100))
    #
    # query2 = {"valid_upto": {"$lt": str(get_current_local_time())}}
    # # await database.test.insert_one(data)
    # print(await database.fyers_access_token.find(query2).to_list(100))
