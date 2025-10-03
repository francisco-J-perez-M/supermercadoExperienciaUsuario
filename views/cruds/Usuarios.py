# Usuarios.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional
from ui_helper import UIHelper
from controllers.UsuariosController import (
    create_user,
    get_user_by_id,
    get_user_by_username,
    list_users,
    update_user,
    delete_user,
    UsuarioError,
    UsuarioExists,
    UsuarioNotFound,
    ensure_indexes,
)
import threading

class UsuariosView(tk.Frame):
    """
    Vista CRUD para usuarios usando UIHelper para estilo.
    Integrar esta clase en la ventana principal: UsuariosView(root).pack(fill='both', expand=True)
    """

    PAGE_SIZE = 25

    def __init__(self, master=None):
        super().__init__(master, bg=UIHelper.COLOR_PRIMARIO)
        UIHelper.configurar_estilo_modo_oscuro()
        self.master = master
        self.current_page = 0
        self.search_q = tk.StringVar()
        self._build_ui()
        # Garantizar índices (ejecutar en hilo para no bloquear UI)
        threading.Thread(target=ensure_indexes, daemon=True).start()
        self._load_users()

    def _build_ui(self):
        # Encabezado con búsqueda y botones
        header = tk.Frame(self, bg=UIHelper.COLOR_PRIMARIO)
        header.pack(fill="x", padx=12, pady=12)

        title = tk.Label(header, text="Usuarios", fg=UIHelper.COLOR_TEXTO,
                         bg=UIHelper.COLOR_PRIMARIO, font=("Segoe UI", 16, "bold"))
        title.pack(side="left")

        search_entry = ttk.Entry(header, textvariable=self.search_q, width=30)
        search_entry.pack(side="right", padx=(6, 0))
        search_entry.bind("<Return>", lambda e: self._on_search())

        search_btn = tk.Button(header, text="Buscar", command=self._on_search)
        UIHelper.estilizar_boton(search_btn)
        search_btn.pack(side="right", padx=6)

        nuevo_btn = tk.Button(header, text="Nuevo usuario", command=self._on_create)
        UIHelper.estilizar_boton(nuevo_btn, bg=UIHelper.COLOR_EXITO)
        nuevo_btn.pack(side="right", padx=6)

        # Tabla de usuarios
        cols = ("_id", "usuario", "rol", "created_at")
        table_frame = tk.Frame(self, bg=UIHelper.COLOR_PRIMARIO)
        table_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse", height=15)
        self.tree.heading("_id", text="ID")
        self.tree.heading("usuario", text="Usuario")
        self.tree.heading("rol", text="Rol")
        self.tree.heading("created_at", text="Creado")
        self.tree.column("_id", width=180, anchor="w")
        self.tree.column("usuario", width=140, anchor="w")
        self.tree.column("rol", width=100, anchor="center")
        self.tree.column("created_at", width=160, anchor="w")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Pie con acciones y paginación
        footer = tk.Frame(self, bg=UIHelper.COLOR_PRIMARIO)
        footer.pack(fill="x", padx=12, pady=(0,12))

        editar_btn = tk.Button(footer, text="Editar", command=self._on_edit)
        UIHelper.estilizar_boton(editar_btn, bg=UIHelper.COLOR_ACENTO)
        editar_btn.pack(side="left", padx=6)

        eliminar_btn = tk.Button(footer, text="Eliminar", command=self._on_delete)
        UIHelper.estilizar_boton(eliminar_btn, bg=UIHelper.COLOR_PELIGRO)
        eliminar_btn.pack(side="left", padx=6)

        prev_btn = tk.Button(footer, text="« Anterior", command=self._on_prev)
        UIHelper.estilizar_boton(prev_btn)
        prev_btn.pack(side="right", padx=6)

        next_btn = tk.Button(footer, text="Siguiente »", command=self._on_next)
        UIHelper.estilizar_boton(next_btn)
        next_btn.pack(side="right", padx=6)

        self.status_label = tk.Label(footer, text="", fg=UIHelper.COLOR_TEXTO_SECUNDARIO, bg=UIHelper.COLOR_PRIMARIO)
        self.status_label.pack(side="left")

    def _set_status(self, text: str):
        self.status_label.config(text=text)

    def _clear_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

    def _load_users(self):
        self._set_status("Cargando usuarios...")
        self._clear_table()
        try:
            q = self.search_q.get().strip()
            # list_users acepta limit/skip; usamos page-size
            skip = self.current_page * self.PAGE_SIZE
            users = list_users(limit=self.PAGE_SIZE, skip=skip)
            if q:
                users = [u for u in users if q.lower() in u.get("usuario", "").lower()]
            for u in users:
                self.tree.insert("", "end", values=(str(u.get("_id")), u.get("usuario"), u.get("rol"), u.get("created_at", "")))
            count = len(users)
            self._set_status(f"Mostrando {count} usuarios (página {self.current_page + 1})")
        except Exception as e:
            self._set_status(f"Error cargando usuarios: {e}")

    def _on_search(self):
        self.current_page = 0
        self._load_users()

    def _on_prev(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._load_users()

    def _on_next(self):
        # simple heuristic: advance and attempt load; if no results, go back
        self.current_page += 1
        self._load_users()
        if not self.tree.get_children():
            self.current_page = max(0, self.current_page - 1)
            self._load_users()

    def _selected_user_id(self) -> Optional[str]:
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.item(sel[0])["values"][0]

    def _on_create(self):
        dlg = UsuarioDialog(self.master, title="Crear usuario")
        if not dlg.result:
            return
        data = dlg.result
        try:
            user = create_user(data["usuario"], data["password"], data.get("rol", "vendedor"))
            messagebox.showinfo("Creado", f"Usuario '{user['usuario']}' creado correctamente")
            self._load_users()
        except UsuarioExists as ue:
            messagebox.showwarning("Existe", str(ue))
        except UsuarioError as e:
            messagebox.showerror("Error", str(e))

    def _on_edit(self):
        user_id = self._selected_user_id()
        if not user_id:
            messagebox.showinfo("Selecciona", "Selecciona un usuario para editar")
            return
        try:
            user = get_user_by_id(user_id)
        except UsuarioError as e:
            messagebox.showerror("Error", str(e))
            return

        dlg = UsuarioDialog(self.master, title="Editar usuario", initial=user, edit=True)
        if not dlg.result:
            return
        updates = dlg.result
        try:
            updated = update_user(user_id, updates)
            messagebox.showinfo("Actualizado", f"Usuario '{updated['usuario']}' actualizado")
            self._load_users()
        except UsuarioNotFound as nf:
            messagebox.showerror("No encontrado", str(nf))
        except UsuarioExists as ue:
            messagebox.showwarning("Existe", str(ue))
        except UsuarioError as e:
            messagebox.showerror("Error", str(e))

    def _on_delete(self):
        user_id = self._selected_user_id()
        if not user_id:
            messagebox.showinfo("Selecciona", "Selecciona un usuario para eliminar")
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar usuario seleccionado?"):
            return
        try:
            ok = delete_user(user_id)
            if ok:
                messagebox.showinfo("Eliminado", "Usuario eliminado correctamente")
                self._load_users()
            else:
                messagebox.showwarning("No encontrado", "El usuario no existía")
        except UsuarioError as e:
            messagebox.showerror("Error", str(e))

class UsuarioDialog(simpledialog.Dialog):
    """
    Diálogo para crear/editar usuario.
    Si edit=True, permite dejar contraseña vacía para no cambiarla.
    Resultado: dict con keys 'usuario', optional 'password', 'rol'
    """

    ROLES = ["administrador", "vendedor", "cajero", "supervisor"]

    def __init__(self, parent, title=None, initial: Optional[dict] = None, edit: bool = False):
        self.initial = initial or {}
        self.edit = edit
        self.result = None
        super().__init__(parent, title=title)

    def body(self, master):
        master.configure(bg=UIHelper.COLOR_PRIMARIO)
        tk.Label(master, text="Usuario", bg=UIHelper.COLOR_PRIMARIO, fg=UIHelper.COLOR_TEXTO).grid(row=0, column=0, sticky="w")
        self.usuario_var = tk.StringVar(value=self.initial.get("usuario", ""))
        self.usuario_entry = ttk.Entry(master, textvariable=self.usuario_var)
        self.usuario_entry.grid(row=0, column=1, pady=6, padx=6)

        tk.Label(master, text="Contraseña", bg=UIHelper.COLOR_PRIMARIO, fg=UIHelper.COLOR_TEXTO).grid(row=1, column=0, sticky="w")
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(master, textvariable=self.password_var, show="*")
        self.password_entry.grid(row=1, column=1, pady=6, padx=6)
        if not self.edit:
            self.password_entry.focus_set()

        tk.Label(master, text="Rol", bg=UIHelper.COLOR_PRIMARIO, fg=UIHelper.COLOR_TEXTO).grid(row=2, column=0, sticky="w")
        self.rol_var = tk.StringVar(value=self.initial.get("rol", "vendedor"))
        self.rol_combo = ttk.Combobox(master, values=self.ROLES, state="readonly", textvariable=self.rol_var)
        self.rol_combo.grid(row=2, column=1, pady=6, padx=6)

        return self.usuario_entry

    def validate(self):
        usuario = self.usuario_var.get().strip()
        password = self.password_var.get()
        rol = self.rol_var.get()
        if not usuario:
            messagebox.showwarning("Validación", "El nombre de usuario es requerido")
            return False
        if not self.edit and not password:
            messagebox.showwarning("Validación", "La contraseña es requerida")
            return False
        return True

    def apply(self):
        data = {"usuario": self.usuario_var.get().strip(), "rol": self.rol_var.get()}
        pwd = self.password_var.get()
        if pwd:
            data["password"] = pwd
        self.result = data

# Ejemplo de arranque independiente para pruebas
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Super Pancho - Usuarios")
    root.configure(bg=UIHelper.COLOR_PRIMARIO)
    root.geometry("850x560")
    app = UsuariosView(master=root)
    app.pack(fill="both", expand=True)
    root.mainloop()
