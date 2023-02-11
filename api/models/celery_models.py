from datetime import date
from typing import Optional

from pydantic.fields import Field
from pydantic.main import BaseModel

from api.models.general_models import Platforms
from api.utils.py_object import PyObjectId
from bson import ObjectId


class DataRefreshRetryQueue(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    max_retry: int
    symbol: str
    retry_count: int
    cron_syntax: str
    exchange: Platforms
    interval: str
    date_from: Optional[date]
    date_to: Optional[date]

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
