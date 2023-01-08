from tests.test_binance_apis_client import client


def test_get_binance_ticker():
    params = {"symbols": ["QTUMUSDT"]}
    response = client.get("/api/v1/binance/ticker/price", params={})
    assert response.status_code == 422

    response = client.get("/api/v1/binance/ticker/price", params=params)
    assert response.status_code == 200


def test_get_binance_kline_client():
    """"""
    params = {"symbols": ["QTUMUSDT"], "interval": '1'}
    response = client.get("/api/v1/binance/kline", params={})
    assert response.status_code == 422

    response = client.get("/api/v1/binance/kline", params=params)
    assert response.status_code == 400

    params["interval"] = '1d'
    response = client.get("/api/v1/binance/kline", params=params)
    assert response.status_code == 200






