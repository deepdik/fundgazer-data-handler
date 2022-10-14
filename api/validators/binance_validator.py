from datetime import date, datetime, time, timedelta

from pydantic import BaseModel, validator
from pydantic.config import Enum
from pydantic.datetime_parse import timezone
from pydantic.fields import Field


class CryptoEnum(str, Enum):
    """
    """
    ETHBTC = 'ETHBTC'
    BANANA = 'banana'
    MELON = 'melon'


class PriceTickerDataModel(BaseModel):
    """
    Price : ( non negative , non zero , float)
    Decimal place validation ( for stocks 2 , for crypto 8)
    For ticker data, new ticker should be in the x% range of previous ticker .
    Code checks for symbol name ( against default symbol list )
    """
    symbol: str = Field(required=True, min_length=1)
    price: float = Field(gt=0, required=True)

    @validator('price')
    def price_round(cls, v):
        return round(v, 8)

    # @validator('symbol')
    # def symbol_check(cls, v):
    #     if v not in ["ETHBTC"]:
    #         return None

    # @pydantic.root_validator(pre=False)
    # def check(cls, values):
    #     print(values)
    #     if values['symbol'] is None:
    #         del values
    #     return {}

    # @validator('float')
    # def passwords_match(cls, v, values, **kwargs):
    #     if 'password1' in values and v != values['password1']:
    #         raise ValueError('passwords do not match')
    #     return v


class CandlestickDataModel(BaseModel):
    """
    Same TIMEZONE across all exchanges, symbols for any of the above data
    Same format  , like “YYYY-MM-DD” or “DD-MM-YYYY.”
    For candle data , date-time should not be missing for trading days. ( consistency)
    For candle data,  date-time should not be repeated .
    For candle data , the latest candle date-time should be same for all symbols in symbol list
    For candle data, length of historical candle data should be same for all symbols in symbol list.

    1499040000000,      // Kline open time
    "0.01634790",       // Open price
    "0.80000000",       // High price
    "0.01575800",       // Low price
    "0.01577100",       // Close price
    "148976.11427815",  // Volume
    1499644799999,      // Kline Close time
    "2434.19055334",    // Quote asset volume
    308,                // Number of trades
    "1756.87402397",    // Taker buy base asset volume
    "28.46694368",      // Taker buy quote asset volume
    "0"                 // Unused field, ignore.

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    open_time: datetime = Field(required=True, tzinfo=timezone.utc)
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


    # @validator("dt", pre=True)
    # def dt_validate(cls, dt):
    #     return datetime.fromtimestamp(dt)
