from ttkbootstrap import ttk
import tkinter as tk

def crear_lista_productos(parent, on_double_click_callback):
    label = ttk.Label(parent, text="Productos del área:", font=("Arial", 12))
    label.pack(anchor="w", pady=(10, 0))

    frame_lista = ttk.Frame(parent)
    frame_lista.pack(fill="both", expand=True)

    scrollbar = ttk.Scrollbar(frame_lista)
    scrollbar.pack(side="right", fill="y")

    lista = tk.Listbox(frame_lista, yscrollcommand=scrollbar.set, height=10)
    lista.pack(fill="both", expand=True)
    lista.bind("<Double-Button-1>", on_double_click_callback)

    scrollbar.config(command=lista.yview)

    return lista
