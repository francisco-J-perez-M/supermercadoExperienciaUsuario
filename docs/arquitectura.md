---

## 🧱 `docs/arquitectura.md`

```markdown
# Arquitectura Institucional del Sistema Supermercado

Este sistema está diseñado bajo el patrón MVC, con separación clara entre lógica, interfaz y persistencia. Su estructura modular permite escalar, mantener y documentar cada componente de forma independiente.

## 📦 Estructura de carpetas

```
mi_proyecto/
├── main.py
├── config/            # Parámetros globales y entorno
├── db/                # Conexión MongoDB
├── models/            # Entidades del sistema
├── controllers/       # Lógica funcional desacoplada
├── services/          # Población, verificación y utilidades
├── views/             # Interfaz gráfica modular
│   └── componentes/   # Subvistas atomizadas
├── analytics/         # Análisis con PySpark
├── tests/             # Pruebas unitarias
└── docs/              # Documentación técnica
```

## 🧩 Roles técnicos

- **Modelos**: encapsulan acceso a MongoDB y validación de datos
- **Controladores**: gestionan el flujo funcional entre vistas y modelos
- **Servicios**: ejecutan tareas técnicas como población masiva o verificación
- **Vistas**: presentan la interfaz gráfica con `ttkbootstrap`, dividida en componentes
- **Main**: orquestador del sistema, decide el flujo según el estado de la base

## 🧠 Principios aplicados

- Atomización visual y funcional
- Replicabilidad en entornos locales y remotos
- Documentación modular por rol
- Trazabilidad de datos y eventos
```
