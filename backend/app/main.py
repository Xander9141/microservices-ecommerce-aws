from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI(title="Ecommerce Backend API")

products = [
    {"id": 1, "name": "Notebook", "price": 750000},
    {"id": 2, "name": "Mouse", "price": 12000},
    {"id": 3, "name": "Teclado", "price": 25000}
]

cart = []

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
    return products

@app.post("/cart")
def add_to_cart(item: CartItem):
    cart.append(item.dict())
    return {"message": "Producto agregado al carrito", "cart": cart}

@app.get("/cart")
def get_cart():
    return {"cart": cart}

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
