from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import jwt
from prometheus_fastapi_instrumentator import Instrumentator
from typing import Dict


app = FastAPI(
    title="Smart E-Commerce - User Service",
    version="1.0.0"
)

Instrumentator().instrument(app).expose(app)


# ============================================================
# PASSWORD & JWT CONFIGURATION
# ============================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

SECRET_KEY = "smart-ecommerce-secret-key"
ALGORITHM = "HS256"


# ============================================================
# DATA MODELS
# ============================================================

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ============================================================
# TEMPORARY IN-MEMORY DATABASE
# ============================================================

users: Dict[int, dict] = {}

user_id_counter = 1


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "service": "User Service",
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
# REGISTER USER
# ============================================================

@app.post("/users/register")
def register(user: UserCreate):

    global user_id_counter

    # Check duplicate email
    for existing_user in users.values():

        if existing_user["email"] == user.email:

            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

    # Hash password
    hashed_password = pwd_context.hash(user.password)

    # Create user
    new_user = {
        "id": user_id_counter,
        "name": user.name,
        "email": user.email,
        "password": hashed_password
    }

    users[user_id_counter] = new_user

    response = {
        "id": user_id_counter,
        "name": user.name,
        "email": user.email
    }

    user_id_counter += 1

    return response


# ============================================================
# LOGIN
# ============================================================

@app.post("/users/login")
def login(request: LoginRequest):

    user = None

    for existing_user in users.values():

        if existing_user["email"] == request.email:

            user = existing_user
            break

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Verify password
    if not pwd_context.verify(
        request.password,
        user["password"]
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Generate JWT
    token = jwt.encode(
        {
            "user_id": user["id"],
            "email": user["email"]
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }

# ============================================================
# GET ALL USERS
# ============================================================

@app.get("/users")
def get_all_users():

    return [
        {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
        for user in users.values()
    ]
# ============================================================
# GET USER
# ============================================================

@app.get("/users/{user_id}")
def get_user(user_id: int):

    if user_id not in users:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user = users[user_id]

    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"]
    }