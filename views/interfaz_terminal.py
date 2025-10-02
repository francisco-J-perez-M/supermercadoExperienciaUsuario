from views.tema_bootstrap import crear_ventana
from views.componentes.area_selector import crear_selector_area
from views.componentes.product_list import crear_lista_productos
from views.componentes.cuenta_display import crear_cuenta_display
from views.componentes.botones import crear_botones
from controllers.producto_controller import cargar_areas, cargar_productos_por_area
from controllers.cliente_controller import atender_cliente, obtener_resumen_diario
from ttkbootstrap import ttk

# Variables globales compartidas
areas = []
productos_por_area = {}
cuenta_actual = {}
total_actual = 0

def iniciar_app(rol_usuario):
    global areas, productos_por_area, cuenta_actual, total_actual

    root = crear_ventana("Supermercado", "800x500", "flatly")

    # --- Área izquierda ---
    frame_izq = ttk.Frame(root)
    frame_izq.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    combo_area = crear_selector_area(frame_izq, None)
    lista_productos = crear_lista_productos(frame_izq, None)

    # --- Área derecha ---
    frame_der = ttk.Frame(root)
    frame_der.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    texto_cuenta = crear_cuenta_display(frame_der)

    # --- Botones ---
    crear_botones(root,
            lambda: on_atender(texto_cuenta),
            lambda: on_resumen(root),
            rol_usuario)


    # --- Asignar eventos después de crear widgets ---
    combo_area.bind("<<ComboboxSelected>>", lambda e: on_area_selected(combo_area, lista_productos))
    lista_productos.bind("<Double-Button-1>", lambda e: on_producto_selected(lista_productos, texto_cuenta))

    # --- Cargar datos iniciales ---
    areas = cargar_areas()
    if areas:
        combo_area["values"] = [a["nombre"] for a in areas]
        combo_area.current(0)
        cargar_productos_por_area_index(0, lista_productos)

    actualizar_cuenta(texto_cuenta)

    root.mainloop()

def cargar_productos_por_area_index(indice, lista_widget):
    global productos_por_area
    area_id = areas[indice]["_id"]
    productos = cargar_productos_por_area(area_id)
    productos_por_area = {i: p for i, p in enumerate(productos)}
    lista_widget.delete(0, "end")
    for p in productos:
        lista_widget.insert("end", f"{p['nombre']} - ${p['precio']:.2f}")

def on_area_selected(combo, lista_widget):
    indice = combo.current()
    if indice >= 0:
        cargar_productos_por_area_index(indice, lista_widget)

def on_producto_selected(lista, texto_widget):
    global cuenta_actual, total_actual
    seleccion = lista.curselection()
    if seleccion:
        indice = seleccion[0]
        producto = productos_por_area[indice]
        pid = producto["nombre"]
        if pid in cuenta_actual:
            cuenta_actual[pid]["cantidad"] += 1
        else:
            cuenta_actual[pid] = {
                "nombre": producto["nombre"],
                "precio": producto["precio"],
                "cantidad": 1
            }
        total_actual += producto["precio"]
        actualizar_cuenta(texto_widget)

def actualizar_cuenta(texto_widget):
    texto_widget.config(state="normal")
    texto_widget.delete(1.0, "end")
    for datos in cuenta_actual.values():
        texto_widget.insert("end", f"{datos['nombre']} x{datos['cantidad']} - ${datos['precio'] * datos['cantidad']:.2f}\n")
    texto_widget.insert("end", f"\nTotal: ${total_actual:.2f}")
    texto_widget.config(state="disabled")

def on_atender(texto_widget):
    atender_cliente(cuenta_actual, total_actual, None, lambda: actualizar_cuenta(texto_widget))

def on_resumen(root):
    clientes = obtener_resumen_diario()
    from views.componentes.resumen_diario import mostrar_resumen
    mostrar_resumen(root, clientes)
