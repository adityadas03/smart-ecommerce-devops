from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from prometheus_fastapi_instrumentator import Instrumentator
from typing import List


app = FastAPI(
    title="Smart E-Commerce - Product Service",
    version="1.0.0"
)

Instrumentator().instrument(app).expose(app)


# ============================================================
# DATA MODELS
# ============================================================

class ProductCreate(BaseModel):

    name: str = Field(..., min_length=2)

    description: str

    price: float = Field(
        ...,
        gt=0
    )

    category: str

    stock: int = Field(
        ...,
        ge=0
    )


class Product(ProductCreate):

    id: int


# ============================================================
# TEMPORARY IN-MEMORY DATABASE
# ============================================================

products: List[Product] = []

product_id_counter = 1


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "service": "Product Service",
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
# CREATE PRODUCT
# ============================================================

@app.post(
    "/products",
    response_model=Product
)
def create_product(product: ProductCreate):

    global product_id_counter

    new_product = Product(
        id=product_id_counter,
        name=product.name,
        description=product.description,
        price=product.price,
        category=product.category,
        stock=product.stock
    )

    products.append(new_product)

    product_id_counter += 1

    return new_product


# ============================================================
# GET ALL PRODUCTS
# ============================================================

@app.get(
    "/products",
    response_model=List[Product]
)
def get_products():

    return products


# ============================================================
# GET PRODUCT
# ============================================================

@app.get(
    "/products/{product_id}",
    response_model=Product
)
def get_product(product_id: int):

    for product in products:

        if product.id == product_id:

            return product

    raise HTTPException(
        status_code=404,
        detail="Product not found"
    )


# ============================================================
# UPDATE PRODUCT
# ============================================================

@app.put(
    "/products/{product_id}",
    response_model=Product
)
def update_product(
    product_id: int,
    product_data: ProductCreate
):

    for index, product in enumerate(products):

        if product.id == product_id:

            updated_product = Product(
                id=product_id,
                name=product_data.name,
                description=product_data.description,
                price=product_data.price,
                category=product_data.category,
                stock=product_data.stock
            )

            products[index] = updated_product

            return updated_product

    raise HTTPException(
        status_code=404,
        detail="Product not found"
    )


# ============================================================
# DELETE PRODUCT
# ============================================================

@app.delete("/products/{product_id}")
def delete_product(product_id: int):

    for index, product in enumerate(products):

        if product.id == product_id:

            products.pop(index)

            return {
                "message": "Product deleted successfully",
                "product_id": product_id
            }

    raise HTTPException(
        status_code=404,
        detail="Product not found"
    )


# ============================================================
# UPDATE STOCK
# ============================================================

@app.patch("/products/{product_id}/stock")
def update_stock(
    product_id: int,
    quantity: int
):

    for product in products:

        if product.id == product_id:

            new_stock = product.stock + quantity

            if new_stock < 0:

                raise HTTPException(
                    status_code=400,
                    detail="Insufficient stock"
                )

            product.stock = new_stock

            return {
                "message": "Stock updated successfully",
                "product_id": product_id,
                "stock": product.stock
            }

    raise HTTPException(
        status_code=404,
        detail="Product not found"
    )