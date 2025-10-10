# Clientes.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from typing import Optional, List, Dict, Any
from ui_helper import UIHelper
from controllers.ClientesController import (
    create_cliente,
    get_cliente_by_id,
    list_clientes,
    update_cliente,
    delete_cliente,
    bulk_insert_clientes,
    sample_cliente_random,
    ClienteError,
    ClienteNotFound,
    ensure_indexes,
)
import threading
import json
from datetime import datetime

class ClientesView(tk.Frame):
    """
    Vista CRUD para clientes/ventas usando UIHelper para estilo.
    Integrar en la ventana principal: ClientesView(root).pack(fill='both', expand=True)
    """

    PAGE_SIZE = 30

    def __init__(self, master=None):
        super().__init__(master, bg=UIHelper.COLOR_PRIMARIO)
        UIHelper.configurar_estilo_ttk()
        self.master = master
        self.current_page = 0
        self.search_q = tk.StringVar()
        self.desde = tk.StringVar()
        self.hasta = tk.StringVar()
        self._build_ui()
        threading.Thread(target=ensure_indexes, daemon=True).start()
        self._load_clientes()

    def _build_ui(self):
        header = tk.Frame(self, bg=UIHelper.COLOR_PRIMARIO)
        header.pack(fill="x", padx=12, pady=12)

        title = tk.Label(header, text="Clientes / Ventas", fg=UIHelper.COLOR_TEXTO,
                         bg=UIHelper.COLOR_PRIMARIO, font=("Segoe UI", 16, "bold"))
        title.pack(side="left")

        # Filtros: fecha desde/hasta y búsqueda por nombre
        filt_frame = tk.Frame(header, bg=UIHelper.COLOR_PRIMARIO)
        filt_frame.pack(side="right")

        tk.Label(filt_frame, text="Desde (ISO)", bg=UIHelper.COLOR_PRIMARIO, fg=UIHelper.COLOR_TEXTO_SECUNDARIO).pack(side="left", padx=(0,4))
        ttk.Entry(filt_frame, textvariable=self.desde, width=14).pack(side="left", padx=4)

        tk.Label(filt_frame, text="Hasta (ISO)", bg=UIHelper.COLOR_PRIMARIO, fg=UIHelper.COLOR_TEXTO_SECUNDARIO).pack(side="left", padx=(6,4))
        ttk.Entry(filt_frame, textvariable=self.hasta, width=14).pack(side="left", padx=4)

        search_entry = ttk.Entry(header, textvariable=self.search_q, width=30)
        search_entry.pack(side="right", padx=(6, 0))
        search_entry.bind("<Return>", lambda e: self._on_search())

        search_btn = tk.Button(header, text="Buscar", command=self._on_search)
        UIHelper.estilizar_boton(search_btn)
        search_btn.pack(side="right", padx=6)

        nuevo_btn = tk.Button(header, text="Nueva venta", command=self._on_create)
        UIHelper.estilizar_boton(nuevo_btn, bg=UIHelper.COLOR_EXITO)
        nuevo_btn.pack(side="right", padx=6)

        import_btn = tk.Button(header, text="Importar JSON", command=self._on_import)
        UIHelper.estilizar_boton(import_btn, bg=UIHelper.COLOR_ACENTO)
        import_btn.pack(side="right", padx=6)

        sample_btn = tk.Button(header, text="Muestra aleatoria", command=self._on_sample)
        UIHelper.estilizar_boton(sample_btn)
        sample_btn.pack(side="right", padx=6)

        # Tabla
        cols = ("_id", "nombre", "total", "fecha")
        table_frame = tk.Frame(self, bg=UIHelper.COLOR_PRIMARIO)
        table_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse", height=18)
        self.tree.heading("_id", text="ID")
        self.tree.heading("nombre", text="Cliente")
        self.tree.heading("total", text="Total")
        self.tree.heading("fecha", text="Fecha")
        self.tree.column("_id", width=160, anchor="w")
        self.tree.column("nombre", width=240, anchor="w")
        self.tree.column("total", width=90, anchor="center")
        self.tree.column("fecha", width=160, anchor="w")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Footer acciones
        footer = tk.Frame(self, bg=UIHelper.COLOR_PRIMARIO)
        footer.pack(fill="x", padx=12, pady=(0,12))

        ver_btn = tk.Button(footer, text="Ver", command=self._on_view)
        UIHelper.estilizar_boton(ver_btn, bg=UIHelper.COLOR_ACENTO)
        ver_btn.pack(side="left", padx=6)

        editar_btn = tk.Button(footer, text="Editar", command=self._on_edit)
        UIHelper.estilizar_boton(editar_btn)
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

    def _load_clientes(self):
        self._set_status("Cargando clientes...")
        self._clear_table()
        try:
            q = self.search_q.get().strip()
            desde = self.desde.get().strip() or None
            hasta = self.hasta.get().strip() or None
            skip = self.current_page * self.PAGE_SIZE
            clientes = list_clientes(limit=self.PAGE_SIZE, skip=skip, desde=desde, hasta=hasta)
            if q:
                clientes = [c for c in clientes if q.lower() in c.get("nombre", "").lower()]
            for c in clientes:
                total = c.get("total", 0)
                fecha = c.get("fecha", "")
                # mostrar fecha legible si es ISO
                try:
                    fecha_disp = datetime.fromisoformat(fecha).strftime("%Y-%m-%d %H:%M")
                except Exception:
                    fecha_disp = fecha
                self.tree.insert("", "end", values=(str(c.get("_id")), c.get("nombre"), f"{total:.2f}", fecha_disp))
            count = len(clientes)
            self._set_status(f"Mostrando {count} clientes (página {self.current_page + 1})")
        except Exception as e:
            self._set_status(f"Error cargando clientes: {e}")

    def _on_search(self):
        self.current_page = 0
        self._load_clientes()

    def _on_prev(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._load_clientes()

    def _on_next(self):
        self.current_page += 1
        self._load_clientes()
        if not self.tree.get_children():
            self.current_page = max(0, self.current_page - 1)
            self._load_clientes()

    def _selected_cliente_id(self) -> Optional[str]:
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.item(sel[0])["values"][0]

    def _on_create(self):
        dlg = ClienteDialog(self.master, title="Registrar venta")
        if not dlg.result:
            return
        data = dlg.result
        try:
            cliente = create_cliente(data["nombre"], data["productos"], fecha=data.get("fecha"))
            messagebox.showinfo("Creado", f"Venta registrada: {cliente['nombre']} - Total {cliente['total']:.2f}")
            self._load_clientes()
        except ClienteError as e:
            messagebox.showerror("Error", str(e))

    def _on_view(self):
        cliente_id = self._selected_cliente_id()
        if not cliente_id:
            messagebox.showinfo("Selecciona", "Selecciona una venta para ver")
            return
        try:
            cliente = get_cliente_by_id(cliente_id)
        except ClienteError as e:
            messagebox.showerror("Error", str(e))
            return
        ViewClienteDialog(self.master, cliente)

    def _on_edit(self):
        cliente_id = self._selected_cliente_id()
        if not cliente_id:
            messagebox.showinfo("Selecciona", "Selecciona una venta para editar")
            return
        try:
            cliente = get_cliente_by_id(cliente_id)
        except ClienteError as e:
            messagebox.showerror("Error", str(e))
            return
        dlg = ClienteDialog(self.master, title="Editar venta", initial=cliente, edit=True)
        if not dlg.result:
            return
        try:
            updated = update_cliente(cliente_id, dlg.result)
            messagebox.showinfo("Actualizado", f"Venta actualizada: {updated.get('nombre')}")
            self._load_clientes()
        except ClienteNotFound as nf:
            messagebox.showerror("No encontrado", str(nf))
        except ClienteError as e:
            messagebox.showerror("Error", str(e))

    def _on_delete(self):
        cliente_id = self._selected_cliente_id()
        if not cliente_id:
            messagebox.showinfo("Selecciona", "Selecciona una venta para eliminar")
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar venta seleccionada?"):
            return
        try:
            ok = delete_cliente(cliente_id)
            if ok:
                messagebox.showinfo("Eliminado", "Venta eliminada correctamente")
                self._load_clientes()
            else:
                messagebox.showwarning("No encontrado", "La venta no existía")
        except ClienteError as e:
            messagebox.showerror("Error", str(e))

    def _on_import(self):
        path = filedialog.askopenfilename(title="Seleccionar JSON", filetypes=[("JSON", "*.json"), ("All", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                messagebox.showerror("Formato", "El JSON debe contener una lista de clientes")
                return
            res = bulk_insert_clientes(data, batch_size=1000)
            messagebox.showinfo("Importación", f"Insertados: {res.get('inserted')}  Fallidos: {res.get('failed')}")
            self._load_clientes()
        except Exception as e:
            messagebox.showerror("Error importando", str(e))

    def _on_sample(self):
        try:
            cliente = sample_cliente_random()
            ViewClienteDialog(self.master, cliente)
        except ClienteError as e:
            messagebox.showerror("Error", str(e))

class ClienteDialog(simpledialog.Dialog):
    """
    Diálogo para crear/editar venta.
    initial (opcional) acepta dict con keys: nombre, productos (list), fecha (ISO string).
    Si edit=True, permite mantener valores actuales.
    Resultado: dict con 'nombre', 'productos', optional 'fecha'
    """

    def __init__(self, parent, title=None, initial: Optional[dict] = None, edit: bool = False):
        self.initial = initial or {}
        self.edit = edit
        self.result: Optional[Dict[str, Any]] = None
        super().__init__(parent, title=title)

    def body(self, master):
        master.configure(bg=UIHelper.COLOR_PRIMARIO)
        tk.Label(master, text="Nombre cliente", bg=UIHelper.COLOR_PRIMARIO, fg=UIHelper.COLOR_TEXTO).grid(row=0, column=0, sticky="w")
        self.nombre_var = tk.StringVar(value=self.initial.get("nombre", ""))
        ttk.Entry(master, textvariable=self.nombre_var, width=40).grid(row=0, column=1, pady=6, padx=6)

        tk.Label(master, text="Productos (JSON lista)", bg=UIHelper.COLOR_PRIMARIO, fg=UIHelper.COLOR_TEXTO).grid(row=1, column=0, sticky="nw")
        self.productos_text = tk.Text(master, width=60, height=8, bg=UIHelper.COLOR_TERCIARIO, fg=UIHelper.COLOR_TEXTO)
        self.productos_text.grid(row=1, column=1, pady=6, padx=6)
        productos_init = self.initial.get("productos")
        if productos_init:
            self.productos_text.insert("1.0", json.dumps(productos_init, ensure_ascii=False, indent=2))

        tk.Label(master, text="Fecha (ISO opcional)", bg=UIHelper.COLOR_PRIMARIO, fg=UIHelper.COLOR_TEXTO).grid(row=2, column=0, sticky="w")
        self.fecha_var = tk.StringVar(value=self.initial.get("fecha", ""))
        ttk.Entry(master, textvariable=self.fecha_var, width=40).grid(row=2, column=1, pady=6, padx=6)

        return ttk.Entry(master, textvariable=self.nombre_var)

    def validate(self):
        nombre = self.nombre_var.get().strip()
        if not nombre:
            messagebox.showwarning("Validación", "El nombre del cliente es requerido")
            return False
        productos_raw = self.productos_text.get("1.0", "end").strip()
        try:
            productos = json.loads(productos_raw)
            if not isinstance(productos, list) or not productos:
                raise ValueError()
            # validación rápida de esquema
            for p in productos:
                if not all(k in p for k in ("nombre", "precio", "cantidad")):
                    raise ValueError()
        except Exception:
            messagebox.showwarning("Validación", "Productos inválidos. Debe ser JSON lista con objetos que tengan nombre, precio y cantidad")
            return False
        fecha = self.fecha_var.get().strip()
        if fecha:
            try:
                # validar formato ISO
                datetime.fromisoformat(fecha)
            except Exception:
                messagebox.showwarning("Validación", "Fecha no es un ISO válido")
                return False
        return True

    def apply(self):
        productos = json.loads(self.productos_text.get("1.0", "end").strip())
        data = {"nombre": self.nombre_var.get().strip(), "productos": productos}
        fecha = self.fecha_var.get().strip()
        if fecha:
            data["fecha"] = fecha
        self.result = data

class ViewClienteDialog(simpledialog.Dialog):
    """
    Diálogo de solo lectura para ver detalles de una venta/cliente.
    """

    def __init__(self, parent, cliente: dict):
        self.cliente = cliente
        super().__init__(parent, title=f"Venta: {cliente.get('nombre', '')}")

    def body(self, master):
        master.configure(bg=UIHelper.COLOR_PRIMARIO)
        tk.Label(master, text=f"Cliente: {self.cliente.get('nombre', '')}", bg=UIHelper.COLOR_PRIMARIO, fg=UIHelper.COLOR_TEXTO, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=10, pady=(6,0))
        tk.Label(master, text=f"Total: {self.cliente.get('total', 0):.2f}", bg=UIHelper.COLOR_PRIMARIO, fg=UIHelper.COLOR_TEXTO_SECUNDARIO).pack(anchor="w", padx=10, pady=(0,6))
        fecha = self.cliente.get("fecha", "")
        try:
            fecha_disp = datetime.fromisoformat(fecha).strftime("%Y-%m-%d %H:%M")
        except Exception:
            fecha_disp = fecha
        tk.Label(master, text=f"Fecha: {fecha_disp}", bg=UIHelper.COLOR_PRIMARIO, fg=UIHelper.COLOR_TEXTO_SECUNDARIO).pack(anchor="w", padx=10, pady=(0,6))

        frame = tk.Frame(master, bg=UIHelper.COLOR_PRIMARIO)
        frame.pack(fill="both", expand=True, padx=10, pady=6)
        txt = tk.Text(frame, width=80, height=18, bg=UIHelper.COLOR_TERCIARIO, fg=UIHelper.COLOR_TEXTO)
        txt.pack(fill="both", expand=True)
        txt.insert("1.0", json.dumps(self.cliente.get("productos", []), ensure_ascii=False, indent=2))
        txt.config(state="disabled")

    def buttonbox(self):
        box = tk.Frame(self)
        UIHelper.estilizar_boton(tk.Button(box, text="Cerrar", command=self.ok))
        tk.Button(box, text="Cerrar", command=self.ok).pack(padx=5, pady=5)
        box.pack()

# Ejemplo de arranque independiente para pruebas
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Super Pancho - Clientes")
    root.configure(bg=UIHelper.COLOR_PRIMARIO)
    root.geometry("1000x650")
    app = ClientesView(master=root)
    app.pack(fill="both", expand=True)
    root.mainloop()
