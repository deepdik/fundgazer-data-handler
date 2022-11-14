from typing import List, Union

from config.database.mongo import MongoManager


async def save_binance_ticker(data):
    database = await MongoManager.get_instance()
    if isinstance(data, list):
        await database.binance_ticker_collection.insert_many(data)
    elif isinstance(data, dict):
        await database.binance_ticker_collection.insert_one(data)
    else:
        raise ValueError("Invalid data for saving")


async def retrieve_latest_ticker(symbol: str):
    database = await MongoManager.get_instance()
    data = await database.binance_ticker_collection.getLastInsertedDocument.find(
        {"symbol": symbol}).sort({"_id": -1}).limit(1)
    return data


async def save_candle_stick(data):
    database = await MongoManager.get_instance()
    if isinstance(data, list):
        await database.binance_candle_stick_collection.insert_many(data)
    elif isinstance(data, dict):
        await database.binance_candle_stick_collection.insert_one(data)
    else:
        raise ValueError("Invalid data for saving")
