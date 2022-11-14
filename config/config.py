import os
from functools import lru_cache

from pydantic import BaseSettings
from dotenv import load_dotenv

load_dotenv('config/environ/.env')


class Settings(BaseSettings):
    APP_NAME: str = "Data handler API"


class Settings(BaseSettings):
    """app config settings"""

    PROJECT_NAME: str = "dataHandler"
    VERSION: str = "1.0"
    DESCRIPTION: str = "description"
    SECRET_KET: str = None
    # DEBUG: bool = bool(os.getenv("DEBUG", "False"))
    DB_URI: str = os.getenv("MONGODB_URI")
    DATE_FORMAT = "DD-MM-YYYY"
    LOCAL_TIME_ZONE = "Asia/Calcutta"

    class Config:
        case_sensitive = True
        env_file = "/config/environ/.env"


@lru_cache
def get_config():
    return Settings()
