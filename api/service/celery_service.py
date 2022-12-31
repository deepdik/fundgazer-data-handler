from datetime import datetime, timedelta

from api.models.general_models import TaskDueType, DataRefreshType
from api.service.binance_service import save_price_ticker_service
from api.utils.celery_tasks.data_handler import binance_data_refresh, test_celery
from api.validators.binance_validator import TaskSchedulerValidator


async def task_scheduler(data: TaskSchedulerValidator):
    delta_time = {}
    if data.run_after == TaskDueType.DAYS:
        delta_time[TaskDueType.DAYS] = data.run_after_val
    elif data.run_after == TaskDueType.HOURS:
        delta_time[TaskDueType.HOURS] = data.run_after_val
    elif data.run_after == TaskDueType.WEEKS:
        delta_time[TaskDueType.WEEKS] = data.run_after_val
    elif data.run_after == TaskDueType.MINUTES:
        delta_time[TaskDueType.MINUTES] = data.run_after_val
    elif data.run_after == TaskDueType.SECONDS:
        delta_time[TaskDueType.SECONDS] = data.run_after_val

    eta = datetime.utcnow() + timedelta(**delta_time)
    exp = eta + timedelta(minutes=5)

    print(eta, data, exp)
    if data.refresh_type == DataRefreshType.BINANCE_TICKER:
        binance_data_refresh.apply_async(
            queue='data-handler', priority=9,
            args=[],
            kwargs={"symbols": data.data["symbols"], "refresh_type": data.refresh_type},
            eta=eta,
            expires=exp
        )
    if data.refresh_type == DataRefreshType.BINANCE_KLINE:
        binance_data_refresh.apply_async(
            queue='data-handler', priority=9,
            args=[],
            kwargs={"symbols": data.data["symbols"],
                    "refresh_type": data.refresh_type,
                    "exchange": data.data["exchange"],
                    "interval": data.data["interval"]
            },
            eta=eta,
            expires=exp
            )

    return True
