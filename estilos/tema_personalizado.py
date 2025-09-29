import customtkinter as ctk
from estilos.paleta_colores import COLORES

def crear_ventana(titulo="Supermercado", tamaño="420x320"):
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")  # No afecta si usamos colores personalizados

    root = ctk.CTk()
    root.title(titulo)
    root.geometry(tamaño)
    root.configure(fg_color=COLORES["fondo_principal"])
    root.resizable(False, False)
    return root
