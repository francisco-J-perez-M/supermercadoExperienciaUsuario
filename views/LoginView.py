import tkinter as tk
from ui_helper import UIHelper

class LoginView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.entry_usuario = None
        self.entry_password = None

    def crear_vista_login(self):
        self.root.title("Login - Supermercado")
        self.root.geometry("350x230")
        self.root.config(bg=UIHelper.COLOR_PRIMARIO)

        frame = tk.Frame(self.root, bg=UIHelper.COLOR_SECUNDARIO, bd=2, relief="ridge")
        frame.place(relx=0.5, rely=0.5, anchor="center", width=300, height=190)

        lbl_titulo = tk.Label(frame, text="🔑 Iniciar Sesión", 
                             font=("Segoe UI", 14, "bold"), 
                             bg=UIHelper.COLOR_SECUNDARIO, 
                             fg=UIHelper.COLOR_TEXTO)
        lbl_titulo.pack(pady=10)

        lbl_usuario = tk.Label(frame, text="Usuario:", 
                              bg=UIHelper.COLOR_SECUNDARIO, 
                              fg=UIHelper.COLOR_TEXTO, 
                              anchor="w")
        lbl_usuario.pack(fill="x", padx=20)
        self.entry_usuario = tk.Entry(frame, 
                                     bg=UIHelper.COLOR_TERCIARIO,
                                     fg=UIHelper.COLOR_TEXTO,
                                     insertbackground=UIHelper.COLOR_TEXTO,
                                     relief="flat",
                                     bd=0)
        self.entry_usuario.pack(fill="x", padx=20, pady=5)
        self.entry_usuario.bind('<Return>', lambda e: self.controller.login())

        lbl_password = tk.Label(frame, text="Contraseña:", 
                               bg=UIHelper.COLOR_SECUNDARIO, 
                               fg=UIHelper.COLOR_TEXTO, 
                               anchor="w")
        lbl_password.pack(fill="x", padx=20)
        self.entry_password = tk.Entry(frame, show="*",
                                      bg=UIHelper.COLOR_TERCIARIO,
                                      fg=UIHelper.COLOR_TEXTO,
                                      insertbackground=UIHelper.COLOR_TEXTO,
                                      relief="flat",
                                      bd=0)
        self.entry_password.pack(fill="x", padx=20, pady=5)
        self.entry_password.bind('<Return>', lambda e: self.controller.login())

        btn_login = tk.Button(frame, text="Ingresar", command=self.controller.login)
        UIHelper.estilizar_boton(btn_login)
        btn_login.pack(pady=10)

        self.entry_usuario.focus_set()

    def obtener_credenciales(self):
        return {
            'usuario': self.entry_usuario.get().strip(),
            'password': self.entry_password.get().strip()
        }

    def limpiar_campos(self):
        self.entry_usuario.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)
        self.entry_usuario.focus_set()

    def mostrar_error(self, mensaje):
        self.limpiar_campos()

    def cerrar_vista(self):
        self.root.destroy()