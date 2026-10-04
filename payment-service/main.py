from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from prometheus_fastapi_instrumentator import Instrumentator
from typing import List
from enum import Enum
import httpx
import os


app = FastAPI(
    title="Smart E-Commerce - Payment Service",
    version="1.0.0"
)

Instrumentator().instrument(app).expose(app)


# ============================================================
# SERVICE CONFIGURATION
# ============================================================

ORDER_SERVICE_URL = os.getenv(
    "ORDER_SERVICE_URL",
    "http://localhost:8004"
)


# ============================================================
# PAYMENT STATUS
# ============================================================

class PaymentStatus(str, Enum):

    PENDING = "pending"

    SUCCESS = "success"

    FAILED = "failed"


# ============================================================
# REQUEST MODEL
# ============================================================

class PaymentCreate(BaseModel):

    order_id: int = Field(
        ...,
        gt=0
    )

    user_id: int = Field(
        ...,
        gt=0
    )

    amount: float = Field(
        ...,
        gt=0
    )


# ============================================================
# RESPONSE MODEL
# ============================================================

class Payment(BaseModel):

    id: int

    order_id: int

    user_id: int

    amount: float

    status: PaymentStatus


# ============================================================
# TEMPORARY DATABASE
# ============================================================

payments: List[Payment] = []

payment_id_counter = 1


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "service": "Payment Service",
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
# CREATE PAYMENT
# ============================================================

@app.post(
    "/payments",
    response_model=Payment
)
def create_payment(
    payment_data: PaymentCreate
):

    global payment_id_counter

    # --------------------------------------------------------
    # Check duplicate payment
    # --------------------------------------------------------

    for existing_payment in payments:

        if existing_payment.order_id == payment_data.order_id:

            raise HTTPException(
                status_code=400,
                detail="Payment already exists for this order"
            )

    # --------------------------------------------------------
    # Verify order exists
    # --------------------------------------------------------

    try:

        order_response = httpx.get(
            f"{ORDER_SERVICE_URL}/orders/{payment_data.order_id}",
            timeout=5
        )

    except httpx.RequestError:

        raise HTTPException(
            status_code=503,
            detail="Order Service is unavailable"
        )

    if order_response.status_code == 404:

        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order_response.status_code != 200:

        raise HTTPException(
            status_code=503,
            detail="Order Service error"
        )

    order = order_response.json()

    # --------------------------------------------------------
    # Verify user matches order
    # --------------------------------------------------------

    if order["user_id"] != payment_data.user_id:

        raise HTTPException(
            status_code=400,
            detail="User does not match the order"
        )

    # --------------------------------------------------------
    # Verify amount
    # --------------------------------------------------------

    if abs(
        order["total_price"] - payment_data.amount
    ) > 0.01:

        raise HTTPException(
            status_code=400,
            detail="Payment amount does not match order total"
        )

    # --------------------------------------------------------
    # Verify order status
    # --------------------------------------------------------

    if order["status"] != "pending_payment":

        raise HTTPException(
            status_code=400,
            detail=(
                "Payment can only be made for "
                "orders with pending_payment status"
            )
        )

    # --------------------------------------------------------
    # Create payment
    # --------------------------------------------------------

    payment = Payment(
        id=payment_id_counter,
        order_id=payment_data.order_id,
        user_id=payment_data.user_id,
        amount=payment_data.amount,
        status=PaymentStatus.SUCCESS
    )

    payments.append(payment)

    payment_id_counter += 1

    # --------------------------------------------------------
    # Update order status
    # --------------------------------------------------------

    try:

        status_response = httpx.patch(
            f"{ORDER_SERVICE_URL}/orders/"
            f"{payment_data.order_id}/status"
            f"?status=paid",
            timeout=5
        )

    except httpx.RequestError:

        # Payment was created, but order update failed
        raise HTTPException(
            status_code=503,
            detail=(
                "Payment created but Order Service "
                "could not be updated"
            )
        )

    if status_response.status_code != 200:

        raise HTTPException(
            status_code=503,
            detail=(
                "Payment created but order status "
                "could not be updated"
            )
        )

    return payment


# ============================================================
# GET ALL PAYMENTS
# ============================================================

@app.get(
    "/payments",
    response_model=List[Payment]
)
def get_payments():

    return payments


# ============================================================
# GET PAYMENT
# ============================================================

@app.get(
    "/payments/{payment_id}",
    response_model=Payment
)
def get_payment(payment_id: int):

    for payment in payments:

        if payment.id == payment_id:

            return payment

    raise HTTPException(
        status_code=404,
        detail="Payment not found"
    )


# ============================================================
# GET PAYMENT BY ORDER
# ============================================================

@app.get(
    "/payments/order/{order_id}",
    response_model=Payment
)
def get_payment_by_order(order_id: int):

    for payment in payments:

        if payment.order_id == order_id:

            return payment

    raise HTTPException(
        status_code=404,
        detail="Payment not found for this order"
    )