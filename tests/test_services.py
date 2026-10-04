import requests
import time


BASE_URLS = {
    "user": "http://localhost:8001",
    "product": "http://localhost:8002",
    "payment": "http://localhost:8003",
    "order": "http://localhost:8004",
}


def test_user_service_health():
    response = requests.get(
        f"{BASE_URLS['user']}/health",
        timeout=5
    )

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_product_service_health():
    response = requests.get(
        f"{BASE_URLS['product']}/health",
        timeout=5
    )

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_payment_service_health():
    response = requests.get(
        f"{BASE_URLS['payment']}/health",
        timeout=5
    )

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_order_service_health():
    response = requests.get(
        f"{BASE_URLS['order']}/health",
        timeout=5
    )

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_user_service_root():
    response = requests.get(
        f"{BASE_URLS['user']}/",
        timeout=5
    )

    assert response.status_code == 200
    assert response.json()["service"] == "User Service"


def test_product_service_root():
    response = requests.get(
        f"{BASE_URLS['product']}/",
        timeout=5
    )

    assert response.status_code == 200
    assert response.json()["service"] == "Product Service"


def test_payment_service_root():
    response = requests.get(
        f"{BASE_URLS['payment']}/",
        timeout=5
    )

    assert response.status_code == 200
    assert response.json()["service"] == "Payment Service"


def test_order_service_root():
    response = requests.get(
        f"{BASE_URLS['order']}/",
        timeout=5
    )

    assert response.status_code == 200
    assert response.json()["service"] == "Order Service"


def test_complete_ecommerce_workflow():

    # ------------------------------------------
    # 1. Create a new user
    # ------------------------------------------

    timestamp = int(time.time())

    user_data = {
        "name": "Automated Test User",
        "email": f"testuser{timestamp}@example.com",
        "password": "password123"
    }

    user_response = requests.post(
        f"{BASE_URLS['user']}/users/register",
        json=user_data,
        timeout=5
    )

    assert user_response.status_code == 200

    user = user_response.json()

    assert "id" in user
    assert user["email"] == user_data["email"]

    user_id = user["id"]

    # ------------------------------------------
    # 2. Create a product
    # ------------------------------------------

    product_data = {
        "name": f"Automated Test Laptop {timestamp}",
        "description": "Product created by automated integration test",
        "price": 50000,
        "category": "Electronics",
        "stock": 10
    }

    product_response = requests.post(
        f"{BASE_URLS['product']}/products",
        json=product_data,
        timeout=5
    )

    assert product_response.status_code == 200

    product = product_response.json()

    assert "id" in product
    assert product["price"] == 50000
    assert product["stock"] == 10

    product_id = product["id"]

    # ------------------------------------------
    # 3. Create an order
    # ------------------------------------------

    order_data = {
        "user_id": user_id,
        "product_id": product_id,
        "quantity": 2
    }

    order_response = requests.post(
        f"{BASE_URLS['order']}/orders",
        json=order_data,
        timeout=10
    )

    assert order_response.status_code == 200

    order = order_response.json()

    assert "id" in order
    assert order["user_id"] == user_id
    assert order["product_id"] == product_id
    assert order["quantity"] == 2
    assert order["total_price"] == 100000
    assert order["status"] == "pending_payment"

    order_id = order["id"]

    # ------------------------------------------
    # 4. Verify product stock was reduced
    # ------------------------------------------

    product_check_response = requests.get(
        f"{BASE_URLS['product']}/products/{product_id}",
        timeout=5
    )

    assert product_check_response.status_code == 200

    updated_product = product_check_response.json()

    assert updated_product["stock"] == 8

    # ------------------------------------------
    # 5. Create payment
    # ------------------------------------------

    payment_data = {
        "order_id": order_id,
        "user_id": user_id,
        "amount": 100000
    }

    payment_response = requests.post(
        f"{BASE_URLS['payment']}/payments",
        json=payment_data,
        timeout=10
    )

    assert payment_response.status_code == 200

    payment = payment_response.json()

    assert "id" in payment
    assert payment["order_id"] == order_id
    assert payment["user_id"] == user_id
    assert payment["amount"] == 100000
    assert payment["status"] == "success"

    # ------------------------------------------
    # 6. Verify order became PAID
    # ------------------------------------------

    order_check_response = requests.get(
        f"{BASE_URLS['order']}/orders/{order_id}",
        timeout=5
    )

    assert order_check_response.status_code == 200

    updated_order = order_check_response.json()

    assert updated_order["status"] == "paid"

    # ------------------------------------------
    # 7. Verify payment can be retrieved
    # ------------------------------------------

    payment_check_response = requests.get(
        f"{BASE_URLS['payment']}/payments/order/{order_id}",
        timeout=5
    )

    assert payment_check_response.status_code == 200

    stored_payment = payment_check_response.json()

    assert stored_payment["order_id"] == order_id
    assert stored_payment["status"] == "success"