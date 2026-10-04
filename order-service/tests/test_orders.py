from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root():

    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["service"] == "Order Service"
    assert response.json()["status"] == "running"


def test_health():

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_orders():

    response = client.get("/orders")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_nonexistent_order():

    response = client.get("/orders/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"