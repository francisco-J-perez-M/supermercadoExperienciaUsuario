from ttkbootstrap import ttk
import tkinter as tk

def crear_cuenta_display(parent):
    label = ttk.Label(parent, text="Cuenta en tiempo real:", font=("Arial", 12))
    label.pack(anchor="w")

    texto = tk.Text(parent, height=12, state="disabled")
    texto.pack(fill="both", expand=True)

    return texto
