from pydantic.types import Enum


class APIMethodEnum(str, Enum):
    POST = 'post'
    GET = 'get'
    DELETE = 'delete'
    PUT = 'put'
    PATCH = 'patch'


class DataRefreshType(str, Enum):
    BINANCE_TICKER = "binance_ticker"
    BINANCE_KLINE = 'binance_kline'


class TaskDueType(str, Enum):
    WEEKS = 'weeks'
    DAYS = 'days'
    MINUTES = 'minutes'
    HOURS = 'hours'
    SECONDS = 'seconds'
