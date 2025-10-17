# InicioController.py
import tkinter as tk
from tkinter import messagebox
from views.InicioView import InicioView
from views.cruds.Usuarios import UsuariosView
from views.cruds.Productos import ProductosView
from views.cruds.Clientes import ClientesView
from controllers.PuntoVentaController import PuntoVentaController
from controllers.SparkController import SparkController
from controllers.MultimediaController import MultimediaController  # Nuevo import

class InicioController:
    def __init__(self):
        self.root = None
        self.view = None
        self.usuario = None
        self.rol = None
        self.multimedia_controller = None  # Controlador multimedia

    def mostrar_inicio(self):
        try:
            self.view.mostrar_inicio()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo mostrar inicio: {e}")

    def mostrar_punto_venta(self):
        """Abrir el punto de venta desde el menú del administrador"""
        try:
            punto_venta_controller = PuntoVentaController()
            punto_venta_controller.iniciar_app(self.rol)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir Punto de Venta: {e}")

    def mostrar_ventas(self):
        try:
            # Si InicioView tiene un método mostrar_ventas, delegar; si no, mostrar inicio
            if hasattr(self.view, "mostrar_ventas"):
                self.view.mostrar_ventas()
            else:
                self.view.mostrar_inicio()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo mostrar ventas: {e}")

    def mostrar_historial(self):
        try:
            if hasattr(self.view, "mostrar_historial"):
                self.view.mostrar_historial()
            else:
                self.view.mostrar_inicio()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo mostrar historial: {e}")

    def mostrar_analisis_spark(self):
        """Abrir el análisis Spark desde el menú"""
        try:
            spark_controller = SparkController()
            spark_controller.iniciar_analisis()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir Análisis Spark: {e}")

    def mostrar_multimedia(self):
        """Muestra el visualizador multimedia dentro del content_frame"""
        try:
            self.view.limpiar_contenido()
            
            # Crear frame contenedor para multimedia
            multimedia_container = tk.Frame(self.view.content_frame, bg=self.view.content_frame.cget('bg'))
            multimedia_container.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Inicializar controlador multimedia si no existe
            if not self.multimedia_controller:
                self.multimedia_controller = MultimediaController(self.root)
            
            # Crear e integrar la vista multimedia
            from views.MultimediaView import MultimediaView
            multimedia_view = MultimediaView(multimedia_container, self.multimedia_controller)
            self.multimedia_controller.set_view(multimedia_view)
            multimedia_view.crear_vista()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir Visualizador Multimedia: {e}")

    def cerrar_sesion(self):
        if messagebox.askyesno("Cerrar Sesión", "¿Seguro que deseas salir?"):
            try:
                self.root.destroy()
            except Exception:
                pass
            # Opcional: Volver al login
            try:
                from controllers.LoginController import LoginController
                login_controller = LoginController()
                login_controller.mostrar_login()
            except Exception:
                pass

    # Nuevos métodos para gestionar inventario desde el menú lateral
    def mostrar_usuarios(self):
        """Muestra la vista de gestión de usuarios dentro del content_frame"""
        try:
            self.view.limpiar_contenido()
            usuarios_view = UsuariosView(master=self.view.content_frame)
            usuarios_view.pack(fill="both", expand=True)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir Usuarios: {e}")

    def mostrar_productos(self):
        """Muestra la vista de gestión de productos dentro del content_frame"""
        try:
            self.view.limpiar_contenido()
            productos_view = ProductosView(master=self.view.content_frame)
            productos_view.pack(fill="both", expand=True)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir Productos: {e}")

    def mostrar_clientes(self):
        """Muestra la vista de gestión de clientes/ventas dentro del content_frame"""
        try:
            self.view.limpiar_contenido()
            clientes_view = ClientesView(master=self.view.content_frame)
            clientes_view.pack(fill="both", expand=True)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir Clientes: {e}")

    def iniciar_aplicacion(self, usuario, rol):
        self.usuario = usuario
        self.rol = rol
        self.root = tk.Tk()
        self.view = InicioView(self.root, self)
        self.view.crear_vista_principal(usuario, rol)
        # Mostrar inicio por defecto
        try:
            self.mostrar_inicio()
        except Exception:
            pass
        self.root.mainloop()