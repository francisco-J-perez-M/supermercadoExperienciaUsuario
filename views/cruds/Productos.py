# Productos.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional
from ui_helper import UIHelper
from controllers.ProductosController import (
    create_producto,
    get_producto_by_id,
    get_producto_by_name,
    list_productos,
    update_producto,
    delete_producto,
    ProductoError,
    ProductoExists,
    ProductoNotFound,
    ensure_indexes,
)
import threading

class ProductosView(tk.Frame):
    """
    Vista CRUD para productos usando UIHelper para estilo.
    Integrar en la ventana principal: ProductosView(root).pack(fill='both', expand=True)
    """

    PAGE_SIZE = 30

    def __init__(self, master=None):
        super().__init__(master, bg=UIHelper.COLOR_PRIMARIO)
        UIHelper.configurar_estilo_ttk()
        self.master = master
        self.current_page = 0
        self.search_q = tk.StringVar()
        self.filter_area = tk.StringVar(value="")
        self.min_price = tk.StringVar(value="")
        self.max_price = tk.StringVar(value="")
        self._build_ui()
        threading.Thread(target=ensure_indexes, daemon=True).start()
        self._load_productos()

    def _build_ui(self):
        header = tk.Frame(self, bg=UIHelper.COLOR_PRIMARIO)
        header.pack(fill="x", padx=12, pady=12)

        title = tk.Label(header, text="Productos", fg=UIHelper.COLOR_TEXTO,
                         bg=UIHelper.COLOR_PRIMARIO, font=("Segoe UI", 16, "bold"))
        title.pack(side="left")

        # Filtros rápidos
        filt_frame = tk.Frame(header, bg=UIHelper.COLOR_PRIMARIO)
        filt_frame.pack(side="right")

        tk.Entry(filt_frame, textvariable=self.min_price, width=7).pack(side="right", padx=4)
        tk.Label(filt_frame, text="Min", bg=UIHelper.COLOR_PRIMARIO, fg=UIHelper.COLOR_TEXTO_SECUNDARIO).pack(side="right")

        tk.Entry(filt_frame, textvariable=self.max_price, width=7).pack(side="right", padx=4)
        tk.Label(filt_frame, text="Max", bg=UIHelper.COLOR_PRIMARIO, fg=UIHelper.COLOR_TEXTO_SECUNDARIO).pack(side="right")

        area_entry = ttk.Entry(filt_frame, textvariable=self.filter_area, width=12)
        area_entry.pack(side="right", padx=6)
        tk.Label(filt_frame, text="Area id", bg=UIHelper.COLOR_PRIMARIO, fg=UIHelper.COLOR_TEXTO_SECUNDARIO).pack(side="right")

        search_entry = ttk.Entry(header, textvariable=self.search_q, width=30)
        search_entry.pack(side="right", padx=(6, 0))
        search_entry.bind("<Return>", lambda e: self._on_search())

        search_btn = tk.Button(header, text="Buscar", command=self._on_search)
        UIHelper.estilizar_boton(search_btn)
        search_btn.pack(side="right", padx=6)

        nuevo_btn = tk.Button(header, text="Nuevo producto", command=self._on_create)
        UIHelper.estilizar_boton(nuevo_btn, bg=UIHelper.COLOR_EXITO)
        nuevo_btn.pack(side="right", padx=6)

        # Tabla
        cols = ("_id", "nombre", "precio", "area_id")
        table_frame = tk.Frame(self, bg=UIHelper.COLOR_PRIMARIO)
        table_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse", height=18)
        self.tree.heading("_id", text="ID")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("precio", text="Precio")
        self.tree.heading("area_id", text="Area")
        self.tree.column("_id", width=160, anchor="w")
        self.tree.column("nombre", width=240, anchor="w")
        self.tree.column("precio", width=90, anchor="center")
        self.tree.column("area_id", width=80, anchor="center")

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

    def _load_productos(self):
        self._set_status("Cargando productos...")
        self._clear_table()
        try:
            q = self.search_q.get().strip()
            area = self.filter_area.get().strip()
            min_p = self.min_price.get().strip()
            max_p = self.max_price.get().strip()
            skip = self.current_page * self.PAGE_SIZE

            # Preparar filtros para controller
            area_id = int(area) if area.isdigit() else None
            productos = list_productos(limit=self.PAGE_SIZE, skip=skip, area_id=area_id, q=q or None)
            # Filtrado adicional por precio si se especifica
            if min_p:
                try:
                    min_v = float(min_p)
                    productos = [p for p in productos if float(p.get("precio", 0)) >= min_v]
                except ValueError:
                    pass
            if max_p:
                try:
                    max_v = float(max_p)
                    productos = [p for p in productos if float(p.get("precio", 0)) <= max_v]
                except ValueError:
                    pass

            for p in productos:
                self.tree.insert("", "end", values=(str(p.get("_id")), p.get("nombre"), p.get("precio"), p.get("area_id")))
            count = len(productos)
            self._set_status(f"Mostrando {count} productos (página {self.current_page + 1})")
        except Exception as e:
            self._set_status(f"Error cargando productos: {e}")

    def _on_search(self):
        self.current_page = 0
        self._load_productos()

    def _on_prev(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._load_productos()

    def _on_next(self):
        self.current_page += 1
        self._load_productos()
        if not self.tree.get_children():
            self.current_page = max(0, self.current_page - 1)
            self._load_productos()

    def _selected_producto_id(self) -> Optional[str]:
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.item(sel[0])["values"][0]

    def _on_create(self):
        dlg = ProductoDialog(self.master, title="Crear producto")
        if not dlg.result:
            return
        data = dlg.result
        try:
            prod = create_producto(data["nombre"], float(data["precio"]), int(data["area_id"]))
            messagebox.showinfo("Creado", f"Producto '{prod['nombre']}' creado correctamente")
            self._load_productos()
        except ProductoExists as pe:
            messagebox.showwarning("Existe", str(pe))
        except ProductoError as e:
            messagebox.showerror("Error", str(e))

    def _on_edit(self):
        producto_id = self._selected_producto_id()
        if not producto_id:
            messagebox.showinfo("Selecciona", "Selecciona un producto para editar")
            return
        try:
            producto = get_producto_by_id(producto_id)
        except ProductoError as e:
            messagebox.showerror("Error", str(e))
            return

        dlg = ProductoDialog(self.master, title="Editar producto", initial=producto, edit=True)
        if not dlg.result:
            return
        updates = dlg.result
        try:
            updated = update_producto(producto_id, updates)
            messagebox.showinfo("Actualizado", f"Producto '{updated['nombre']}' actualizado")
            self._load_productos()
        except ProductoNotFound as nf:
            messagebox.showerror("No encontrado", str(nf))
        except ProductoExists as pe:
            messagebox.showwarning("Existe", str(pe))
        except ProductoError as e:
            messagebox.showerror("Error", str(e))

    def _on_delete(self):
        producto_id = self._selected_producto_id()
        if not producto_id:
            messagebox.showinfo("Selecciona", "Selecciona un producto para eliminar")
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar producto seleccionado?"):
            return
        try:
            ok = delete_producto(producto_id)
            if ok:
                messagebox.showinfo("Eliminado", "Producto eliminado correctamente")
                self._load_productos()
            else:
                messagebox.showwarning("No encontrado", "El producto no existía")
        except ProductoError as e:
            messagebox.showerror("Error", str(e))

class ProductoDialog(simpledialog.Dialog):
    """
    Diálogo para crear/editar producto.
    Resultado: dict con 'nombre', 'precio', 'area_id' y posibles campos extra
    """

    def __init__(self, parent, title=None, initial: Optional[dict] = None, edit: bool = False):
        self.initial = initial or {}
        self.edit = edit
        self.result = None
        super().__init__(parent, title=title)

    def body(self, master):
        master.configure(bg=UIHelper.COLOR_PRIMARIO)
        tk.Label(master, text="Nombre", bg=UIHelper.COLOR_PRIMARIO, fg=UIHelper.COLOR_TEXTO).grid(row=0, column=0, sticky="w")
        self.nombre_var = tk.StringVar(value=self.initial.get("nombre", ""))
        ttk.Entry(master, textvariable=self.nombre_var, width=40).grid(row=0, column=1, pady=6, padx=6)

        tk.Label(master, text="Precio", bg=UIHelper.COLOR_PRIMARIO, fg=UIHelper.COLOR_TEXTO).grid(row=1, column=0, sticky="w")
        self.precio_var = tk.StringVar(value=str(self.initial.get("precio", "")))
        ttk.Entry(master, textvariable=self.precio_var).grid(row=1, column=1, pady=6, padx=6)

        tk.Label(master, text="Area id", bg=UIHelper.COLOR_PRIMARIO, fg=UIHelper.COLOR_TEXTO).grid(row=2, column=0, sticky="w")
        self.area_var = tk.StringVar(value=str(self.initial.get("area_id", "")))
        ttk.Entry(master, textvariable=self.area_var).grid(row=2, column=1, pady=6, padx=6)

        return ttk.Entry(master, textvariable=self.nombre_var)

    def validate(self):
        nombre = self.nombre_var.get().strip()
        precio = self.precio_var.get().strip()
        area = self.area_var.get().strip()
        if not nombre:
            messagebox.showwarning("Validación", "El nombre es requerido")
            return False
        try:
            p = float(precio)
            if p < 0:
                raise ValueError()
        except Exception:
            messagebox.showwarning("Validación", "Precio inválido")
            return False
        if not area.isdigit():
            messagebox.showwarning("Validación", "Area id debe ser entero")
            return False
        return True

    def apply(self):
        data = {"nombre": self.nombre_var.get().strip(), "precio": float(self.precio_var.get()), "area_id": int(self.area_var.get())}
        self.result = data

# Ejemplo de arranque independiente para pruebas
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Super Pancho - Productos")
    root.configure(bg=UIHelper.COLOR_PRIMARIO)
    root.geometry("950x600")
    app = ProductosView(master=root)
    app.pack(fill="both", expand=True)
    root.mainloop()
