from api.models.celery_models import DataRefreshRetryQueue
from api.models.general_models import Platforms
from config.database.mongo import MongoManager
from fastapi.encoders import jsonable_encoder


async def data_refresh_retry_queue(data: DataRefreshRetryQueue, method):
    database = await MongoManager.get_instance()
    if method == "GET_ALL":
        return await database.data_refresh_retry_queue.find({}).to_list(1000)

    elif method == "SAVE":
        query = {
            "symbol": data.symbol,
            "exchange": data.exchange,
            "interval": data.interval,
        }
        # search in db
        retry_data = await database.data_refresh_retry_queue.find_one(query)
        if retry_data:
            if retry_data["retry_count"] + 1 == retry_data["max_retry"]:
                # delete from queue
                await database.data_refresh_retry_queue.delete_one(query)
            else:
                update = {"$set": {"retry_count": retry_data["retry_count"] + 1}}
                await database.data_refresh_retry_queue.update_one(
                    query, update, upsert=True
                )
        else:
            await database.data_refresh_retry_queue.insert_one(jsonable_encoder(data))


async def get_data_refresh_retry_status(symbols, interval, exchange: Platforms):
    database = await MongoManager.get_instance()
    query = {"symbol": {"$in": symbols}, "exchange": exchange, "interval": interval}
    data = await database.data_refresh_retry_queue.find(query).to_list(1000)
    if not data:
        return False
    elif len(data) == len(symbols):
        return True
    else:
        return False


async def delete_data_refresh_retry_queue(symbol, exchange, interval):
    print(f"deleting from Queue {symbol}, {exchange}, {interval}")
    database = await MongoManager.get_instance()
    query = {"symbol": symbol, "exchange": exchange, "interval": interval}
    await database.data_refresh_retry_queue.delete_one(query)
