from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import psycopg2
import os
import time
import boto3
import random

app = FastAPI(title="Ecommerce Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

connected = False

while not connected:
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )
        connected = True
        print("PostgreSQL conectado correctamente")
    except Exception as error:
        print("Esperando PostgreSQL...")
        print(error)
        time.sleep(2)

cursor = conn.cursor()

# CONFIGURACIÓN AMAZON S3 (Alternativa B)
BUCKET_NAME = "msecommerce-production-storage"
MAX_SPACE_BYTES = 2 * 1024 * 1024 * 1024  # 2 GB de espacio límite por usuario

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION", "us-east-2")
)

# TABLAS BASE
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
    password VARCHAR(100),
    verification_code VARCHAR(10),
    is_verified BOOLEAN DEFAULT FALSE
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


# MODELOS PYDANTIC
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

class VerifyRequest(BaseModel):
    username: str
    code: str


# AUXILIARES
def get_user_used_space(user_id: str) -> int:
    """Calcula el peso total consumido en el prefijo del usuario de S3"""
    total_size = 0
    prefix = f"users/{user_id}/"
    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
        if "Contents" in response:
            for obj in response["Contents"]:
                total_size += obj["Size"]
        return total_size
    except Exception:
        return 0


# RUTAS
@app.get("/")
def home():
    return {"message": "Backend Ecommerce API funcionando con PostgreSQL y Amazon S3 listo"}


@app.post("/register")
def register(user: User):
    try:
        val_code = str(random.randint(100000, 999999))

        cursor.execute(
            "INSERT INTO users (username, password, verification_code, is_verified) VALUES (%s, %s, %s, FALSE)",
            (user.username, user.password, val_code)
        )
        conn.commit()

        # REQUERIMIENTO 1: Disparar evento síncrono/asíncrono hacia microservicio de notificaciones
        try:
            requests.post(
                "http://notifications:9001/notify/register",
                json={"email": user.username, "code": val_code},
                timeout=3
            )
        except Exception as e:
            print(f"[WARN] No se pudo enviar notificación de registro: {str(e)}")

        return {
            "message": "Usuario registrado. Ingrese el código enviado a su correo para verificar.",
            "debug_code": val_code
        }
    except Exception as error:
        conn.rollback()
        return {
            "message": "No se pudo registrar el usuario",
            "error": str(error)
        }


@app.post("/verify")
def verify_account(data: VerifyRequest):
    cursor.execute(
        "SELECT id, verification_code FROM users WHERE username = %s",
        (data.username,)
    )
    result = cursor.fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if result[1] == data.code:
        cursor.execute(
            "UPDATE users SET is_verified = TRUE WHERE username = %s",
            (data.username,)
        )
        conn.commit()
        return {"message": "Cuenta activada con éxito. Ya puede iniciar sesión."}

    raise HTTPException(status_code=400, detail="Código de validación incorrecto")


@app.post("/login")
def login(user: User):
    cursor.execute(
        "SELECT id, username, is_verified FROM users WHERE username = %s AND password = %s",
        (user.username, user.password)
    )
    result = cursor.fetchone()

    if result:
        if not result[2]:
            raise HTTPException(status_code=403, detail="Su cuenta no ha sido verificada aún.")

        return {
            "message": "Inicio de sesión correcto",
            "user_id": result[0],
            "username": result[1]
        }

    return {"message": "Credenciales inválidas"}


# GESTIÓN DE ARCHIVOS (AMAZON S3)
@app.post("/files/upload")
async def upload_file(user_id: str, file: UploadFile = File(...)):
    used_space = get_user_used_space(user_id)

    file_bytes = await file.read()
    file_size = len(file_bytes)

    if used_space + file_size > MAX_SPACE_BYTES:
        raise HTTPException(status_code=400, detail="Espacio de almacenamiento de 2 GB superado.")

    s3_key = f"users/{user_id}/{file.filename}"

    try:
        s3_client.put_object(Bucket=BUCKET_NAME, Key=s3_key, Body=file_bytes)

        new_used = used_space + file_size
        available = MAX_SPACE_BYTES - new_used

        # REQUERIMIENTO 6: Disparar evento hacia microservicio de notificaciones móviles (Twilio/Logs)
        try:
            requests.post(
                "http://notifications:9001/notify/file-upload",
                json={
                    "user_id": int(user_id),
                    "filename": file.filename,
                    "used_space_mb": round(new_used / (1024 * 1024), 2),
                    "available_space_mb": round(available / (1024 * 1024), 2)
                },
                timeout=3
            )
        except Exception as e:
            print(f"[WARN] No se pudo enviar notificación de archivo: {str(e)}")

        return {
            "status": "success",
            "filename": file.filename,
            "used_space_mb": round(new_used / (1024 * 1024), 2),
            "available_space_mb": round(available / (1024 * 1024), 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en AWS S3: {str(e)}")


@app.get("/files/status")
async def get_storage_status(user_id: str):
    used_space = get_user_used_space(user_id)
    available_space = MAX_SPACE_BYTES - used_space

    return {
        "used_space_mb": round(used_space / (1024 * 1024), 2),
        "available_space_mb": round(available_space / (1024 * 1024), 2)
    }


# PRODUCTOS, CARRITO Y PAGOS
@app.get("/products")
def get_products():
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    return [
        {"id": row[0], "name": row[1], "price": row[2]}
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
        {"id": row[0], "product_id": row[1], "quantity": row[2]}
        for row in rows
    ]


@app.post("/pay")
def process_payment(payment: PaymentRequest):
    try:
        # Llama a payments-service (el cual generará la preferencia real de Mercado Pago)
        response = requests.post(
            "http://payments:9000/payments",
            json=payment.dict(),
            timeout=5
        )
        resp_data = response.json()

        # REQUERIMIENTO 2: Si el pago fue exitoso, disparar el correo de confirmación de compra
        if response.status_code == 200 and resp_data.get("status") == "approved":
            try:
                requests.post(
                    "http://notifications:9001/notify/purchase",
                    json={
                        "email": f"usuario_id_{payment.user_id}@ucm.cl",
                        "transaction_id": resp_data.get("transaction_id"),
                        "amount": payment.amount,
                        "products": "Compra de Carrito - Ecommerce UCM"
                    },
                    timeout=3
                )
            except Exception as e:
                print(f"[WARN] No se pudo enviar comprobante de compra: {str(e)}")

        return {
            "message": "Pago procesado desde backend",
            "payment_service_response": resp_data
        }
    except Exception as error:
        return {
            "message": "No se pudo conectar con el microservicio de pagos",
            "error": str(error),
            "status": "failed"
        }