import pytest
from fastapi.testclient import TestClient

from api.service.symbol_service import get_supported_symbol_mapping
from main import app

client = TestClient(app)

from api.validators.binance_validator import PriceTickerValidator, validate_ticker_range


def test_binance_ticker_round_price():
    """
    """
    data = {"symbol": "XYZ", "price": 10.022293939393}
    # Decimal place validation (for crypto 8)
    v_data = PriceTickerValidator(**data)
    assert v_data.symbol == 'XYZ'
    assert len(str(v_data.price).split(".")[1]) == 8


def test_binance_ticker_min_price():
    # Price : (Non negative , non zero , float)
    data = {"symbol": "XYZ", "price": -10.022293939393}
    with pytest.raises(ValueError) as error:
        PriceTickerValidator(**data)

    data = {"symbol": "XYZ", "price": 0}
    with pytest.raises(ValueError) as error:
        PriceTickerValidator(**data)


@pytest.mark.asyncio
async def test_binance_ticker_symbol_list():
    data = {"symbol": "XYZ", "price": 10.022293939393}
    # Code checks for symbol name ( against default symbol list )
    supp_symbols_list = await get_supported_symbol_mapping()
    supported_symbol = "ETCUSDT"
    not_supported_symbol = 'XYZ'
    assert supp_symbols_list.get(supported_symbol).get("binance") == "ETCUSDT"
    assert supp_symbols_list.get(not_supported_symbol, {}).get("binance") is None


def test_validate_ticker_range():
    """
    # For ticker data, new ticker should be in the x% range of previous ticker
    # (date should also be considered)
    """
    data = [{"symbol": "XYZ", "price": 10.022293939393}]
    new_data = [{"symbol": "XYZ", "price": 10.022293939393}]
    new_error_data = [{"symbol": "XYZ", "price": 50.022293939393}]

    # should give error
    with pytest.raises(ValueError) as error:
        validate_ticker_range(data, new_error_data)

    # should not give error
    assert validate_ticker_range(data, new_data) is None


