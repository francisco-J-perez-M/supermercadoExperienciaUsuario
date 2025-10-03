# AvisoBase.py
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from ui_helper import UIHelper

class AvisoBase(tk.Toplevel):
    """
    Ventana separada que muestra el aviso de BD ausente y ofrece:
      - Cargar default (500000)
      - Seleccionar cantidad
      - Iniciar creación en terminal (delegando en el controlador)
    """
    def __init__(self, parent, controller, default_total=500_000):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.default_total = default_total
        self.title("Base de datos no encontrada")
        self.geometry("420x200")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        frame = tk.Frame(self, bg=UIHelper.COLOR_SECUNDARIO)
        frame.pack(expand=True, fill="both", padx=12, pady=12)

        lbl = tk.Label(frame,
                       text="No se encontraron las colecciones iniciales.\nPuedes crear la base de datos ahora.",
                       bg=UIHelper.COLOR_SECUNDARIO,
                       fg=UIHelper.COLOR_TEXTO,
                       font=("Segoe UI", 11),
                       justify="left")
        lbl.pack(fill="x", pady=(0,8))

        hint = tk.Label(frame,
                        text="Opciones de creación:",
                        bg=UIHelper.COLOR_SECUNDARIO,
                        fg=UIHelper.COLOR_TEXTO_SECUNDARIO,
                        font=("Segoe UI", 9, "italic"))
        hint.pack(anchor="w", pady=(0,8))

        btn_default = tk.Button(frame,
                                text=f"Cargar default ({self.default_total})",
                                command=self._on_default,
                                anchor="w")
        btn_select = tk.Button(frame,
                               text="Seleccionar cantidad total",
                               command=self._on_select,
                               anchor="w")

        from functools import partial
        UIHelper.estilizar_boton(btn_default, bg=UIHelper.COLOR_ACENTO)
        UIHelper.estilizar_boton(btn_select, bg=UIHelper.COLOR_TERCIARIO)
        btn_default.pack(fill="x", pady=4)
        btn_select.pack(fill="x", pady=4)

        btn_frame = tk.Frame(frame, bg=UIHelper.COLOR_SECUNDARIO)
        btn_frame.pack(fill="x", pady=(10,0))
        btn_cancel = tk.Button(btn_frame, text="Cerrar", command=self._on_close)
        UIHelper.estilizar_boton(btn_cancel, bg=UIHelper.COLOR_TERCIARIO)
        btn_cancel.pack(side="right")

    def _on_default(self):
        if not messagebox.askyesno("Confirmar", f"Crear base de datos con {self.default_total} registros. ¿Continuar?", parent=self):
            return
        # delegar al controlador: iniciar seed en terminal (no bloqueante)
        self.controller._start_seed_in_terminal(self.default_total)
        messagebox.showinfo("Iniciado", "La creación ha sido iniciada en la terminal.", parent=self)
        self._on_close()

    def _on_select(self):
        respuesta = simpledialog.askstring("Poblado inicial", "Número total de clientes a generar (ej. 500000):", parent=self)
        if respuesta is None:
            return
        try:
            total = int(respuesta)
            if total <= 0:
                raise ValueError()
        except Exception:
            messagebox.showwarning("Entrada inválida", "Ingresa un número entero positivo", parent=self)
            return
        if not messagebox.askyesno("Confirmar", f"Crear base de datos con {total} registros. ¿Continuar?", parent=self):
            return
        self.controller._start_seed_in_terminal(total)
        messagebox.showinfo("Iniciado", "La creación ha sido iniciada en la terminal.", parent=self)
        self._on_close()

    def _on_close(self):
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()
