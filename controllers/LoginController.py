# LoginController.py
import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, ttk
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
    """Ventana modal con Progressbar que muestra porcentaje y estado."""
    def __init__(self, parent, total_expected: int):
        self.parent = parent
        self.total_expected = max(1, total_expected)
        self.top = Toplevel(parent)
        self.top.title("Creando base de datos")
        self.top.geometry("480x140")
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()

        lbl = tk.Label(self.top, text="Creando base de datos. Esto puede tardar varios minutos...", anchor="w")
        lbl.pack(fill="x", padx=12, pady=(10,4))

        self.progress = ttk.Progressbar(self.top, orient="horizontal", mode="determinate", maximum=self.total_expected)
        self.progress.pack(fill="x", padx=12, pady=6)

        self.status_var = tk.StringVar(value="Iniciando...")
        self.lbl_status = tk.Label(self.top, textvariable=self.status_var, anchor="w")
        self.lbl_status.pack(fill="x", padx=12, pady=(0,8))

        btn_frame = tk.Frame(self.top)
        btn_frame.pack(fill="x", padx=12, pady=(0,10))
        self.btn_close = tk.Button(btn_frame, text="Cerrar (seguir en segundo plano)", command=self._close)
        self.btn_close.pack(side="right")
        self._closed = False

    def _close(self):
        try:
            self.top.grab_release()
            self.top.destroy()
        finally:
            self._closed = True

    def update_progress(self, value: int):
        if self._closed:
            return
        try:
            self.progress['value'] = min(self.total_expected, max(0, int(value)))
        except Exception:
            pass

    def update_status(self, text: str):
        if self._closed:
            return
        try:
            self.status_var.set(text)
        except Exception:
            pass

    def set_maximum(self, maximum: int):
        if maximum <= 0:
            return
        self.total_expected = maximum
        try:
            self.progress.config(maximum=maximum)
        except Exception:
            pass

    def destroy(self):
        if not self._closed:
            try:
                self.top.grab_release()
                self.top.destroy()
            finally:
                self._closed = True

class LoginController:
    """
    LoginController actualizado:
      - si falta la BD muestra AvisoBase (ventana separada)
      - permite iniciar la creación via scripts/script.py
      - muestra una ventana de progreso con barra y estado leyendo stdout del script
      - no requiere librerías adicionales (usa tkinter)
    """

    DEFAULT_TOTAL = 500_000
    PROGRESS_PATTERN = re.compile(r"Inserted\s+(\d+)\s*/\s*(\d+)", re.IGNORECASE)

    def __init__(self):
        self.root = tk.Tk()
        self.view = None
        self._seed_process = None
        self._seed_thread = None
        try:
            self.root.withdraw()
        except Exception:
            pass

    def _db_exists(self) -> bool:
        try:
            db = get_db()
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

    def _run_script_with_progress(self, total: int):
        """
        Ejecuta script.py y muestra un diálogo de progreso que lee stdout
        en tiempo real y actualiza la barra con líneas del tipo:
            Inserted X/TOTAL clientes
        Si no se detecta ese patrón, la barra queda en modo indeterminado hasta finalizar.
        """
        script_path = self._find_script_path()
        if not script_path:
            self.root.after(0, lambda: messagebox.showerror("Error", "No se encontró script.py para crear la base de datos"))
            self._show_login()
            return

        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        progress_dialog = None

        def worker():
            nonlocal progress_dialog
            cmd = [sys.executable, script_path, str(total)]
            try:
                # Capturamos stdout para parsearlo y actualizar GUI
                proc = subprocess.Popen(cmd, cwd=project_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
                self._seed_process = proc

                # Crear diálogo en hilo principal antes de leer
                def create_dialog():
                    nonlocal progress_dialog
                    progress_dialog = SeedProgressDialog(self.root, total_expected=total)
                self.root.after(0, create_dialog)

                inserted = 0
                reported_total = total
                # Leer stdout línea a línea
                for raw_line in proc.stdout:
                    line = raw_line.strip()
                    # actualizar status textual
                    if progress_dialog:
                        self.root.after(0, lambda l=line: progress_dialog.update_status(l))
                    # intentar parsear progreso
                    m = self.PROGRESS_PATTERN.search(line)
                    if m:
                        try:
                            inserted = int(m.group(1))
                            reported_total = int(m.group(2)) or reported_total
                            # ajustar máximo si el script reporta distinto
                            if progress_dialog and progress_dialog.total_expected != reported_total:
                                self.root.after(0, lambda rt=reported_total: progress_dialog.set_maximum(rt))
                            if progress_dialog:
                                self.root.after(0, lambda val=inserted: progress_dialog.update_progress(val))
                        except Exception:
                            pass

                # leer stderr completo (por si hay errores)
                stderr = proc.stderr.read()
                ret = proc.wait()

                if ret == 0:
                    if progress_dialog:
                        # asegurar barra completa y estado final
                        self.root.after(0, lambda: progress_dialog.update_progress(reported_total))
                        self.root.after(0, lambda: progress_dialog.update_status("Completado correctamente."))
                        # informar al usuario
                        self.root.after(0, lambda: messagebox.showinfo("Poblado completado", f"Poblado finalizado: {reported_total} clientes creados"))
                        self.root.after(0, lambda: progress_dialog.destroy())
                else:
                    err_msg = stderr or f"El script terminó con código {ret}"
                    if progress_dialog:
                        self.root.after(0, lambda: progress_dialog.update_status("Error durante el poblado"))
                        self.root.after(0, lambda: progress_dialog.destroy())
                    self.root.after(0, lambda: messagebox.showerror("Error en poblado", err_msg))

            except Exception as e:
                try:
                    if progress_dialog:
                        self.root.after(0, lambda: progress_dialog.destroy())
                finally:
                    self.root.after(0, lambda: messagebox.showerror("Error ejecutando script", str(e)))
            finally:
                try:
                    if proc and proc.stdout:
                        proc.stdout.close()
                except Exception:
                    pass
                try:
                    if proc and proc.stderr:
                        proc.stderr.close()
                except Exception:
                    pass
                # asegurar que la vista de login se muestre al terminar
                try:
                    self.root.after(0, self._show_login)
                except Exception:
                    pass

        self._seed_thread = threading.Thread(target=worker, daemon=True)
        self._seed_thread.start()

    # retrocompatibilidad con AvisoBase
    def _start_seed_in_terminal(self, total: int):
        return self._run_script_with_progress(total)

    def start_seed_default(self):
        return self._run_script_with_progress(self.DEFAULT_TOTAL)

    def start_seed_with_total(self, total: int):
        return self._run_script_with_progress(total)

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
        if not self._db_exists():
            # abrir aviso separado para permitir elegir crear DB
            self.mostrar_aviso_base()
            # si el usuario cierra aviso sin iniciar seed, mostrar login igual
            self._show_login()
        else:
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
