from datetime import datetime
from typing import List

import pytest
from fastapi.testclient import TestClient
from pydantic.tools import parse_obj_as

from main import app

client = TestClient(app)

from api.validators.binance_validator import CandlestickDataModel, klineValidator


def test_binance_kline_date_zone():
    """
    """
    data = {
        "open_time": 1669586400000,
        "open_price": "0.07332000",
        "high_price": "0.07340000",
        "low_price": "0.07329900",
        "close_price": "0.07337600",
        "volume": "1541.98130000",
        "close_time": 1669589999999,
    }
    v_data = CandlestickDataModel(**data)
    # Same TIMEZONE across all exchanges, symbols for any of the above data
    assert v_data.open_time.tzname() == "IST"
    assert v_data.close_time.tzname() == 'IST'


def test_binance_kline_date_format():
    data = {
        "open_time": 1669586400000,
        "open_price": "0.07332000",
        "high_price": "0.07340000",
        "low_price": "0.07329900",
        "close_price": "0.07337600",
        "volume": "1541.98130000",
        "close_time": 1669589999999,
    }
    v_data = CandlestickDataModel(**data)
    # Same format  , like “YYYY-MM-DD” or “DD-MM-YYYY.”
    datetime.strptime(str(v_data.close_time.date()), '%Y-%m-%d')

    with pytest.raises(ValueError) as error:
        datetime.strptime(str(v_data.close_time.date()), '%m-%d-%Y')


def test_binance_kline_open_close_date():
    data = {
        "open_time": 1669586400000,
        "open_price": "0.07332000",
        "high_price": "0.07340000",
        "low_price": "0.07329900",
        "close_price": "0.07337600",
        "volume": "1541.98130000",
        "close_time": 1669589999999,
    }
    v_data = CandlestickDataModel(**data)
    # Closed time should be greater than open time
    data["close_time"] = 10000000
    with pytest.raises(ValueError) as error:
        CandlestickDataModel(**data)


def test_binance_kline_low_high_price():
    """
    """
    data = {
        "open_time": 1669586400000,
        "open_price": "0.07332000",
        "high_price": "0.07340000",
        "low_price": "0.07329900",
        "close_price": "0.07337600",
        "volume": "1541.98130000",
        "close_time": 1669589999999,
    }
    v_data = CandlestickDataModel(**data)

    # Low Price should less than high price
    with pytest.raises(ValueError) as error:
        v_data.low_price = "0.07340001"


def test_binance_kline_min_price():
    data = {
        "open_time": 1669586400000,
        "open_price": "0.07332000",
        "high_price": "0.07340000",
        "low_price": "0.07329900",
        "close_price": "0.07337600",
        "volume": "1541.98130000",
        "close_time": 1669589999999,
    }
    v_data = CandlestickDataModel(**data)
    # price can't be negative
    with pytest.raises(ValueError) as error:
        v_data.low_price = "-0.9999"

    # price can't be negative
    with pytest.raises(ValueError) as error:
        v_data.open_price = "-0.9999"

    # price can't be negative
    with pytest.raises(ValueError) as error:
        v_data.high_price = "-0.9999"


def test_binance_ticker_vol():
    # vol can't be negative
    data = {
        "open_time": 1669586400000,
        "open_price": "0.07332000",
        "high_price": "0.07340000",
        "low_price": "0.07329900",
        "close_price": "0.07337600",
        "volume": "1541.98130000",
        "close_time": 1669589999999,
    }
    v_data = CandlestickDataModel(**data)
    with pytest.raises(ValueError) as error:
        v_data.volume = "-0.9999"


def test_kline_data_length():
    """
    For candle data, length of historical candle data should be same for all
    symbols in symbol list. -> length()
    """
    data = [{
        "open_time": 1669586400000,
        "open_price": "0.07332000",
        "high_price": "0.07340000",
        "low_price": "0.07329900",
        "close_price": "0.07337600",
        "volume": "1541.98130000",
        "close_time": 1669589999999,
    }]
    limit = 2
    with pytest.raises(ValueError) as error:
        klineValidator(data, limit)


def test_kline_interval():
    """
    #For candle data , date-time should not be missing for trading days. (consistency)
    # No candle data interval should be missing
    """
    data = [{
            "open_time": 1672876800000,
            "open_price": "0.07332000",
            "high_price": "0.07340000",
            "low_price": "0.07329900",
            "close_price": "0.07337600",
            "volume": "1541.98130000",
            "close_time": 1672963199999,
        },
        {
            "open_time": 1672963200000,
            "open_price": "0.07332000",
            "high_price": "0.07340000",
            "low_price": "0.07329900",
            "close_price": "0.07337600",
            "volume": "1541.98130000",
            "close_time": 1673049599999,
        },
        {
            "open_time": 1673136000000,
            "open_price": "0.07332000",
            "high_price": "0.07340000",
            "low_price": "0.07329900",
            "close_price": "0.07337600",
            "volume": "1541.98130000",
            "close_time": 9673206870,
        }
    ]

    limit = 3
    data = parse_obj_as(List[CandlestickDataModel], data)
    with pytest.raises(ValueError) as error:
        klineValidator(data, limit)


def test_kline_duplicate_data():
    """
    For candle data,  date-time should not be repeated.
    duplicate candle with interval
    """
    data = [{
            "open_time": 1669608000000,
            "open_price": "0.07332000",
            "high_price": "0.07340000",
            "low_price": "0.07329900",
            "close_price": "0.07337600",
            "volume": "1541.98130000",
            "close_time": 9673206870,
        },
        {
            "open_time": 1669608000000,
            "open_price": "0.07332000",
            "high_price": "0.07340000",
            "low_price": "0.07329900",
            "close_price": "0.07337600",
            "volume": "1541.98130000",
            "close_time": 9673206870,
        }
    ]

    limit = 2
    data = parse_obj_as(List[CandlestickDataModel], data)
    with pytest.raises(ValueError) as error:
        klineValidator(data, limit)


def test_kline_data_datetime():
    """
    For candle data, the latest candle date-time
    should be same for all symbols in symbol list. -> open<curr<=closed
    """
    data = [{
            "open_time": 1669608000000,
            "open_price": "0.07332000",
            "high_price": "0.07340000",
            "low_price": "0.07329900",
            "close_price": "0.07337600",
            "volume": "1541.98130000",
            "close_time": 1669611599999,
        },
        {
            "open_time": 1669611600000,
            "open_price": "0.07332000",
            "high_price": "0.07340000",
            "low_price": "0.07329900",
            "close_price": "0.07337600",
            "volume": "1541.98130000",
            "close_time": 1669615199999,
        }
    ]
    limit = 2
    data = parse_obj_as(List[CandlestickDataModel], data)
    with pytest.raises(ValueError) as error:
        klineValidator(data, limit)