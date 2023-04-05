import json

# from config.database.mongo import MongoManager


async def get_supported_symbol_mapping():
    with open("api/utils/supported_symbols.json", "r") as f:
        data = json.loads(f.read())
    return data
    # database = await MongoManager.get_instance()
    # data = await database.symbol_mapping.find({}, {"_id": 0}).to_list(1000)
    # symb_list = {}
    # for symb in data:
    #     symb_list.update(symb)
    # return symb_list
