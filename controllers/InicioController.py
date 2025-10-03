import tkinter as tk
from tkinter import messagebox
from views.InicioView import InicioView
from controllers.PuntoVentaController import PuntoVentaController
from controllers.SparkController import SparkController

class InicioController:
    def __init__(self):
        self.root = None
        self.view = None
        self.usuario = None
        self.rol = None
    
    def mostrar_inicio(self):
        self.view.mostrar_inicio()
    
    def mostrar_punto_venta(self):
        """Abrir el punto de venta desde el menú del administrador"""
        punto_venta_controller = PuntoVentaController()
        # Podemos pasar el root actual si queremos manejar ventanas hijas
        # o crear una nueva instancia independiente
        punto_venta_controller.iniciar_app(self.rol)
    
    def mostrar_ventas(self):
        self.view.mostrar_ventas()
    
    def mostrar_historial(self):
        self.view.mostrar_historial()

    def mostrar_analisis_spark(self):
        """Abrir el análisis Spark desde el menú"""
        spark_controller = SparkController()
        spark_controller.iniciar_analisis()

    def cerrar_sesion(self):
        if messagebox.askyesno("Cerrar Sesión", "¿Seguro que deseas salir?"):
            self.root.destroy()
            # Opcional: Volver al login
            from controllers.LoginController import LoginController
            login_controller = LoginController()
            login_controller.mostrar_login()
    
    def iniciar_aplicacion(self, usuario, rol):
        self.usuario = usuario
        self.rol = rol
        self.root = tk.Tk()
        self.view = InicioView(self.root, self)
        self.view.crear_vista_principal(usuario, rol)
        self.root.mainloop()