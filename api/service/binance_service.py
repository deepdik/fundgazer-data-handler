from typing import List

from pydantic.error_wrappers import ValidationError
from pydantic.tools import parse_obj_as

from api.repository.binance_repo import save_binance_ticker
from api.validators.binance_validator import PriceTickerDataModel, CandlestickDataModel
from utils.logger import logger_config

logger = logger_config(__name__)


async def price_ticker_service(data: List[PriceTickerDataModel]):
    try:
        await save_binance_ticker(data)
    except ValidationError as e:
        logger.error(e)
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
        logger.error(e)
        print(e)


