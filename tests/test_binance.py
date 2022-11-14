from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_binance_app():
    response = client.get("", headers={"X-Token": ""})
    assert response.status_code == 200
    assert response.json() == {}





