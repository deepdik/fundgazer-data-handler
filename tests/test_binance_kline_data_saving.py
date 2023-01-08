
import pytest
from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

from api.service.binance_service import save_candle_stick_service


@pytest.mark.asyncio
async def test_binance_kline_save_with_unsupported_symbol():
    """"""
    symbols = "QSDT"
    resp = await save_candle_stick_service(symbols, 'binance', '1d')
    assert resp["success"] == False


@pytest.mark.asyncio
async def test_binance_kline_save_with_supported_symbol():
    """"""
    symbols = "QTUMUSDT"
    resp = await save_candle_stick_service(symbols, 'binance', '1d')
    assert resp["success"] == True


@pytest.mark.asyncio
async def test_binance_kline_save_with_invalid_interval():
    """"""
    symbols = "QTUMUSDT"
    resp = await save_candle_stick_service(symbols, 'binance', '1T')
    assert resp["success"] == False