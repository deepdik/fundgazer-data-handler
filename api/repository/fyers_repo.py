from datetime import datetime

from api.models.fyers_models import FyersKline
from config.database.mongo import MongoManager
from fastapi.encoders import jsonable_encoder


async def save_fyers_candle_stick(data: FyersKline):
    database = await MongoManager.get_instance()
    query = {"symbol": data.symbol, "interval": data.interval}
    j_data = jsonable_encoder(data)
    update = {"$set":
                  {"kline_data": j_data["kline_data"],
                   "date_from": j_data["date_from"],
                   "date_to": j_data["date_to"],
                   "valid_upto": j_data["valid_upto"],
                   "created_at": j_data["created_at"]
                   }}

    await database.fyers_candle_stick.update_one(query, update, upsert=True)


async def get_candle_stick(symbols: list, interval: str, curr_time: datetime):
    database = await MongoManager.get_instance()
    query = {"symbol": {"$in": symbols}, "interval": interval, "valid_upto": {"$gte": str(curr_time)}}
    # print(await database.binance_candle_stick.count_documents({}))
    return await database.fyers_candle_stick.find(query).to_list(1000)