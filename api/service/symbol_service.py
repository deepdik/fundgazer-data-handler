import json


async def get_supported_symbol_mapping():
    with open('api/utils/supported_symbols.json', "r") as f:
        data = json.loads(f.read())
    return data
