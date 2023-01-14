from datetime import datetime, timedelta
from typing import Optional

import pytz

from pydantic import BaseModel, validator
from pydantic.class_validators import root_validator
from pydantic.fields import Field

from api.utils.datetime_convertor import convert_utc_to_local, get_current_local_time


class PriceTickerValidator(BaseModel):
    """
    Price : (Non negative , non zero , float)
    Decimal place validation ( for stocks 2 , for crypto 8)
    For ticker data, new ticker should be in the x% range of previous ticker .(date should also be considered)
    Code checks for symbol name ( against default symbol list )
    """
    symbol: str = Field(required=True, min_length=1)
    price: float = Field(gt=0, required=True)
    last_updated: datetime = Field(required=False, default=get_current_local_time())

    @validator('price')
    def price_round(cls, value):
        return round(value, 8)

    class Config:
        validate_assignment = True


def validate_ticker_range(v_data, pre_data):
    """
    :param v_data:
    :param pre_data:
    :return:
    """
    for data in v_data:
        # get internal mapping symbol
        pre_price = next((item for item in pre_data if item["symbol"] == data["symbol"]), None)
        if pre_price:
            per_change = (float(pre_price["price"]) - data["price"]) / float(pre_price["price"]) * 100
            if abs(per_change) > 50:
                raise ValueError(f"Percentage change in price for {data['symbol']} is greater than permitted")


def get_symbol_mapping(v_data, symbol_mapping):
    for data in v_data:
        data.symbol = symbol_mapping[data.symbol]
    return v_data


class CandlestickDataModel(BaseModel):
    """
    Same TIMEZONE across all exchanges, symbols for any of the above data
    Same format  , like “YYYY-MM-DD” or “DD-MM-YYYY.”

    1499040000000,      // Kline open time
    "0.01634790",       // Open price
    "0.80000000",       // High price > low
    "0.01575800",       // Low price
    "0.01577100",       // Close price
    "148976.11427815",  // Volume > 0
    1499644799999,      // Kline Close time > Open time
    "2434.19055334",    // Quote asset volume > 0
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    open_time: datetime = Field(required=True)
    open_price: float = Field(gt=0, required=True)
    high_price: float = Field(gt=0, required=True)
    low_price: float = Field(gt=0, required=True)
    close_price: float = Field(gt=0, required=True)
    volume: float = Field(gt=0, required=True)
    close_time: datetime = Field(required=True)
    quote_asset_vol: Optional[float] = Field(gt=0, required=True)
    no_of_trade: Optional[int] = Field(gt=0, required=True)
    buy_base_asset_vol: Optional[float] = Field(gt=0, required=True)
    buy_quote_asset_vol: Optional[float] = Field(gt=0, required=True)

    @validator("open_time")
    def open_time_conversion(cls, value):
        return convert_utc_to_local(value)

    @validator("close_time")
    def close_time_conversion(cls, value):
        return convert_utc_to_local(value)

    @root_validator(pre=False)
    def check(cls, values):
        if values["high_price"] < values["low_price"]:
            raise ValueError("Low Price should less than high price")

        if values["close_time"] < values["open_time"]:
            raise ValueError("Closed time should be greater than open time")

        return values

    class Config:
        validate_assignment = True


def klineValidator(v_data, limit):
    """
    For candle data , date-time should not be missing for trading days. (consistency)-> No candle data interval should be missing
    For candle data,  date-time should not be repeated. => (check in Db for data with timestamp) -> duplicate candle with internval
    For candle data , the latest candle date-time should be same for all symbols in symbol list. -> open<curr<=closed
    For candle data, length of historical candle data should be same for all symbols in symbol list. -> length()

    :param v_data:
    :return:
    """
    if limit and len(v_data) != limit:
        raise ValueError(f"Length of data miss match (data-{len(v_data)} limit-{limit})")

    latest_candle = v_data[-1]
    local_dt = datetime.now()
    dt_utc = local_dt.astimezone(pytz.UTC)
    local_time = convert_utc_to_local(dt_utc)
    if not (latest_candle.open_time < local_time <= latest_candle.close_time):
        raise ValueError("Candle data is not latest")

    start = 0
    timedict = {}
    latest_time = local_time - timedelta(days=365)
    while start < len(v_data):
        if timedict.get(v_data[start].open_time) and timedict.get(v_data[start].open_time) == v_data[start].close_time:
            raise ValueError("duplicate candle found")
        else:
            timedict[v_data[start].open_time] = v_data[start].close_time

        if 1 < start:
            diff = v_data[start].open_time - v_data[start - 1].close_time
            if diff.total_seconds() > 1:
                raise ValueError("Some Candle data is missing")

        if latest_time < v_data[start].open_time:
            latest_time = v_data[start].open_time
        start += 1
