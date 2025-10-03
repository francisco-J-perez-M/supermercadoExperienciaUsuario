import tkinter as tk
from tkinter import messagebox
from db.conexion import get_db
from controllers.PuntoVentaController import PuntoVentaController
from controllers.InicioController import InicioController
from views.LoginView import LoginView

class LoginController:
    def __init__(self):
        self.root = tk.Tk()
        self.view = LoginView(self.root, self)
    
    def login(self):
        credenciales = self.view.obtener_credenciales()
        usuario = credenciales['usuario']
        password = credenciales['password']

        if not usuario or not password:
            messagebox.showwarning("Campos vacíos", "Debes ingresar usuario y contraseña")
            return

        try:
            db = get_db()
            coleccion_usuarios = db["usuarios"]
            user = coleccion_usuarios.find_one({"usuario": usuario, "password": password})

            if user:
                rol = user["rol"]
                messagebox.showinfo("Bienvenido", f"Usuario: {usuario}\nRol: {rol}")
                self.view.cerrar_vista()
                
                # Redirigir según el rol
                if rol == "administrador":
                    inicio_controller = InicioController()
                    inicio_controller.iniciar_aplicacion(usuario, rol)
                else:  # vendedor u otros roles
                    punto_venta_controller = PuntoVentaController()
                    punto_venta_controller.iniciar_app(rol)
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos")
                self.view.mostrar_error("Credenciales incorrectas")
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar a la base de datos: {str(e)}")

    def mostrar_login(self):
        self.view.crear_vista_login()
        self.root.mainloop()