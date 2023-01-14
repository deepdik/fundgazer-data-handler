from datetime import datetime
from typing import List, Union
from config.database.mongo import MongoManager
from pymongo import InsertOne, DeleteMany, ReplaceOne, UpdateOne, UpdateMany
from config.config import get_config

setting = get_config()


async def save_binance_ticker(data):
    database = await MongoManager.get_instance()

    if isinstance(data, list):
        for obj in data:
            query = {"symbol": obj["symbol"]}
            update = {"$set": obj}
            await database.binance_ticker.update_one(query, update, upsert=True)
    elif isinstance(data, dict):
        query = {"symbol": data["symbol"]}
        update = {"$set": data}
        await database.binance_ticker.update_one(query, update, upsert=True)
    else:
        raise ValueError("Invalid data for saving")


async def retrieve_latest_ticker(symbol: list):
    database = await MongoManager.get_instance()
    #await database.binance_ticker.drop()
    return await database.binance_ticker.find({"symbol": {"$in": symbol}}).to_list(1000)


async def save_candle_stick(data):
    database = await MongoManager.get_instance()
    query = {"symbol": data["symbol"], "interval": data["interval"]}
    update = {"$set":
                  {"kline_data": data["kline_data"],
                   "updated_at": data["updated_at"],
                   "valid_upto": data["valid_upto"],
                   "created_at": data["created_at"]
                   }}
    # requests = [
    #     UpdateOne(query, {"$pull": {"kline_data": {"open_time": {"$gte": latest_time}}}}),
    #     UpdateOne(query, {"$push": {'kline_data': data["kline_data"]}})
    # ]
    #await database.binance_candle_stick.drop()
    await database.binance_candle_stick.update_one(query, update, upsert=True)


async def get_candle_stick(symbols: list, interval: str, curr_time: datetime):
    print(symbols)
    database = await MongoManager.get_instance()
    print(curr_time)
    query = {"symbol": {"$in": symbols}, "interval": interval, "valid_upto": {"$gte": str(curr_time)}}
    # print(await database.binance_candle_stick.count_documents({}))
    return await database.binance_candle_stick.find(query).to_list(1000)


async def retrieve_candle_stick(data):
    database = await MongoManager.get_instance()
    if isinstance(data, list):
        await database.binance_candle_stick.insert_many(data)
    elif isinstance(data, dict):
        await database.binance_candle_stick.insert_one(data)
    else:
        raise ValueError("Invalid data for saving")
