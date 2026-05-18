from fastapi import FastAPI
from pydantic import BaseModel
import requests
import sqlite3

app = FastAPI(title="Ecommerce Backend API")

conn = sqlite3.connect("ecommerce.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT,
    price INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    quantity INTEGER
)
""")

conn.commit()

cursor.execute("SELECT COUNT(*) FROM products")
count = cursor.fetchone()[0]

if count == 0:
    cursor.executemany(
        "INSERT INTO products (id, name, price) VALUES (?, ?, ?)",
        [
            (1, "Notebook", 750000),
            (2, "Mouse", 12000),
            (3, "Teclado", 25000)
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

@app.get("/")
def home():
    return {"message": "Backend Ecommerce API funcionando"}

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
        "INSERT INTO cart (product_id, quantity) VALUES (?, ?)",
        (item.product_id, item.quantity)
    )

    conn.commit()

    return {
        "message": "Producto agregado al carrito"
    }

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
