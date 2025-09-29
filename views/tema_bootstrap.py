import ttkbootstrap as tb
from tkinter import PhotoImage

def crear_ventana(titulo="Supermercado", tamaño="800x500", tema="flatly"):
    root = tb.Window(themename=tema)
    root.title(titulo)
    root.geometry(tamaño)
    root.configure(bg="#071739")  # Fondo navy profundo

    # --- Opcional: ícono institucional ---
    # icono = PhotoImage(file="assets/icono.png")
    # root.iconphoto(False, icono)

    # --- Opcional: desactivar redimensionamiento si se desea control visual ---
    root.resizable(False, False)

    return root
