import asyncio
import time
from datetime import datetime, timedelta
from celery.schedules import crontab
from api.models.general_models import DataRefreshType
from api.service.binance_service import save_price_ticker_service, save_candle_stick_service
from api.service.fyers_service import save_stocks_service
from api.utils.datetime_convertor import get_current_local_time

from main import celery, settings


@celery.task(bind=True, name='test', auto_retry=[], max_retries=3)
def test_celery(x, y):
    t1 = time.time()
    print("long time task finished =>" + str((x + y)) + " " + str(datetime.datetime.now()))
    return x + y


@celery.task(bind=True, name='data_refresh', autoretry_for=(Exception,),
             max_retries=3, retry_backoff=True)
def data_refresh(*args, **kwargs):
    resp = ''
    refresh_type = kwargs.get("refresh_type", '')
    if DataRefreshType.BINANCE_TICKER == refresh_type:
        resp = asyncio.run(save_price_ticker_service(kwargs.get("symbols")))
    elif DataRefreshType.BINANCE_KLINE == refresh_type:
        resp = asyncio.run(save_candle_stick_service(
            kwargs.get("symbols"),
            kwargs.get("exchange"),
            kwargs.get("interval")
        ))
    # symbols: str, date_from: date, date_to: date, interval: str = "D"
    elif DataRefreshType.FYERS_KLINE == refresh_type:
        date_to = get_current_local_time().date()
        date_from = get_current_local_time().date() - timedelta(days=30)
        interval = "D"
        print(kwargs.get("symbols"))
        resp = asyncio.run(save_stocks_service(
            kwargs.get("symbols"),
            date_from,
            date_to,
            interval
        ))
    else:
        print(f"Invalid refresh try => {refresh_type}")

    print(f"Response => {resp}")
    return resp


celery.conf.beat_schedule = {
    'binance_kline_data_refresh': {
        'task': 'data_refresh',
        'schedule': crontab(),
        'args': [],
        'kwargs': {'symbols': settings.SYMBOL_LIST,
                   "exchange": 'binance', 'interval': '1d',
                   "refresh_type":DataRefreshType.BINANCE_KLINE},
        'options': {'queue': 'data-handler'}
    },
    'binance_ticker_data_refresh': {
        'task': 'data_refresh',
        'schedule': crontab(),
        'args': [],
        'kwargs': {"symbols": settings.SYMBOL_LIST, "refresh_type":DataRefreshType.BINANCE_TICKER},
        'options': {'queue': 'data-handler'}
    },
    'fyers_stocks_data_refresh': {
        'task': 'data_refresh',
        'schedule': crontab(),
        'args': [],
        'kwargs': {"symbols": settings.FYERS_SYMBOL_LIST,
                   "refresh_type":DataRefreshType.FYERS_KLINE},
        'options': {'queue': 'data-handler'}
    },
}
