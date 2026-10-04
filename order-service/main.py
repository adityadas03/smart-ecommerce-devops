from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from prometheus_fastapi_instrumentator import Instrumentator
from typing import List
import httpx
import os


app = FastAPI(
    title="Smart E-Commerce - Order Service",
    version="1.0.0"
)

Instrumentator().instrument(app).expose(app)


# ============================================================
# SERVICE URLS
# ============================================================

USER_SERVICE_URL = os.getenv(
    "USER_SERVICE_URL",
    "http://localhost:8001"
)

PRODUCT_SERVICE_URL = os.getenv(
    "PRODUCT_SERVICE_URL",
    "http://localhost:8002"
)


# ============================================================
# ORDER STATUS
# ============================================================

ORDER_STATUSES = [
    "pending_payment",
    "paid",
    "payment_failed",
    "cancelled"
]


# ============================================================
# DATA MODELS
# ============================================================

class OrderCreate(BaseModel):

    user_id: int = Field(
        ...,
        gt=0
    )

    product_id: int = Field(
        ...,
        gt=0
    )

    quantity: int = Field(
        ...,
        gt=0
    )


class Order(BaseModel):

    id: int

    user_id: int

    product_id: int

    quantity: int

    total_price: float

    status: str


# ============================================================
# TEMPORARY DATABASE
# ============================================================

orders: List[Order] = []

order_id_counter = 1


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "service": "Order Service",
        "status": "running",
        "version": "1.0.0"
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ============================================================
# CREATE ORDER
# ============================================================

@app.post(
    "/orders",
    response_model=Order
)
def create_order(
    order_data: OrderCreate
):

    global order_id_counter

    # ========================================================
    # CHECK USER SERVICE
    # ========================================================

    try:

        user_response = httpx.get(
            f"{USER_SERVICE_URL}/users/"
            f"{order_data.user_id}",
            timeout=5
        )

    except httpx.RequestError:

        raise HTTPException(
            status_code=503,
            detail="User Service is unavailable"
        )

    if user_response.status_code == 404:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user_response.status_code != 200:

        raise HTTPException(
            status_code=503,
            detail="User Service error"
        )

    # ========================================================
    # CHECK PRODUCT SERVICE
    # ========================================================

    try:

        product_response = httpx.get(
            f"{PRODUCT_SERVICE_URL}/products/"
            f"{order_data.product_id}",
            timeout=5
        )

    except httpx.RequestError:

        raise HTTPException(
            status_code=503,
            detail="Product Service is unavailable"
        )

    if product_response.status_code == 404:

        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if product_response.status_code != 200:

        raise HTTPException(
            status_code=503,
            detail="Product Service error"
        )

    product = product_response.json()

    # ========================================================
    # CHECK STOCK
    # ========================================================

    if product["stock"] < order_data.quantity:

        raise HTTPException(
            status_code=400,
            detail="Insufficient product stock"
        )

    # ========================================================
    # CALCULATE TOTAL PRICE
    # ========================================================

    total_price = (
        product["price"] *
        order_data.quantity
    )

    # ========================================================
    # RESERVE / REDUCE STOCK
    # ========================================================

    try:

        stock_response = httpx.patch(
            f"{PRODUCT_SERVICE_URL}/products/"
            f"{order_data.product_id}/stock"
            f"?quantity=-{order_data.quantity}",
            timeout=5
        )

    except httpx.RequestError:

        raise HTTPException(
            status_code=503,
            detail="Product Service is unavailable"
        )

    if stock_response.status_code != 200:

        raise HTTPException(
            status_code=400,
            detail="Unable to reserve product stock"
        )

    # ========================================================
    # CREATE ORDER
    # ========================================================

    new_order = Order(
        id=order_id_counter,
        user_id=order_data.user_id,
        product_id=order_data.product_id,
        quantity=order_data.quantity,
        total_price=total_price,
        status="pending_payment"
    )

    orders.append(new_order)

    order_id_counter += 1

    return new_order


# ============================================================
# GET ALL ORDERS
# ============================================================

@app.get(
    "/orders",
    response_model=List[Order]
)
def get_orders():

    return orders


# ============================================================
# GET SPECIFIC ORDER
# ============================================================

@app.get(
    "/orders/{order_id}",
    response_model=Order
)
def get_order(order_id: int):

    for order in orders:

        if order.id == order_id:

            return order

    raise HTTPException(
        status_code=404,
        detail="Order not found"
    )


# ============================================================
# UPDATE ORDER STATUS
# ============================================================

@app.patch(
    "/orders/{order_id}/status",
    response_model=Order
)
def update_order_status(
    order_id: int,
    status: str
):

    # --------------------------------------------------------
    # Validate status
    # --------------------------------------------------------

    if status not in ORDER_STATUSES:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid status. Allowed statuses: "
                f"{', '.join(ORDER_STATUSES)}"
            )
        )

    # --------------------------------------------------------
    # Find order
    # --------------------------------------------------------

    order = None

    for existing_order in orders:

        if existing_order.id == order_id:

            order = existing_order
            break

    if order is None:

        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # --------------------------------------------------------
    # Prevent invalid payment transition
    # --------------------------------------------------------

    if (
        status == "paid"
        and order.status != "pending_payment"
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Only pending_payment orders "
                "can become paid"
            )
        )

    # --------------------------------------------------------
    # Handle payment failure
    # --------------------------------------------------------

    if (
        status == "payment_failed"
        and order.status == "pending_payment"
    ):

        try:

            stock_response = httpx.patch(
                f"{PRODUCT_SERVICE_URL}/products/"
                f"{order.product_id}/stock"
                f"?quantity={order.quantity}",
                timeout=5
            )

        except httpx.RequestError:

            raise HTTPException(
                status_code=503,
                detail=(
                    "Product Service unavailable. "
                    "Stock could not be restored."
                )
            )

        if stock_response.status_code != 200:

            raise HTTPException(
                status_code=503,
                detail="Unable to restore product stock"
            )

    # --------------------------------------------------------
    # Update status
    # --------------------------------------------------------

    order.status = status

    return order