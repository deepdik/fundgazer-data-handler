import asyncio
import time

import aiohttp.web
import requests as requests

from api.models.general_models import APIMethodEnum
from api.utils.api_caller_util import request_url
from main import settings


async def async_api_caller(url: str, method: APIMethodEnum, params: dict = None,
                           data=None, retry=settings.ERROR_RETRY_COUNT):
    # TODO : can switch server if server realted issue
    if retry <= 0: return
    resp = {}
    status = False
    try:
        resp, status = await request_url(url, method, params, data)
    except aiohttp.web.HTTPTooManyRequests as e:
        print(e)
        print(f"Error - Remaining retry count => {retry - 1}")
        time.sleep(settings.HTTP_TOO_MANY_REQ_SLEEP)
        return await async_api_caller(url, method, params, data, retry - 1)

    except (aiohttp.web.HTTPRequestTimeout, aiohttp.web.HTTPGone,
            aiohttp.web.HTTPServerError) as e:
        print(e)
        print(f"Error -Remaining retry count => {retry - 1}")
        time.sleep(settings.HTTP_REQ_TIMEOUT_SLEEP)
        resp, status = await async_api_caller(url, method, params, data, retry - 1)

    except (asyncio.TimeoutError, aiohttp.http.HttpProcessingError,
            aiohttp.client_exceptions.ClientConnectorError) as e:
        print(e)
        print(f"Error -Remaining retry count => {retry - 1}")
        time.sleep(settings.ASYNC_TIMEOUT_SLEEP)
        resp, status = await async_api_caller(url, method, params, data, retry - 1)

    except Exception as e:
        print('Unknown exception Not handled in API caller wrapper - ', e)

    finally:
        print("Return from finally block")
        return resp, status
