import asyncio
import time
from datetime import datetime, timedelta
from celery.schedules import crontab
from api.models.general_models import DataRefreshType, Platforms
from api.repository.celery_repo import data_refresh_retry_queue, delete_data_refresh_retry_queue
from api.service.binance_service import save_binance_price_ticker_service, save_binance_candle_stick_service
from api.service.fyers_service import save_fyers_stocks_service
from api.utils.datetime_convertor import get_current_local_time
from api.utils.utils import is_required_scheduling

from main import celery, settings
from utils.logger import logger_config

logger = logger_config(__name__)


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
        resp = asyncio.run(save_binance_price_ticker_service(kwargs.get("symbols")))

    elif DataRefreshType.BINANCE_KLINE == refresh_type:
        resp = asyncio.run(save_binance_candle_stick_service(
            kwargs.get("symbols"),
            kwargs.get("exchange"),
            kwargs.get("interval")
        ))
    # symbols: str, date_from: date, date_to: date, interval: str = "D"
    elif DataRefreshType.FYERS_KLINE == refresh_type:
        date_from = kwargs.get("date_from")
        date_to = kwargs.get("date_to")
        interval = kwargs.get("interval")

        if not date_to:
            date_to = get_current_local_time().date()

        if not date_from:
            date_from = get_current_local_time().date() - timedelta(days=30)

        if not interval:
            interval = "D"

        print(kwargs.get("symbols"))
        resp = asyncio.run(save_fyers_stocks_service(
            kwargs.get("symbols"),
            date_from,
            date_to,
            interval
        ))
    else:
        print(f"Invalid refresh try => {refresh_type}")

    print(f"Response => {resp}")
    # remove from retry queue
    if resp.get("success") and kwargs.get("retry_count") is not None:
        # remove from retry queue
        asyncio.run(delete_data_refresh_retry_queue(
            kwargs.get("symbols"),
            kwargs.get("exchange"),
            kwargs.get("interval")
        ))
    return resp


@celery.task(name='data_refresh_retry', autoretry_for=(Exception,),
             max_retries=3, retry_backoff=True)
def data_refresh_retry():
    # get task list
    tasks = asyncio.run(data_refresh_retry_queue({}, "GET_ALL"))
    #tasks = await data_refresh_retry_queue({}, "GET_ALL")

    logger.info(tasks)
    for task in tasks:
        logger.info("Started adding task")
        status, schedule_time = is_required_scheduling(task.get("cron_syntax"), 10)
        logger.info(f"got status and runtime {status}, {schedule_time}")
        if status:
            if task["exchange"] == Platforms.BINANCE:
                data_refresh.apply_async(
                    queue="data-handler",
                    priority=9,
                    args=[],
                    kwargs={'symbols': task["symbol"],
                            "exchange": task["exchange"], 'interval': task["interval"],
                            "refresh_type": DataRefreshType.BINANCE_KLINE,
                            "retry_count": task["retry_count"],
                            "max_retry": task["max_retry"]
                            },
                    eta=schedule_time
                )
                logger.info(f"task added in retry queue successfully")

            elif task["exchange"] == Platforms.FYERS:
                data_refresh.apply_async(
                    queue="data-handler",
                    priority=9,
                    args=[],
                    kwargs={'symbols': task["symbol"],
                            "exchange": task["exchange"], 'interval': task["interval"],
                            "refresh_type": DataRefreshType.FYERS_KLINE,
                            "retry_count": task["retry_count"],
                            "max_retry": task["max_retry"],
                            "date_from": task["date_from"],
                            "date_to": task["date_to"],
                            },
                    eta=schedule_time
                )
                logger.info(f"task added in retry queue successfully")


celery.conf.beat_schedule = {
    'binance_kline_data_refresh': {
        'task': 'data_refresh',
        'schedule': crontab(minute=1, hour=0),
        'args': [],
        'kwargs': {'symbols': settings.SYMBOL_LIST,
                   "exchange": 'binance', 'interval': '1d',
                   "refresh_type": DataRefreshType.BINANCE_KLINE},
        'options': {'queue': 'data-handler'}
    },
    'data_refresh_retry': {
        'task': 'data_refresh_retry',
        'schedule': crontab(minute="*/10"),
        'options': {'queue': 'data-handler-retry'}
    },
    'fyers_stocks_data_refresh': {
        'task': 'data_refresh',
        'schedule': crontab(minute=3, hour=0, day_of_week='mon-fri'),
        'args': [],
        'kwargs': {"symbols": settings.FYERS_SYMBOL_LIST,
                   "refresh_type": DataRefreshType.FYERS_KLINE},
        'options': {'queue': 'data-handler'}
    },
}
