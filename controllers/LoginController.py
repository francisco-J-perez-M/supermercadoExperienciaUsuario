# LoginController.py
import tkinter as tk
from tkinter import messagebox
from db.conexion import get_db
from controllers.PuntoVentaController import PuntoVentaController
from controllers.InicioController import InicioController
from views.LoginView import LoginView
from controllers.UsuariosController import authenticate, create_user, UsuarioError, UsuarioExists, UsuarioNotFound

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
            # Usar authenticate del UsuariosController (que maneja hash)
            try:
                user_doc = authenticate(usuario, password)
            except UsuarioNotFound:
                user_doc = None

            if user_doc:
                rol = user_doc.get("rol", "vendedor")
                messagebox.showinfo("Bienvenido", f"Usuario: {usuario}\nRol: {rol}")
                self.view.cerrar_vista()

                # Redirigir según el rol
                if rol == "administrador":
                    inicio_controller = InicioController()
                    inicio_controller.iniciar_aplicacion(usuario, rol)
                else:
                    punto_venta_controller = PuntoVentaController()
                    punto_venta_controller.iniciar_app(rol)
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos")
                self.view.mostrar_error("Credenciales incorrectas")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar a la base de datos: {str(e)}")

    def registrar_usuario(self, usuario: str, password: str, rol: str = "vendedor"):
        """Handler llamado desde la vista para crear un nuevo usuario"""
        try:
            nuevo = create_user(usuario, password, rol)
            messagebox.showinfo("Registro", f"Usuario '{nuevo['usuario']}' creado correctamente")
            return True
        except UsuarioExists as ue:
            messagebox.showwarning("Existe", str(ue))
        except UsuarioError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear usuario: {e}")
        return False

    def mostrar_login(self):
        self.view.crear_vista_login()
        self.root.mainloop()
