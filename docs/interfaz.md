---

## 🎨 `docs/interfaz.md`

```markdown
# Componentes Visuales del Sistema

La interfaz gráfica está construida con `ttkbootstrap`, dividida en componentes reutilizables que permiten modificar cada parte sin afectar el resto.

## 🧩 Componentes en `views/componentes/`

| Componente         | Rol técnico                  |
|--------------------|------------------------------|
| `area_selector.py` | Combobox de selección de área |
| `product_list.py`  | Listbox de productos por área |
| `cuenta_display.py`| Visualización de cuenta actual |
| `botones.py`       | Botones de acción (atender, resumen) |
| `resumen_diario.py`| Ventana resumen con scroll |

## 🎛 Ensamblador principal

- `interfaz_terminal.py` importa y conecta todos los componentes
- Usa `crear_ventana()` desde `tema_bootstrap.py` para mantener consistencia visual

## 🔐 Login

- `views/login.py` gestiona autenticación
- Delegación al controlador `login_controller.py`

## 🧠 Principios aplicados

- Atomización visual
- Reusabilidad de componentes
- Estilo institucional con temas configurables
```

---