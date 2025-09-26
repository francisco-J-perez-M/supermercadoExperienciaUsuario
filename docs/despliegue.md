---

## 🚀 `docs/despliegue.md`

```markdown
# Flujo de Despliegue del Sistema

Este sistema incluye un mecanismo de verificación y despliegue condicional que permite iniciar en modo local o servidor según el estado de la base de datos.

## 🔍 Verificación inicial

Al ejecutar `main.py`, se verifica si las colecciones clave (`usuarios`, `clientes`, `productos`, `areas`) están pobladas.

- Si **ya existen datos**, se redirige al login
- Si **no existen datos**, se muestra una ventana con dos opciones:

## 🖥️ Despliegue Local

- Inserta 500,000 registros de clientes
- Población masiva con `poblar_clientes()` en lotes
- Ideal para pruebas de rendimiento y simulación institucional

## 🌐 Despliegue en Servidor

- Inserta datos mínimos:
  - 3 usuarios (admin + vendedores)
  - 10 áreas
  - 20–30 productos
  - 0–10 clientes de prueba
- Ideal para entornos de staging o producción inicial

## 🧩 Módulos involucrados

- `services/verificador_db.py`
- `services/poblacion_local.py`
- `services/poblacion_servidor.py`
- `views/ventana_inicio.py`
```
