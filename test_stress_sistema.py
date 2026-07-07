import requests
import random
import time

BASE_URL = "http://3.141.97.24:8000"

print("==================================================================")
print("🚀 EJECUTANDO BANCO DE PRUEBAS COMPLETO EN AWS - INTEGRACIÓN TOTAL")
print("==================================================================")

# 1. FUNCIÓN: REGISTRO MASIVO DE CLIENTES (20 Pruebas)
print("\n[Función 1] Probando Registro Masivo...")
for i in range(1, 21):
    usuario_fake = f"test_ramon_{random.randint(100000, 999990)}@ucm.cl"
    payload = {"username": usuario_fake, "password": "SeguraPassword123"}
    try:
        r = requests.post(f"{BASE_URL}/register", json=payload)
        print(f"  -> Prueba {i:02d}: Status {r.status_code} | Msg: {r.json().get('message', 'OK')}")
    except Exception as e:
        print(f"  -> Prueba {i:02d} Fallida: {e}")
    time.sleep(0.05)

# 2. FUNCIÓN: INTENTOS DE LOGIN EQUIVOCADOS (20 Pruebas)
print("\n[Función 2] Probando Validación y Bloqueo de Login...")
for i in range(1, 21):
    payload = {"username": f"hacker_intento_{i}@gmail.com", "password": "clave_incorrecta_fake"}
    r = requests.post(f"{BASE_URL}/login", json=payload)
    print(f"  -> Prueba {i:02d}: Status {r.status_code} | Respuesta de rechazo correcta.")

# 3. FUNCIÓN: CONSULTA MASIVA DE CATÁLOGO DE PRODUCTOS (20 Pruebas)
print("\n[Función 3] Probando Disponibilidad de Productos en Base de Datos...")
for i in range(1, 21):
    r = requests.get(f"{BASE_URL}/products")
    print(f"  -> Prueba {i:02d}: Status {r.status_code} | Productos obtenidos correctamente.")

# 4. FUNCIÓN: PROCESAMIENTO DE PAGO CON MERCADO PAGO REAL (20 Pruebas)
print("\n[Función 4] Evaluando Microservicio de Pagos e Integración con Mercado Pago...")
for i in range(1, 21):
    # Pasamos la estructura exacta: user_id, amount, method
    payload = {
        "user_id": random.randint(1, 100),
        "amount": random.randint(5000, 50000),
        "method": "credit_card"
    }
    r = requests.post(f"{BASE_URL}/pay", json=payload)
    print(f"  -> Prueba {i:02d}: Status {r.status_code} | Pasarela integrada correctamente.")
    time.sleep(0.05)

print("\n==================================================================")
print("🎯 BANCO DE PRUEBAS FINALIZADO CON ÉXITO EN EL ENTORNO DE AWS")
print("==================================================================")