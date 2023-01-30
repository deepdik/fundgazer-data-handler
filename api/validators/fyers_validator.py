from datetime import date, datetime
from typing import Optional

from pydantic.class_validators import validator, root_validator
from pydantic.fields import Field
from pydantic.main import BaseModel

from api.utils.datetime_convertor import convert_utc_to_local


class SaveStockQueryValidator(BaseModel):
    """
symbols, date_from: date, date_to: date, resolution
    """
    symbols: str = Field(required=True, min_length=1)
    interval: str = Field(required=True)
    date_from: date = Field(required=True)
    date_to: date = Field(required=True)

    @validator('symbols')
    def symbols_break(cls, value):
        return value.split(",")

    @validator('interval')
    def interval_validate(cls, value):
        """
        1 minute : “1”
        2 minute : “2"
        3 minute : "3"
        5 minute : "5"
        10 minute : "10"
        15 minute : "15"
        20 minute : "20"
        30 minute : "30"
        60 minute : "60"
        120 minute : "120"
        240 minute : "240"
        """
        if value not in ["1", "2", "3", "5", "10", "15", "20", "30",
                         "60", "120", "240", "D"]:
            raise ValueError("Invalid Interval value")
        return value

    @validator('date_from')
    def date_from_validate(cls, value):
        try:
            bool(datetime.strptime(str(value), "%Y-%m-%d"))
            return value
        except ValueError:
            raise ValueError("Invalid date form. Shloud be in YYYY-MM-DD")

    @validator('date_to')
    def date_to_validate(cls, value):
        try:
            bool(datetime.strptime(str(value), "%Y-%m-%d"))
            return value
        except ValueError:
            raise ValueError("Invalid date form. Shloud be in YYYY-MM-DD")

    class Config:
        validate_assignment = True


class FyersCandlestickDataModel(BaseModel):
    """
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    open_time: datetime = Field(required=True)
    open_price: float = Field(gt=0, required=True)
    high_price: float = Field(gt=0, required=True)
    low_price: float = Field(gt=0, required=True)
    close_price: float = Field(gt=0, required=True)
    volume: float = Field(gt=0, required=True)

    @validator("open_time")
    def open_time_conversion(cls, value):
        return convert_utc_to_local(value)

    @root_validator(pre=False)
    def check(cls, values):
        if values["high_price"] < values["low_price"]:
            raise ValueError("Low Price should less than high price")

        return values

    class Config:
        validate_assignment = True


class GetStockParamsValidator(BaseModel):
    """
symbols, date_from: date, date_to: date, resolution
    """
    symbols: str = Field(required=True, min_length=1)
    interval: str = Field(required=True)

    @validator('symbols')
    def symbols_break(cls, value):
        return value.split(",")

    @validator('interval')
    def interval_validate(cls, value):
        if value not in ["1", "2", "3", "5", "10m", "15", "20", "30",
                         "60", "120", "240", "D"]:
            raise ValueError("Invalid Interval value")
        return value

    class Config:
        validate_assignment = True


class StockPriceTickerValidator(BaseModel):
    """
    Price : (Non negative , non zero , float)
    Decimal place validation ( for stocks 2)
    For ticker data, new ticker should be in the x% range of previous ticker .(date should also be considered)
    Code checks for symbol name ( against default symbol list )
    """
    symbol: str = Field(required=True, min_length=1)
    price: float = Field(gt=0, required=True)

    @validator('price')
    def price_round(cls, value):
        return round(value, 2)

    class Config:
        validate_assignment = True