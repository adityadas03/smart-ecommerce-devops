from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_root():

    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["service"] == "Payment Service"
    assert response.json()["status"] == "running"


def test_health():

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_payments():

    response = client.get("/payments")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_payment():

    response = client.post(
        "/payments",
        json={
            "order_id": 1,
            "user_id": 1,
            "amount": 150000
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["order_id"] == 1
    assert data["user_id"] == 1
    assert data["amount"] == 150000
    assert data["status"] == "success"


def test_duplicate_payment():

    response = client.post(
        "/payments",
        json={
            "order_id": 1,
            "user_id": 1,
            "amount": 150000
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Payment already exists for this order"
    )


def test_get_payment():

    response = client.get("/payments/1")

    assert response.status_code == 200

    assert response.json()["order_id"] == 1


def test_get_payment_by_order():

    response = client.get("/payments/order/1")

    assert response.status_code == 200

    assert response.json()["order_id"] == 1


def test_nonexistent_payment():

    response = client.get("/payments/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Payment not found"


def test_nonexistent_order_payment():

    response = client.get("/payments/order/999")

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Payment not found for this order"
    )


def test_invalid_amount():

    response = client.post(
        "/payments",
        json={
            "order_id": 2,
            "user_id": 1,
            "amount": 0
        }
    )

    assert response.status_code == 422


def test_invalid_order_id():

    response = client.post(
        "/payments",
        json={
            "order_id": 0,
            "user_id": 1,
            "amount": 1000
        }
    )

    assert response.status_code == 422


def test_invalid_user_id():

    response = client.post(
        "/payments",
        json={
            "order_id": 2,
            "user_id": 0,
            "amount": 1000
        }
    )

    assert response.status_code == 422