# Microservices Ecommerce AWS

Sistema ecommerce basado en arquitectura de microservicios, desarrollado con FastAPI, Docker, PostgreSQL y un microservicio independiente de pagos.

## Objetivo del proyecto

El objetivo es implementar una solución de ventas online separada por servicios, donde cada componente cumple una responsabilidad específica.  
El proyecto busca demostrar arquitectura de microservicios, contenedores Docker, persistencia de datos, integración entre servicios y automatización inicial con GitHub Actions.

## Arquitectura

El sistema está compuesto por:

- **Frontend:** interfaz web para visualizar productos, agregar al carrito y ejecutar pagos.
- **Backend API:** servicio principal desarrollado con FastAPI. Gestiona usuarios, productos, carrito y comunicación con pagos.
- **Payments Service:** microservicio independiente encargado de procesar pagos simulados.
- **PostgreSQL:** base de datos relacional para persistencia.
- **Docker Compose:** orquestación local de todos los servicios.
- **GitHub Actions:** pipeline base de integración continua.

## Flujo del sistema

1. El usuario accede al frontend.
2. El frontend consulta productos al backend.
3. El backend obtiene los productos desde PostgreSQL.
4. El usuario agrega productos al carrito.
5. El carrito se guarda en PostgreSQL.
6. El usuario ejecuta el pago.
7. El backend se comunica con el microservicio de pagos.
8. El microservicio responde con una transacción aprobada.

## Servicios

| Servicio | Tecnología | Puerto |
|---|---|---|
| Frontend | HTML + Nginx | 80 |
| Backend API | FastAPI | 8000 |
| Payments Service | FastAPI | 9000 |
| Database | PostgreSQL | 5432 |

## Endpoints principales

### Backend

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/` | Estado del backend |
| POST | `/register` | Registro de usuario |
| POST | `/login` | Inicio de sesión |
| GET | `/products` | Lista de productos |
| POST | `/cart` | Agregar producto al carrito |
| GET | `/cart` | Consultar carrito |
| POST | `/pay` | Procesar pago mediante microservicio |

### Payments Service

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/` | Estado del microservicio |
| POST | `/payments` | Procesamiento de pago |

## Ejecución local

```bash
docker compose up --build