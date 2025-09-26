import ttkbootstrap as tb

def crear_ventana(titulo="Supermercado", tamaño="800x500", tema="flatly"):
    root = tb.Window(themename=tema)
    root.title(titulo)
    root.geometry(tamaño)
    return root
