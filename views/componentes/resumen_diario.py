import customtkinter as ctk
from estilos.paleta_colores import COLORES
from estilos.fuentes import FUENTES
from datetime import datetime
from tkinter import messagebox

def mostrar_resumen(root, clientes_hoy):
    fecha_formateada = datetime.now().strftime('%d/%m/%Y')

    if not clientes_hoy:
        messagebox.showinfo("Resumen Diario", f"No hay clientes atendidos el día {fecha_formateada}")
        return

    total_diario = sum(cliente['total'] for cliente in clientes_hoy)
    cantidad_ventas = len(clientes_hoy)

    resumen = f"RESUMEN DEL DÍA: {fecha_formateada}\n\n"
    resumen += f"Clientes atendidos: {cantidad_ventas}\n"
    resumen += f"Total vendido: ${total_diario:.2f}\n\n"
    resumen += "Detalle de clientes:\n"

    for i, cliente in enumerate(clientes_hoy, 1):
        fecha_dt = datetime.fromisoformat(cliente['fecha'])
        resumen += f"\n{i}. {cliente['nombre']} - Total: ${cliente['total']:.2f} - {fecha_dt.strftime('%H:%M:%S')}\n"
        for prod in cliente['productos']:
            resumen += f"   - {prod['nombre']} x{prod['cantidad']}\n"

    ventana = ctk.CTkToplevel(root)
    ventana.title(f"Resumen Diario - {fecha_formateada}")
    ventana.geometry("500x400")
    ventana.configure(fg_color=COLORES["fondo_principal"])

    texto = ctk.CTkTextbox(ventana, wrap="word", font=FUENTES["entrada"],
                           fg_color=COLORES["campo_fondo"], text_color="white",
                           corner_radius=10)
    texto.pack(fill="both", expand=True, padx=10, pady=10)
    texto.insert("1.0", resumen)
    texto.configure(state="disabled")
