import tkinter as tk
from tkinter import ttk
from ui_helper import UIHelper

class PuntoVentaView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.combo_area = None
        self.lista_productos = None
        self.texto_cuenta = None
        self.btn_resumen = None

    def crear_vista_principal(self):
        # Configurar estilo oscuro para ttk
        UIHelper.configurar_estilo_ttk()
        
        self.root.title("Supermercado - Punto de Venta")
        self.root.geometry("900x550")
        self.root.config(bg=UIHelper.COLOR_PRIMARIO)

        titulo = tk.Label(self.root, text="🛒 Punto de Venta", 
                         font=("Segoe UI", 18, "bold"), 
                         bg=UIHelper.COLOR_PRIMARIO, 
                         fg=UIHelper.COLOR_TEXTO)
        titulo.pack(pady=10)

        frame_principal = tk.Frame(self.root, bg=UIHelper.COLOR_PRIMARIO)
        frame_principal.pack(fill="both", expand=True, padx=20, pady=10)

        # Frame izquierdo
        frame_izq = tk.Frame(frame_principal, bg=UIHelper.COLOR_SECUNDARIO, bd=1, relief="solid")
        frame_izq.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        lbl_area = tk.Label(frame_izq, text="Seleccionar área:", 
                           font=("Segoe UI", 12, "bold"), 
                           bg=UIHelper.COLOR_SECUNDARIO, 
                           fg=UIHelper.COLOR_TEXTO)
        lbl_area.pack(anchor="w", padx=10, pady=(10, 0))

        self.combo_area = ttk.Combobox(frame_izq, state="readonly")
        self.combo_area.pack(fill="x", padx=10, pady=5)
        self.combo_area.bind("<<ComboboxSelected>>", self.controller.on_area_selected)

        lbl_productos = tk.Label(frame_izq, text="Productos del área:", 
                                font=("Segoe UI", 12), 
                                bg=UIHelper.COLOR_SECUNDARIO, 
                                fg=UIHelper.COLOR_TEXTO)
        lbl_productos.pack(anchor="w", padx=10, pady=(10, 0))

        frame_lista = tk.Frame(frame_izq, bg=UIHelper.COLOR_SECUNDARIO)
        frame_lista.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(frame_lista)
        scrollbar.pack(side="right", fill="y")

        self.lista_productos = tk.Listbox(frame_lista, 
                                         yscrollcommand=scrollbar.set, 
                                         height=10, 
                                         font=("Segoe UI", 10),
                                         bg=UIHelper.COLOR_TERCIARIO,
                                         fg=UIHelper.COLOR_TEXTO,
                                         selectbackground=UIHelper.COLOR_ACENTO,
                                         relief="flat",
                                         bd=0)
        self.lista_productos.pack(fill="both", expand=True)
        self.lista_productos.bind("<Double-Button-1>", self.controller.on_producto_selected)

        scrollbar.config(command=self.lista_productos.yview)

        # Frame derecho
        frame_der = tk.Frame(frame_principal, bg=UIHelper.COLOR_SECUNDARIO, bd=1, relief="solid")
        frame_der.pack(side="right", fill="both", expand=True, padx=10, pady=5)

        lbl_cuenta = tk.Label(frame_der, text="Cuenta en tiempo real:", 
                             font=("Segoe UI", 12, "bold"), 
                             bg=UIHelper.COLOR_SECUNDARIO, 
                             fg=UIHelper.COLOR_TEXTO)
        lbl_cuenta.pack(anchor="w", padx=10, pady=10)

        self.texto_cuenta = tk.Text(frame_der, 
                                   height=12, 
                                   state="disabled", 
                                   bg=UIHelper.COLOR_TERCIARIO,
                                   fg=UIHelper.COLOR_TEXTO,
                                   font=("Consolas", 10),
                                   relief="flat",
                                   bd=0,
                                   padx=10,
                                   pady=10)
        self.texto_cuenta.pack(fill="both", expand=True, padx=10, pady=5)

        # Botones
        frame_botones = tk.Frame(self.root, bg=UIHelper.COLOR_PRIMARIO)
        frame_botones.pack(pady=10)

        btn_atender = tk.Button(frame_botones, text="✅ Atender Cliente", width=20, command=self.controller.atender_cliente)
        UIHelper.estilizar_boton(btn_atender, bg=UIHelper.COLOR_EXITO, hover="#0e6b0e")
        btn_atender.pack(side="left", padx=10)

        self.btn_resumen = tk.Button(frame_botones, text="📑 Resumen Diario", width=20, command=self.controller.mostrar_resumen)
        UIHelper.estilizar_boton(self.btn_resumen)
        self.btn_resumen.pack(side="right", padx=10)

    def actualizar_combo_areas(self, nombres_areas):
        self.combo_area['values'] = nombres_areas
        if nombres_areas:
            self.combo_area.current(0)

    def actualizar_lista_productos(self, productos):
        self.lista_productos.delete(0, tk.END)
        for producto in productos:
            self.lista_productos.insert(tk.END, f"{producto['nombre']} - ${producto['precio']:.2f}")

    def actualizar_cuenta(self, cuenta_actual, total_actual):
        self.texto_cuenta.config(state="normal")
        self.texto_cuenta.delete(1.0, tk.END)

        for producto_id, datos in cuenta_actual.items():
            self.texto_cuenta.insert(tk.END, f"{datos['nombre']} x{datos['cantidad']} - ${datos['precio'] * datos['cantidad']:.2f}\n")

        self.texto_cuenta.insert(tk.END, f"\nTotal: ${total_actual:.2f}")
        self.texto_cuenta.config(state="disabled")