import customtkinter as ctk
from estilos.tema_personalizado import crear_ventana
from estilos.paleta_colores import COLORES
from estilos.fuentes import FUENTES
from views.componentes.menu_lateral import crear_menu_lateral
from views.componentes.area_selector import crear_selector_area
from views.componentes.product_list import crear_lista_productos
from views.componentes.cuenta_display import crear_cuenta_display
from views.componentes.resumen_diario import mostrar_resumen
from controllers.producto_controller import cargar_areas, cargar_productos_por_area
from controllers.cliente_controller import atender_cliente, obtener_resumen_diario

# Variables globales
areas = []
productos_por_area = {}
cuenta_actual = {}
total_actual = 0
historial_compras = []

def iniciar_app(nombre_usuario, rol_usuario):
    root = crear_ventana("Terminal - Supermercado", "900x540")

    # --- Contenedor principal ---
    contenedor = ctk.CTkFrame(root, fg_color="transparent")
    contenedor.pack(fill="both", expand=True)

    # --- Panel derecho dinámico ---
    panel_derecho = ctk.CTkFrame(contenedor, fg_color="transparent")
    panel_derecho.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    # --- Navegación desde menú lateral ---
    def mostrar_seccion(seccion):
        for widget in panel_derecho.winfo_children():
            widget.destroy()
        if seccion == "Inicio":
            mostrar_inicio(panel_derecho)
        elif seccion == "Inventario":
            mostrar_inventario(panel_derecho, rol_usuario)
        elif seccion == "Ventas":
            mostrar_ventas(panel_derecho)
        elif seccion == "Historial":
            mostrar_historial(panel_derecho)

    crear_menu_lateral(contenedor, nombre_usuario, rol_usuario, mostrar_seccion)
    mostrar_seccion("Inicio")
    root.mainloop()

# --- Panel: Inicio ---
def mostrar_inicio(panel):
    label = ctk.CTkLabel(panel, text="Bienvenido al sistema", font=FUENTES["titulo"],
                         text_color=COLORES["dorado"])
    label.pack(pady=20)

# --- Panel: Inventario ---
def mostrar_inventario(panel, rol_usuario):
    global areas, productos_por_area, cuenta_actual, total_actual

    combo_area = crear_selector_area(panel, lambda _: on_area_selected(combo_area, lista_productos))
    combo_area.pack(pady=(10, 0))

    lista_productos = crear_lista_productos(panel, lambda nombre, precio: on_producto_selected(nombre, precio, texto_cuenta))
    lista_productos.pack(fill="both", expand=True)

    texto_cuenta = crear_cuenta_display(panel)
    texto_cuenta.pack(fill="both", expand=True)

    botones_frame = ctk.CTkFrame(panel, fg_color="transparent")
    botones_frame.pack(pady=10)

    btn_comprar = ctk.CTkButton(botones_frame, text="Comprar", font=FUENTES["boton"],
                                fg_color=COLORES["dorado"], text_color=COLORES["texto_oscuro"],
                                corner_radius=10, command=lambda: on_comprar(texto_cuenta))
    btn_comprar.pack(side="left", padx=10)

    btn_quitar = ctk.CTkButton(botones_frame, text="Quitar Último", font=FUENTES["boton"],
                               fg_color=COLORES["dorado"], text_color=COLORES["texto_oscuro"],
                               corner_radius=10, command=lambda: on_quitar(texto_cuenta))
    btn_quitar.pack(side="right", padx=10)

    areas = cargar_areas()
    if areas:
        combo_area.configure(values=[a["nombre"] for a in areas])
        combo_area.set(areas[0]["nombre"])
        cargar_productos_por_area_index(0, lista_productos)

    actualizar_cuenta(texto_cuenta)

# --- Panel: Ventas (placeholder) ---
def mostrar_ventas(panel):
    label = ctk.CTkLabel(panel, text="Panel de ventas (en construcción)", font=FUENTES["etiqueta"],
                         text_color=COLORES["texto_claro"])
    label.pack(pady=20)

# --- Panel: Historial ---
def mostrar_historial(panel):
    global historial_compras
    panel_historial = ctk.CTkTextbox(panel, font=FUENTES["entrada"],
                                     fg_color=COLORES["campo_fondo"], text_color="white",
                                     corner_radius=10)
    panel_historial.pack(fill="both", expand=True, padx=10, pady=10)

    panel_historial.insert("1.0", "Historial de compras:\n\n")
    for i, compra in enumerate(historial_compras, 1):
        panel_historial.insert("end", f"{i}. Total: ${compra['total']:.2f}\n")
        for prod in compra["productos"]:
            panel_historial.insert("end", f"   - {prod['nombre']} x{prod['cantidad']}\n")
        panel_historial.insert("end", "\n")
    panel_historial.configure(state="disabled")

# --- Lógica compartida ---
def cargar_productos_por_area_index(indice, lista_widget):
    global productos_por_area
    area_id = areas[indice]["_id"]
    productos = cargar_productos_por_area(area_id)
    productos_por_area = {i: p for i, p in enumerate(productos)}
    lista_widget.limpiar()
    for p in productos:
        lista_widget.agregar_producto(p["nombre"], p["precio"])

def on_area_selected(combo, lista_widget):
    nombre = combo.get()
    indice = next((i for i, a in enumerate(areas) if a["nombre"] == nombre), 0)
    cargar_productos_por_area_index(indice, lista_widget)

def on_producto_selected(nombre, precio, texto_widget):
    global cuenta_actual, total_actual
    if nombre in cuenta_actual:
        cuenta_actual[nombre]["cantidad"] += 1
    else:
        cuenta_actual[nombre] = {
            "nombre": nombre,
            "precio": precio,
            "cantidad": 1
        }
    total_actual += precio
    actualizar_cuenta(texto_widget)

def actualizar_cuenta(texto_widget):
    texto_widget.configure(state="normal")
    texto_widget.delete("1.0", "end")
    for datos in cuenta_actual.values():
        texto_widget.insert("end", f"{datos['nombre']} x{datos['cantidad']} - ${datos['precio'] * datos['cantidad']:.2f}\n")
    texto_widget.insert("end", f"\nTotal: ${total_actual:.2f}")
    texto_widget.configure(state="disabled")

def on_comprar(texto_widget):
    global cuenta_actual, total_actual, historial_compras
    if cuenta_actual:
        resumen = {
            "productos": list(cuenta_actual.values()),
            "total": total_actual
        }
        historial_compras.append(resumen)
        atender_cliente(cuenta_actual, total_actual, None, lambda: actualizar_cuenta(texto_widget))
        cuenta_actual = {}
        total_actual = 0
        actualizar_cuenta(texto_widget)

def on_quitar(texto_widget):
    global cuenta_actual, total_actual
    if cuenta_actual:
        ultimo = list(cuenta_actual.keys())[-1]
        total_actual -= cuenta_actual[ultimo]["precio"] * cuenta_actual[ultimo]["cantidad"]
        cuenta_actual.pop(ultimo)
        actualizar_cuenta(texto_widget)
