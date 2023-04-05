from datetime import datetime

from api.models.fyers_models import FyersKline
from api.utils.datetime_convertor import get_current_local_time
from config.database.mongo import MongoManager
from fastapi.encoders import jsonable_encoder


async def save_fyers_candle_stick(data: FyersKline):
    print(f"valid upto {data.valid_upto}")
    database = await MongoManager.get_instance()
    query = {"symbol": data.symbol, "interval": data.interval}
    j_data = jsonable_encoder(data)
    update = {
        "$set": {
            "kline_data": j_data["kline_data"],
            "date_from": j_data["date_from"],
            "date_to": j_data["date_to"],
            "valid_upto": j_data["valid_upto"],
            "created_at": j_data["created_at"],
        }
    }

    await database.fyers_candle_stick.update_one(query, update, upsert=True)


async def get_candle_stick(symbols: list, interval: str, curr_time: datetime):
    database = await MongoManager.get_instance()
    query = {
        "symbol": {"$in": symbols},
        "interval": interval,
        # "valid_upto": {"$gte": str(curr_time)},
    }
    # print(await database.binance_candle_stick.count_documents({}))
    kline_data = await database.fyers_candle_stick.find(query, {"_id": 0}).to_list(1000)
    got_symbols = set()
    for data in kline_data:
        got_symbols.add(data["symbol"])
    return kline_data, got_symbols


async def save_fyers_access_token(data):
    print(data["valid_upto"])
    database = await MongoManager.get_instance()
    query = {"token": data["token"], "valid_upto": str(data["valid_upto"])}
    update = {"$set": query}
    await database.fyers_access_token.update_one({}, update, upsert=True)


async def get_fyers_access_token():
    database = await MongoManager.get_instance()
    query = {"valid_upto": {"$gt": str(get_current_local_time())}}
    data = await database.fyers_access_token.find(query).to_list(10)
    if data:
        return data[0]["token"]
