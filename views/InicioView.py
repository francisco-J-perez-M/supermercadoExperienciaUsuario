import tkinter as tk
from ui_helper import UIHelper

class InicioView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.menu_frame = None
        self.content_frame = None

    def crear_vista_principal(self, usuario, rol):
        self.root.title("Terminal - Supermercado")
        self.root.geometry("900x550")
        self.root.config(bg=UIHelper.COLOR_PRIMARIO)

        # Frame lateral (menú)
        self.menu_frame = tk.Frame(self.root, bg=UIHelper.COLOR_SECUNDARIO, width=200)
        self.menu_frame.pack(side="left", fill="y")

        # Frame principal (contenido)
        self.content_frame = tk.Frame(self.root, bg=UIHelper.COLOR_PRIMARIO)
        self.content_frame.pack(side="right", expand=True, fill="both")

        self._crear_menu_lateral(usuario, rol)
        self.mostrar_inicio()

    def _crear_menu_lateral(self, usuario, rol):
        lbl_usuario = tk.Label(self.menu_frame, 
                              text=f"👤 {usuario}\nRol: {rol}",
                              bg=UIHelper.COLOR_SECUNDARIO, 
                              fg=UIHelper.COLOR_TEXTO, 
                              font=("Segoe UI", 11, "bold"), 
                              justify="left")
        lbl_usuario.pack(pady=15, anchor="w", padx=10)

        opciones = [
            ("🏠 Inicio", self.controller.mostrar_inicio),
            ("📦 Punto de venta", self.controller.mostrar_punto_venta),
            ("📂 Análisis Spark", self.controller.mostrar_analisis_spark),
        ]

        for texto, comando in opciones:
            btn = tk.Button(self.menu_frame, text=texto, command=comando, anchor="w")
            UIHelper.estilizar_boton(btn, bg=UIHelper.COLOR_TERCIARIO, hover=UIHelper.COLOR_ACENTO)
            btn.pack(fill="x", pady=5, padx=10)

        btn_cerrar = tk.Button(self.menu_frame, text="⏻  Cerrar Sesión",
                              command=self.controller.cerrar_sesion)
        UIHelper.estilizar_boton(btn_cerrar, bg=UIHelper.COLOR_PELIGRO, hover="#b02a30")
        btn_cerrar.pack(side="bottom", pady=20, padx=10, fill="x")

    def limpiar_contenido(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def mostrar_inicio(self):
        self.limpiar_contenido()
        lbl_titulo = tk.Label(self.content_frame, 
                             text="Bienvenido al Sistema de Gestión",
                             font=("Segoe UI", 18, "bold"), 
                             bg=UIHelper.COLOR_PRIMARIO, 
                             fg=UIHelper.COLOR_TEXTO)
        lbl_titulo.pack(pady=20)

        info_frame = tk.Frame(self.content_frame, bg=UIHelper.COLOR_PRIMARIO)
        info_frame.pack(pady=10)

        lbl_info = tk.Label(info_frame, 
                           text="Como administrador tienes acceso a:",
                           font=("Segoe UI", 12), 
                           bg=UIHelper.COLOR_PRIMARIO, 
                           fg=UIHelper.COLOR_TEXTO_SECUNDARIO)
        lbl_info.pack(pady=10)

        funciones = [
            "• Punto de venta",
            "• Análisis de datos con Spark",
        ]

        for funcion in funciones:
            lbl_funcion = tk.Label(info_frame, 
                                  text=funcion,
                                  font=("Segoe UI", 10), 
                                  bg=UIHelper.COLOR_PRIMARIO, 
                                  fg=UIHelper.COLOR_TEXTO_SECUNDARIO)
            lbl_funcion.pack(anchor="w", pady=2)