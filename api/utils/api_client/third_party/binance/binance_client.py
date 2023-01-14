from api.exception.api_caller_wrapper import async_api_caller
from api.models.general_models import APIMethodEnum
from main import settings


async def binance_ticker_client(symbols: list):
    url = settings.BINANCE_SERVER_1 + settings.BINANCE_TICKER
    str_symbol = ','.join(f'"{w}"' for w in symbols)
    params = {"symbols": f'[{str_symbol}]'} if symbols else {}
    return await async_api_caller(url, APIMethodEnum.GET, params)


async def binance_kline_client(symbol: str, interval: str, limit: int = None):
    url = settings.BINANCE_SERVER_1 + settings.BINANCE_CANDLESTICK_DATA
    params = {"symbol": symbol, "interval": interval}
    if limit:
        params["limit"] = limit
    return await async_api_caller(url, APIMethodEnum.GET, params)
