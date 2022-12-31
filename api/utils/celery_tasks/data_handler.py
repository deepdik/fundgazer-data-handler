import asyncio
import time
from datetime import datetime
from celery.schedules import crontab
from api.models.general_models import DataRefreshType
from api.service.binance_service import save_price_ticker_service, save_candle_stick_service

from main import celery, settings


@celery.task(bind=True, name='test', auto_retry=[], max_retries=3)
def test_celery(x, y):
    t1 = time.time()
    print("long time task finished =>" + str((x + y)) + " " + str(datetime.datetime.now()))
    return x + y


@celery.task(bind=True, name='binance_data_refresh', autoretry_for=(Exception,),
             max_retries=3, retry_backoff=True)
def binance_data_refresh(*args, **kwargs):
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
    print("Response", resp)
    return resp


@celery.task(bind=True, name='periodic_binance_kline', autoretry_for=(Exception,),
             max_retries=3, retry_backoff=True)
def periodic_binance_kline(*args, **kwargs):
    resp = asyncio.run(save_candle_stick_service(kwargs.get("symbols"),
                                                 kwargs.get("exchange"), kwargs.get("interval")))
    # add logic in case fail for some symbol
    print("Kline Response", resp)
    if not resp["success"]:
        # retry and can be pushed into Q again with failed symbols
        pass
    return resp


@celery.task(bind=True, name='periodic_binance_ticker', autoretry_for=(Exception,),
             max_retries=3, retry_backoff=True)
def periodic_binance_ticker(*args, **kwargs):
    resp = asyncio.run(save_price_ticker_service(kwargs.get("symbols")))
    print("Ticker Response", resp)
    return resp


# run at midnight 12:01 IST
celery.conf.beat_schedule = {
    'binance_kline_data_refresh': {
        'task': 'periodic_binance_kline',
        'schedule': crontab(minute=0, hour=0),
        'args': [],
        'kwargs': {'symbols': settings.SYMBOL_LIST, "exchange": 'binance', 'interval': '1d'},
        'options': {'queue': 'data-handler'}
    },
    'binance_ticker_data_refresh': {
        'task': 'periodic_binance_ticker',
        'schedule': crontab(minute=0, hour=0),
        'args': [],
        'kwargs': {"symbols": settings.SYMBOL_LIST},
        'options': {'queue': 'data-handler'}
    },
}
