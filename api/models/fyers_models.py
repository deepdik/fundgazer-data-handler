from datetime import datetime, date
from typing import Union, List

from pydantic.fields import Field
from pydantic.main import BaseModel
from bson import ObjectId

from api.utils.py_object import PyObjectId


class KlineData(BaseModel):
    open_time: datetime = Field(required=True)
    open_price: float = Field(gt=0, required=True)
    high_price: float = Field(gt=0, required=True)
    low_price: float = Field(gt=0, required=True)
    close_price: float = Field(gt=0, required=True)
    volume: float = Field(gt=0, required=True)


class FyersKline(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    kline_data: Union[List[KlineData]]
    symbol: str
    created_at: datetime
    date_from: date
    date_to: date
    interval: str
    valid_upto: datetime

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
