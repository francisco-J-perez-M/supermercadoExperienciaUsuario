# LoginController.py
import tkinter as tk
from tkinter import messagebox, Toplevel, ttk
import threading
import subprocess
import sys
import os
import re
from typing import Optional
from db.conexion import get_db
from controllers.PuntoVentaController import PuntoVentaController
from controllers.InicioController import InicioController
from controllers.UsuariosController import authenticate, create_user, UsuarioError, UsuarioExists, UsuarioNotFound
from views.LoginView import LoginView
from views.AvisoBase import AvisoBase

class SeedProgressDialog:
    """Diálogo modal con Progressbar y estado."""
    PROG_PATTERN = re.compile(r"Inserted\s+(\d+)\s*/\s*(\d+)", re.IGNORECASE)

    def __init__(self, parent, initial_total: int):
        self.parent = parent
        self.total = max(1, initial_total)
        self.top = Toplevel(parent)
        self.top.title("Creando base de datos")
        self.top.geometry("480x140")
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()

        lbl = tk.Label(self.top, text="Creando base de datos. Esto puede tardar varios minutos...", anchor="w")
        lbl.pack(fill="x", padx=12, pady=(10,4))

        self.progress = ttk.Progressbar(self.top, orient="horizontal", mode="determinate", maximum=self.total)
        self.progress.pack(fill="x", padx=12, pady=6)

        self.status_var = tk.StringVar(value="Preparando...")
        self.lbl_status = tk.Label(self.top, textvariable=self.status_var, anchor="w")
        self.lbl_status.pack(fill="x", padx=12, pady=(0,8))

        btn_frame = tk.Frame(self.top)
        btn_frame.pack(fill="x", padx=12, pady=(0,10))
        self.btn_close = tk.Button(btn_frame, text="Cerrar (seguir en segundo plano)", command=self._close)
        self.btn_close.pack(side="right")
        self.closed = False

    def _close(self):
        try:
            self.top.grab_release()
            self.top.destroy()
        finally:
            self.closed = True

    def update_status(self, text: str):
        if self.closed:
            return
        try:
            self.status_var.set(text)
        except Exception:
            pass

    def set_maximum(self, maximum: int):
        if maximum <= 0:
            return
        try:
            self.total = maximum
            self.progress.config(maximum=maximum)
        except Exception:
            pass

    def update_progress(self, value: int):
        if self.closed:
            return
        try:
            self.progress['value'] = min(self.total, max(0, int(value)))
        except Exception:
            pass

    def destroy(self):
        if not self.closed:
            try:
                self.top.grab_release()
                self.top.destroy()
            finally:
                self.closed = True

class LoginController:
    """
    Flujo:
      - Al iniciar, si falta la BD abre AvisoBase (ventana separada).
      - AvisoBase delega la creación al controller (default o cantidad).
      - Mientras el seed corre, se muestra SeedProgressDialog.
      - Al completarse con éxito aparece mensaje "BD lista" y se muestra el login.
      - Si el usuario cierra AvisoBase sin iniciar seed, se muestra el login inmediatamente.
    """

    DEFAULT_TOTAL = 500_000

    def __init__(self):
        self.root = tk.Tk()
        self.view = None
        self._seed_proc = None
        self._seed_thread = None
        try:
            self.root.withdraw()
        except Exception:
            pass

    def _db_exists(self) -> bool:
        try:
            db = get_db()
            if db is None:
                return False
            colls = db.list_collection_names()
            return "usuarios" in colls and "productos" in colls and "areas" in colls
        except Exception:
            return False

    def _find_script_path(self) -> Optional[str]:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        candidates = [
            os.path.join(base_dir, "scripts", "script.py"),
            os.path.join(base_dir, "script.py"),
            os.path.abspath(os.path.join(os.getcwd(), "scripts", "script.py")),
            os.path.abspath(os.path.join(os.getcwd(), "script.py")),
        ]
        return next((p for p in candidates if os.path.exists(p)), None)

    def _run_seed_with_progress(self, total: int):
        script_path = self._find_script_path()
        if not script_path:
            self.root.after(0, lambda: messagebox.showerror("Error", "No se encontró scripts/script.py para crear la base de datos"))
            self.root.after(0, self._show_login)
            return

        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        progress_dialog = SeedProgressDialog(self.root, initial_total=total)

        def worker():
            nonlocal progress_dialog
            cmd = [sys.executable, script_path, str(total)]
            proc = None
            try:
                proc = subprocess.Popen(cmd, cwd=project_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
                self._seed_proc = proc

                reported_total = total
                # Leer stdout línea por línea
                for raw in proc.stdout:
                    line = raw.strip()
                    self.root.after(0, lambda l=line: progress_dialog.update_status(l))
                    m = SeedProgressDialog.PROG_PATTERN.search(line)
                    if m:
                        try:
                            inserted = int(m.group(1))
                            reported_total = int(m.group(2)) or reported_total
                            if reported_total and progress_dialog.total != reported_total:
                                self.root.after(0, lambda rt=reported_total: progress_dialog.set_maximum(rt))
                            self.root.after(0, lambda v=inserted: progress_dialog.update_progress(v))
                        except Exception:
                            pass

                stderr = proc.stderr.read()
                ret = proc.wait()

                if ret == 0:
                    self.root.after(0, lambda: progress_dialog.update_progress(reported_total))
                    self.root.after(0, lambda: progress_dialog.update_status("Completado correctamente."))
                    self.root.after(0, lambda: messagebox.showinfo("Base de datos lista", "La base de datos está lista. Ahora puede iniciar sesión."))
                else:
                    err = stderr or f"El script terminó con código {ret}"
                    self.root.after(0, lambda: messagebox.showerror("Error en creación", err))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error ejecutando script", str(e)))
            finally:
                try:
                    self.root.after(0, lambda: progress_dialog.destroy())
                except Exception:
                    pass
                # Siempre aseguramos mostrar login al final del flujo (éxito o fallo)
                self.root.after(0, self._show_login)

        t = threading.Thread(target=worker, daemon=True)
        t.start()
        self._seed_thread = t

    # Métodos públicos invocados por AvisoBase
    def start_seed_default(self):
        self._run_seed_with_progress(self.DEFAULT_TOTAL)

    def start_seed_with_total(self, total: int):
        self._run_seed_with_progress(total)

    def mostrar_aviso_base(self):
        AvisoBase(self.root, controller=self, default_total=self.DEFAULT_TOTAL)

    def _show_login(self):
        if not self.view:
            self.view = LoginView(self.root, self)
            self.view.crear_vista_login()
        try:
            self.root.deiconify()
            if not getattr(self.root, "_mainloop_started", False):
                self.root._mainloop_started = True
                self.root.mainloop()
        except Exception:
            pass

    def mostrar_login(self):
        """
        Flujo clásico: si falta la BD abre AvisoBase (ventana separada)
        y luego continúa mostrando el login (queda detrás).
        """
        # intentar ocultar root brevemente (mantener comportamiento previo opcional)
        try:
            self.root.withdraw()
        except Exception:
            pass

        # abrir aviso si falta la BD
        if not self._db_exists():
            self.mostrar_aviso_base()

        # mostrar login (queda detrás si AvisoBase modal está activo)
        self._show_login()

    def intentar_login(self):
        credenciales = self.view.obtener_credenciales()
        usuario = credenciales.get('usuario')
        password = credenciales.get('password')

        if not usuario or not password:
            messagebox.showwarning("Campos vacíos", "Debes ingresar usuario y contraseña")
            return

        try:
            try:
                user_doc = authenticate(usuario, password)
            except UsuarioNotFound:
                user_doc = None

            if user_doc:
                rol = user_doc.get("rol", "vendedor")
                messagebox.showinfo("Bienvenido", f"Usuario: {usuario}\nRol: {rol}")
                self.view.cerrar_vista()
                if rol == "administrador":
                    inicio = InicioController()
                    inicio.iniciar_aplicacion(usuario, rol)
                else:
                    pv = PuntoVentaController()
                    pv.iniciar_app(rol)
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos")
                self.view.mostrar_error("Credenciales incorrectas")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar a la base de datos: {str(e)}")

    def registrar_usuario(self, usuario: str, password: str, rol: str = "vendedor"):
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
