from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import psycopg2
import os
import time

app = FastAPI(title="Ecommerce Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

time.sleep(5)

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT")
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    price INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS cart (
    id SERIAL PRIMARY KEY,
    product_id INTEGER,
    quantity INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE,
    password VARCHAR(100)
)
""")

conn.commit()

cursor.execute("SELECT COUNT(*) FROM products")
count = cursor.fetchone()[0]

if count == 0:
    cursor.executemany(
        "INSERT INTO products (name, price) VALUES (%s, %s)",
        [
            ("Notebook", 750000),
            ("Mouse", 12000),
            ("Teclado", 25000)
        ]
    )
    conn.commit()


class CartItem(BaseModel):
    product_id: int
    quantity: int


class PaymentRequest(BaseModel):
    user_id: int
    amount: int
    method: str


class User(BaseModel):
    username: str
    password: str


@app.get("/")
def home():
    return {"message": "Backend Ecommerce API funcionando con PostgreSQL"}


@app.post("/register")
def register(user: User):
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (user.username, user.password)
        )
        conn.commit()

        return {"message": "Usuario registrado correctamente"}

    except Exception as error:
        conn.rollback()
        return {
            "message": "No se pudo registrar el usuario",
            "error": str(error)
        }


@app.post("/login")
def login(user: User):
    cursor.execute(
        "SELECT * FROM users WHERE username = %s AND password = %s",
        (user.username, user.password)
    )

    result = cursor.fetchone()

    if result:
        return {
            "message": "Inicio de sesión correcto",
            "user_id": result[0],
            "username": result[1]
        }

    return {"message": "Credenciales inválidas"}


@app.get("/products")
def get_products():
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "name": row[1],
            "price": row[2]
        }
        for row in rows
    ]


@app.post("/cart")
def add_to_cart(item: CartItem):
    cursor.execute(
        "INSERT INTO cart (product_id, quantity) VALUES (%s, %s)",
        (item.product_id, item.quantity)
    )

    conn.commit()

    return {"message": "Producto agregado al carrito"}


@app.get("/cart")
def get_cart():
    cursor.execute("SELECT * FROM cart")
    rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "product_id": row[1],
            "quantity": row[2]
        }
        for row in rows
    ]


@app.post("/pay")
def process_payment(payment: PaymentRequest):
    try:
        response = requests.post(
            "http://payments:9000/payments",
            json=payment.dict(),
            timeout=5
        )

        return {
            "message": "Pago procesado desde backend",
            "payment_service_response": response.json()
        }

    except Exception as error:
        return {
            "message": "No se pudo conectar con el microservicio de pagos",
            "error": str(error),
            "status": "failed"
        }