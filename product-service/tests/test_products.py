from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_root():

    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["service"] == "Product Service"
    assert response.json()["status"] == "running"


def test_health():

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_product():

    response = client.post(
        "/products",
        json={
            "name": "Laptop",
            "description": "Gaming Laptop",
            "price": 75000,
            "category": "Electronics",
            "stock": 10
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Laptop"
    assert data["price"] == 75000
    assert data["stock"] == 10


def test_get_products():

    response = client.get("/products")

    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_product():

    response = client.get("/products/1")

    assert response.status_code == 200
    assert response.json()["name"] == "Laptop"


def test_update_product():

    response = client.put(
        "/products/1",
        json={
            "name": "Gaming Laptop",
            "description": "High performance gaming laptop",
            "price": 80000,
            "category": "Electronics",
            "stock": 15
        }
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Gaming Laptop"
    assert response.json()["price"] == 80000


def test_update_stock():

    response = client.patch(
        "/products/1/stock?quantity=5"
    )

    assert response.status_code == 200
    assert response.json()["stock"] == 20


def test_delete_product():

    response = client.delete("/products/1")

    assert response.status_code == 200
    assert response.json()["message"] == "Product deleted successfully"