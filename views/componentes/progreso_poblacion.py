from ttkbootstrap import ttk
import tkinter as tk
import time

class VentanaProgreso:
    def __init__(self, total_registros):
        self.total = total_registros
        self.inicio = time.time()

        self.root = tk.Toplevel()
        self.root.title("Poblando base de datos...")
        self.root.geometry("400x150")
        self.root.resizable(False, False)

        self.label = ttk.Label(self.root, text="Progreso: 0%", font=("Arial", 12))
        self.label.pack(pady=10)

        self.barra = ttk.Progressbar(self.root, length=300, mode="determinate", bootstyle="info")
        self.barra.pack(pady=10)
        self.barra["maximum"] = total_registros

        self.tiempo = ttk.Label(self.root, text="Tiempo transcurrido: 0s", font=("Arial", 10))
        self.tiempo.pack(pady=5)

        self.root.update()

    def actualizar(self, actual):
        porcentaje = int((actual / self.total) * 100)
        self.barra["value"] = actual
        self.label.config(text=f"Progreso: {porcentaje}%")
        transcurrido = int(time.time() - self.inicio)
        self.tiempo.config(text=f"Tiempo transcurrido: {transcurrido}s")
        self.root.update()

    def cerrar(self):
        self.root.destroy()
