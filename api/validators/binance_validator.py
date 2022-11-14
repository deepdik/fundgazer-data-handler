from datetime import date, datetime, time, timedelta
from typing import List

from pydantic import BaseModel, validator
from pydantic.class_validators import root_validator
from pydantic.config import Enum
from pydantic.fields import Field

from api.repository.binance_repo import retrieve_latest_ticker
from api.utils.datetime_convertor import convert_utc_to_local

CRYPTO_SYMBOLS = {"ETHBTC": "ETHBTCE", "LTCBTC": "LTCBTCE"}


class PriceTickerDataModel(BaseModel):
    """
    Price : (Non negative , non zero , float)
    Decimal place validation ( for stocks 2 , for crypto 8)
    For ticker data, new ticker should be in the x% range of previous ticker .(date should also be considered)
    Code checks for symbol name ( against default symbol list )
    """
    symbol: str = Field(required=True, min_length=1)
    price: float = Field(gt=0, required=True)

    @validator('price')
    def price_round(cls, value):
        print("pricer")
        return round(value, 8)

    @validator('symbol')
    def symbol_validation(cls, value):
        print("symbol")
        if not CRYPTO_SYMBOLS.get(value):
            raise ValueError(f"Symbol {value} not found")

    @root_validator(pre=False)
    def check(cls, values):
        #print(retrieve_latest_ticker(values["symbol"]))
        return values


class CandlestickDataModel(BaseModel):
    """
    Same TIMEZONE across all exchanges, symbols for any of the above data
    Same format  , like “YYYY-MM-DD” or “DD-MM-YYYY.”
    For candle data , date-time should not be missing for trading days. (consistency)
    For candle data,  date-time should not be repeated. => (check in Db for data with timestamp)
    For candle data , the latest candle date-time should be same for all symbols in symbol list.
    For candle data, length of historical candle data should be same for all symbols in symbol list.

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
    quote_asset_vol: float = Field(gt=0, required=True)
    no_of_trade: int = Field(gt=0, required=True)
    buy_base_asset_vol: float = Field(gt=0, required=True)
    buy_quote_asset_vol: float = Field(gt=0, required=True)

    @validator("open_time")
    def open_time_conversion(cls, value):
        return convert_utc_to_local(value)

    @validator("close_time")
    def close_time_conversion(cls, value):
        return convert_utc_to_local(value)

    @root_validator(pre=False)
    def check(cls, values):
        print(values["low_price"], values["high_price"])
        if values["high_price"] <= values["low_price"]:
            raise ValueError("Low Price should less than high price")

        if values["close_time"] < values["open_time"]:
            raise ValueError("Closed time should less than open time")

        return values


