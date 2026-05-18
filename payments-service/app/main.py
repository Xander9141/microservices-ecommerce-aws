from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="Payments Microservice")

class PaymentRequest(BaseModel):
    user_id: int
    amount: int
    method: str

@app.get("/")
def home():
    return {"message": "Microservicio de pagos funcionando"}

@app.post("/payments")
def create_payment(payment: PaymentRequest):
    return {
        "message": "Pago procesado correctamente",
        "transaction_id": "TX-" + datetime.now().strftime("%Y%m%d%H%M%S"),
        "user_id": payment.user_id,
        "amount": payment.amount,
        "method": payment.method,
        "status": "approved"
    }
