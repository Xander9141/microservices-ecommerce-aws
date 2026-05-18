# Arquitectura del Sistema

El sistema implementa una arquitectura basada en microservicios para un ecommerce.

## Servicios

### Frontend

Responsable de la interfaz de usuario. Permite visualizar productos, carrito de compras y proceso de pago.

### Backend API

Servicio desarrollado con FastAPI. Gestiona productos, carrito de compras y comunicación con el microservicio de pagos.

### Payments Service

Microservicio independiente encargado de procesar pagos simulados con tarjeta de crédito o débito.

## Flujo del sistema

1. El usuario accede al frontend.
2. El frontend consulta productos al backend.
3. El usuario agrega productos al carrito.
4. El backend recibe la solicitud de pago.
5. El backend se comunica con el microservicio de pagos.
6. El microservicio responde si el pago fue aprobado.

## Despliegue esperado

Cada servicio se ejecuta en un contenedor Docker independiente.  
El despliegue final está pensado para AWS ECS Fargate utilizando imágenes almacenadas en AWS ECR.
