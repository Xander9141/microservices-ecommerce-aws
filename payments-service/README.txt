# Microservices Ecommerce AWS

Sistema de ventas online basado en arquitectura de microservicios utilizando Docker, FastAPI, Angular y AWS.

## Arquitectura

El sistema está compuesto por:

* Frontend Angular
* Backend API REST FastAPI
* Microservicio de pagos
* Docker Compose
* CI/CD con GitHub Actions
* AWS ECS + ECR

## Tecnologías

* Angular
* FastAPI
* Docker
* GitHub Actions
* AWS ECS
* AWS ECR

## Funcionalidades

* Registro de usuarios
* Inicio de sesión
* Visualización de productos
* Carrito de compras
* Integración de pagos
* Persistencia de datos

## Ejecución local

```bash
docker-compose up --build
```

## CI/CD

El proyecto utiliza GitHub Actions para:

* Build automático
* Push de imágenes a ECR
* Deploy automático en AWS ECS

## Integrantes

* Ramón Alexander Torres Rodríguez
