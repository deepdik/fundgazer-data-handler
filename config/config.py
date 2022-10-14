from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Data handler API"

    class Config:
        env_file = "environ/.env"

