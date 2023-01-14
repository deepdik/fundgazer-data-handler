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
    FYERS_KLINE = 'fyers_candle'


class TaskDueType(str, Enum):
    WEEKS = 'weeks'
    DAYS = 'days'
    MINUTES = 'minutes'
    HOURS = 'hours'
    SECONDS = 'seconds'


class StatusCodes(int, Enum):
    """
    Subset of suitable HTTP status codes that are good fit to
    describe the scenario of the custom exceptions.
    """

    NO_CONTENT = 204
    BAD_REQUEST = 400
    NOT_AUTHORIZED = 401
    NOT_FOUND = 404
    NOT_ACCEPTABLE = 406
    REQUEST_TIMEOUT = 408
    EXPECTATION_FAILED = 412
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504