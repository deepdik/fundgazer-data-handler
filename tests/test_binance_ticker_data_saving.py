
import pytest
from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

from api.service.binance_service import save_price_ticker_service


@pytest.mark.asyncio
async def test_binance_ticker_save_with_unsupported_symbol():
    """"""
    symbols = "QSDT"
    resp = await save_price_ticker_service(symbols)
    assert resp["success"] == False


@pytest.mark.asyncio
async def test_binance_ticker_save_with_supported_symbol():
    """"""
    symbols = "QTUMUSDT"
    resp = await save_price_ticker_service(symbols)
    assert resp["success"] == True
