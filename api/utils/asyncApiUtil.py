import asyncio
from typing import List, Dict

import aiohttp


async def get_url(session: aiohttp.ClientSession, url: str) -> Dict:
    async with session.get(url) as response:
        return await response.json()


async def request_multiple_urls(urls: List[str]):
    async with aiohttp.ClientSession() as session:
        tasks: List[asyncio.Task] = []
        for url in urls:
            tasks.append(
                asyncio.ensure_future(
                    get_url(session, url)
                )
            )
        return await asyncio.gather(*tasks)


async def get_request_url(url: str, params: dict = {}):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.json()




