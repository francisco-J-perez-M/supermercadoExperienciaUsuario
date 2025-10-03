# LoginView.py
import tkinter as tk
from tkinter import messagebox, simpledialog
from ui_helper import UIHelper
from tkinter import ttk

class RegistroDialog(simpledialog.Dialog):
    ROLES = ["vendedor", "administrador", "cajero", "supervisor"]

    def __init__(self, parent, controller):
        self.controller = controller
        self.result = None
        super().__init__(parent, title="Registrar nuevo usuario")

    def body(self, master):
        master.configure(bg=UIHelper.COLOR_SECUNDARIO)
        tk.Label(master, text="Usuario:", bg=UIHelper.COLOR_SECUNDARIO, fg=UIHelper.COLOR_TEXTO).grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self.usuario_var = tk.StringVar()
        tk.Entry(master, textvariable=self.usuario_var, bg=UIHelper.COLOR_TERCIARIO, fg=UIHelper.COLOR_TEXTO).grid(row=0, column=1, padx=8, pady=6)

        tk.Label(master, text="Contraseña:", bg=UIHelper.COLOR_SECUNDARIO, fg=UIHelper.COLOR_TEXTO).grid(row=1, column=0, sticky="w", padx=8, pady=6)
        self.password_var = tk.StringVar()
        tk.Entry(master, textvariable=self.password_var, show="*", bg=UIHelper.COLOR_TERCIARIO, fg=UIHelper.COLOR_TEXTO).grid(row=1, column=1, padx=8, pady=6)

        tk.Label(master, text="Rol:", bg=UIHelper.COLOR_SECUNDARIO, fg=UIHelper.COLOR_TEXTO).grid(row=2, column=0, sticky="w", padx=8, pady=6)
        self.rol_var = tk.StringVar(value="vendedor")
        ttk.Combobox(master, values=self.ROLES, textvariable=self.rol_var, state="readonly").grid(row=2, column=1, padx=8, pady=6)

        return None

    def validate(self):
        u = self.usuario_var.get().strip()
        p = self.password_var.get()
        if not u:
            messagebox.showwarning("Validación", "Usuario requerido")
            return False
        if not p or len(p) < 6:
            messagebox.showwarning("Validación", "Contraseña requerida (min 6 caracteres)")
            return False
        return True

    def apply(self):
        self.result = {
            "usuario": self.usuario_var.get().strip(),
            "password": self.password_var.get(),
            "rol": self.rol_var.get()
        }

class LoginView:
    """
    Vista de login. Esta vista se mostrará sólo después de que AvisoBase haya sido despachado
    (si la BD no estaba presente) o inmediatamente si la BD ya existía.
    """

    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.entry_usuario = None
        self.entry_password = None

    def crear_vista_login(self):
        self.root.title("Login - Supermercado")
        self.root.geometry("380x280")
        self.root.config(bg=UIHelper.COLOR_PRIMARIO)
        # Asegurar que la ventana root esté visible
        try:
            self.root.deiconify()
        except Exception:
            pass

        frame = tk.Frame(self.root, bg=UIHelper.COLOR_SECUNDARIO, bd=2, relief="ridge")
        frame.place(relx=0.5, rely=0.5, anchor="center", width=340, height=240)

        lbl_titulo = tk.Label(frame, text="🔑 Iniciar Sesión",
                             font=("Segoe UI", 14, "bold"),
                             bg=UIHelper.COLOR_SECUNDARIO,
                             fg=UIHelper.COLOR_TEXTO)
        lbl_titulo.pack(pady=8)

        lbl_usuario = tk.Label(frame, text="Usuario:", bg=UIHelper.COLOR_SECUNDARIO, fg=UIHelper.COLOR_TEXTO, anchor="w")
        lbl_usuario.pack(fill="x", padx=20)
        self.entry_usuario = tk.Entry(frame,
                                     bg=UIHelper.COLOR_TERCIARIO,
                                     fg=UIHelper.COLOR_TEXTO,
                                     insertbackground=UIHelper.COLOR_TEXTO,
                                     relief="flat",
                                     bd=0)
        self.entry_usuario.pack(fill="x", padx=20, pady=4)
        self.entry_usuario.bind('<Return>', lambda e: self.controller.intentar_login())

        lbl_password = tk.Label(frame, text="Contraseña:", bg=UIHelper.COLOR_SECUNDARIO, fg=UIHelper.COLOR_TEXTO, anchor="w")
        lbl_password.pack(fill="x", padx=20)
        self.entry_password = tk.Entry(frame, show="*",
                                      bg=UIHelper.COLOR_TERCIARIO,
                                      fg=UIHelper.COLOR_TEXTO,
                                      insertbackground=UIHelper.COLOR_TEXTO,
                                      relief="flat",
                                      bd=0)
        self.entry_password.pack(fill="x", padx=20, pady=4)
        self.entry_password.bind('<Return>', lambda e: self.controller.intentar_login())

        btn_frame = tk.Frame(frame, bg=UIHelper.COLOR_SECUNDARIO)
        btn_frame.pack(pady=6, fill="x", padx=20)

        btn_login = tk.Button(btn_frame, text="Ingresar", command=self.controller.intentar_login)
        UIHelper.estilizar_boton(btn_login)
        btn_login.pack(side="left", expand=True, fill="x", padx=(0,6))

        btn_reg = tk.Button(btn_frame, text="Registrarse", command=self._on_registrarse)
        UIHelper.estilizar_boton(btn_reg, bg=UIHelper.COLOR_ACENTO)
        btn_reg.pack(side="right", expand=True, fill="x", padx=(6,0))

        self.entry_usuario.focus_set()

    def _on_registrarse(self):
        dlg = RegistroDialog(self.root, self.controller)
        if not dlg.result:
            return
        data = dlg.result
        ok = self.controller.registrar_usuario(data["usuario"], data["password"], data.get("rol", "vendedor"))
        if ok:
            self.entry_usuario.delete(0, tk.END)
            self.entry_usuario.insert(0, data["usuario"])
            self.entry_password.delete(0, tk.END)
            self.entry_password.insert(0, data["password"])
            messagebox.showinfo("Listo", "Registro completado. Ahora puedes ingresar.")

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
        try:
            self.root.destroy()
        except Exception:
            pass
