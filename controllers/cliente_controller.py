from models.cliente import ClienteModel
from tkinter import messagebox

def atender_cliente(cuenta_actual, total_actual, db, actualizar_callback):
    if not cuenta_actual:
        messagebox.showwarning("Atención", "No hay productos en la cuenta")
        return

    modelo = ClienteModel()
    modelo.registrar_cliente(list(cuenta_actual.values()), total_actual)

    messagebox.showinfo("Éxito", f"Cliente atendido por ${total_actual:.2f}")
    cuenta_actual.clear()
    actualizar_callback()

def obtener_resumen_diario():
    modelo = ClienteModel()
    return modelo.obtener_clientes_hoy()
