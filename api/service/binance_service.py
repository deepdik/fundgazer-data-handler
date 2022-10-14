from typing import List

from pydantic.error_wrappers import ValidationError
from pydantic.tools import parse_obj_as

from api.validators.binance_validator import PriceTickerDataModel, CandlestickDataModel


async def price_ticker_service(resp: List[PriceTickerDataModel]):
    try:
        data = parse_obj_as(List[PriceTickerDataModel], resp)
        return data
    except ValidationError as e:
        print(e)


async def candle_stick_service(candle_data: List[CandlestickDataModel]):
    try:
        dict_data = []
        fields = CandlestickDataModel.__fields__.keys()

        for data in candle_data:
            dict_data.append(dict(zip(fields, candle_data[0])))

        data = parse_obj_as(List[CandlestickDataModel], dict_data)
        # data = CandlestickDataModel.parse_obj(resp)
        return data
    except ValidationError as e:
        print(e)


