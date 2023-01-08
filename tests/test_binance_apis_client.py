
import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

from api.utils.api_client.third_party.binance_client import binance_ticker_client, binance_kline_client


@pytest.mark.asyncio
async def test_binance_kline_client():
    """"""
    symbols = ["QTUMUSDT"]
    resp, status = await binance_ticker_client(symbols)
    assert status == True


@pytest.mark.asyncio
async def test_binance_ticker_client():
    """"""
    symbols = "QTUMUSDT"
    interval = '1d'
    limit = 1000
    resp, status = await binance_kline_client(symbols, '1', limit)
    assert status == False

    resp, status = await binance_kline_client(symbols, interval, limit)
    assert status == True


