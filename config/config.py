import os
from functools import lru_cache
from typing import List

from pydantic import BaseSettings
from dotenv import load_dotenv

load_dotenv('config/environ/.env')


# class Settings(BaseSettings):
#     APP_NAME: str = "Data handler API"


class Settings(BaseSettings):
    """app config settings"""

    PROJECT_NAME: str = "dataHandler"
    VERSION: str = "1.0"
    DESCRIPTION: str = "description"
    SECRET_KET: str = None
    ENV: str

    DB_URI: str = os.getenv("MONGODB_URI")
    DATE_FORMAT = "DD-MM-YYYY"
    LOCAL_TIME_ZONE = "Asia/Calcutta"
    KLINE_DEFAULT_VALID: int = 30  # min

    HTTP_TOO_MANY_REQ_SLEEP: int
    HTTP_REQ_TIMEOUT_SLEEP: int
    ASYNC_TIMEOUT_SLEEP: int
    ERROR_RETRY_COUNT: int

    BINANCE_SERVER_1: str
    BINANCE_SERVER_2: str
    BINANCE_SERVER_3: str
    BINANCE_SERVER_4: str
    BINANCE_TICKER: str
    BINANCE_CANDLESTICK_DATA: str

    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    CELERY_ACKS_LATE: bool

    SYMBOL_LIST: List[str]
    FYERS_SYMBOL_LIST: str

    class Config:
        case_sensitive = True
        env_file = "config/environ/.env"


@lru_cache(128)
def get_config():
    return Settings()
