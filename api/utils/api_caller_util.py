import asyncio
import json
from typing import List, Dict

import aiohttp
import requests as requests

from api.models.general_models import APIMethodEnum


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


async def request_url(url: str, method: APIMethodEnum, params: dict = None, data=None):
    json_response = None
    status_code = 0
    async with aiohttp.ClientSession() as session:
        if method == APIMethodEnum.GET:
            async with session.get(url, params=params) as resp:
                json_response = await resp.json()
                if resp.ok:
                    return json_response, resp.ok
                status_code = resp.status

        elif method == APIMethodEnum.POST:
            async with session.post(url, data=data) as resp:
                json_response = await resp.json()
                if resp.ok:
                    return json_response, resp.ok
                status_code = resp.status

    if status_code == 429:
        print(f"Error response => {json_response}")
        raise aiohttp.web.HTTPTooManyRequests
    elif status_code == 408:
        print(f"Error response => {json_response}")
        raise aiohttp.web.HTTPRequestTimeout
    elif status_code == 410:
        print(f"Error response => {json_response}")
        raise aiohttp.web.HTTPGone
    elif status_code >= 500:
        print(f"Error response => {json_response}")
        raise aiohttp.web.HTTPServerError
    else:
        return json_response, False

