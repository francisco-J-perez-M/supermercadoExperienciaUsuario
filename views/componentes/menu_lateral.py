import customtkinter as ctk
from estilos.paleta_colores import COLORES
from estilos.fuentes import FUENTES

def crear_menu_lateral(parent, nombre_usuario, rol_usuario, on_seleccion_callback):
    menu = ctk.CTkFrame(parent, width=180, fg_color=COLORES["fondo_principal"])
    menu.pack(side="left", fill="y")

    # --- Saludo institucional ---
    saludo = ctk.CTkLabel(menu, text=f"Hola, {rol_usuario} {nombre_usuario}",
                          font=FUENTES["etiqueta"], text_color=COLORES["dorado"])
    saludo.pack(pady=(20, 10))

    # --- Botones del menú ---
    botones_info = [
        ("Inicio", "🏠"),
        ("Inventario", "📦"),
        ("Ventas", "📈"),
        ("Historial", "📁")
    ]

    botones = []
    for texto, icono in botones_info:
        btn = ctk.CTkButton(menu, text=f"{icono}  {texto}", font=FUENTES["entrada"],
                            fg_color="transparent", text_color=COLORES["texto_claro"],
                            hover_color=COLORES["campo_fondo"], corner_radius=8,
                            command=lambda t=texto: on_seleccion_callback(t))
        btn.pack(fill="x", padx=10, pady=5)
        botones.append(btn)

    # --- Botón cerrar sesión ---
    cerrar_sesion = ctk.CTkButton(menu, text="⏻  Cerrar Sesión", font=FUENTES["entrada"],
                                  fg_color=COLORES["dorado"], text_color=COLORES["texto_oscuro"],
                                  corner_radius=10)
    cerrar_sesion.pack(side="bottom", pady=20, padx=10, fill="x")

    return {
        "frame": menu,
        "botones": botones,
        "cerrar_sesion": cerrar_sesion
    }
