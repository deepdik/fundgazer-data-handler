from datetime import datetime
from typing import Union, List
from bson import ObjectId
from pydantic import BaseModel, Field
from api.utils.py_object import PyObjectId


class BinanceTicker(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    symbol: str
    price: float

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class KlineData(BaseModel):
    open_time: datetime = Field(required=True)
    open_price: float = Field(gt=0, required=True)
    high_price: float = Field(gt=0, required=True)
    low_price: float = Field(gt=0, required=True)
    close_price: float = Field(gt=0, required=True)
    volume: float = Field(gt=0, required=True)
    close_time: datetime = Field(required=True)
    quote_asset_vol: float = Field(gt=0, required=True)
    no_of_trade: int = Field(gt=0, required=True)
    buy_base_asset_vol: float = Field(gt=0, required=True)
    buy_quote_asset_vol: float = Field(gt=0, required=True)


class BinanceKline(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    kline_data: Union[List[KlineData]]
    symbol: str
    created_at: datetime
    updated_at: datetime
    interval: str
    valid_upto: datetime

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
