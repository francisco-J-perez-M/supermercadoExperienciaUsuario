import tkinter as tk
from tkinter import ttk, scrolledtext
from ui_helper import UIHelper

class SparkView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.resultado_area = None
        self.btn_test = None
        self.btn_analizar = None
        self.btn_exportar = None
        self.progress_bar = None
        self.lbl_estado = None
        self.lbl_progreso_detalle = None  # Nueva etiqueta para mostrar el paso actual
        self.lbl_porcentaje = None  # Nueva etiqueta para mostrar porcentaje

    def crear_vista(self):
        """Crear la interfaz gráfica del análisis Spark"""
        UIHelper.configurar_estilo_ttk()

        self.root.title("Análisis Completo de Supermercado")
        self.root.geometry("1000x800")
        self.root.config(bg=UIHelper.COLOR_PRIMARIO)

        # Frame principal
        main_frame = tk.Frame(self.root, bg=UIHelper.COLOR_PRIMARIO, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # Título
        titulo = tk.Label(main_frame,
                          text="🔍 Análisis de Datos con Spark",
                          font=("Segoe UI", 18, "bold"),
                          bg=UIHelper.COLOR_PRIMARIO,
                          fg=UIHelper.COLOR_TEXTO)
        titulo.pack(pady=(0, 20))

        # Frame para botones
        btn_frame = tk.Frame(main_frame, bg=UIHelper.COLOR_PRIMARIO)
        btn_frame.pack(pady=(0, 20), fill="x")

        # Botón de análisis
        self.btn_analizar = tk.Button(btn_frame,
                                      text="📊 Realizar Análisis Completo",
                                      command=self.controller.realizar_analisis,
                                      width=20)
        UIHelper.estilizar_boton(self.btn_analizar, bg=UIHelper.COLOR_EXITO, hover="#0e6b0e")
        self.btn_analizar.pack(side="left", padx=5)

        # Botón de exportación
        self.btn_exportar = tk.Button(btn_frame,
                                      text="💾 Exportar Resultados",
                                      command=self.controller.exportar_resultados,
                                      width=20)
        UIHelper.estilizar_boton(self.btn_exportar, bg=UIHelper.COLOR_ACENTO, hover="#2980b9")
        self.btn_exportar.pack(side="left", padx=5)

        # Frame para el área de resultados
        result_frame = tk.Frame(main_frame, bg=UIHelper.COLOR_SECUNDARIO, bd=1, relief="solid")
        result_frame.pack(fill="both", expand=True, pady=10)

        lbl_resultados = tk.Label(result_frame,
                                  text="Resultados del Análisis:",
                                  font=("Segoe UI", 12, "bold"),
                                  bg=UIHelper.COLOR_SECUNDARIO,
                                  fg=UIHelper.COLOR_TEXTO)
        lbl_resultados.pack(anchor="w", padx=10, pady=(10, 5))

        self.resultado_area = scrolledtext.ScrolledText(
            result_frame,
            width=120,
            height=35,
            font=("Consolas", 10),
            bg=UIHelper.COLOR_TERCIARIO,
            fg=UIHelper.COLOR_TEXTO,
            insertbackground=UIHelper.COLOR_TEXTO,
            relief="flat",
            padx=10,
            pady=10
        )
        self.resultado_area.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Frame de estado con barra de progreso mejorada
        status_frame = tk.Frame(main_frame, bg=UIHelper.COLOR_PRIMARIO)
        status_frame.pack(fill="x", pady=10)

        # Etiqueta de estado principal
        self.lbl_estado = tk.Label(status_frame,
                                   text="Listo para realizar análisis",
                                   font=("Segoe UI", 10),
                                   bg=UIHelper.COLOR_PRIMARIO,
                                   fg=UIHelper.COLOR_TEXTO_SECUNDARIO)
        self.lbl_estado.pack(anchor="w", side="top", fill="x")

        # Frame para detalles de progreso
        progress_detail_frame = tk.Frame(status_frame, bg=UIHelper.COLOR_PRIMARIO)
        progress_detail_frame.pack(fill="x", pady=(5, 0))

        # Etiqueta de paso actual
        self.lbl_progreso_detalle = tk.Label(progress_detail_frame,
                                             text="",
                                             font=("Segoe UI", 9),
                                             bg=UIHelper.COLOR_PRIMARIO,
                                             fg=UIHelper.COLOR_TEXTO_SECUNDARIO)
        self.lbl_progreso_detalle.pack(anchor="w", side="left")

        # Etiqueta de porcentaje
        self.lbl_porcentaje = tk.Label(progress_detail_frame,
                                       text="0%",
                                       font=("Segoe UI", 9, "bold"),
                                       bg=UIHelper.COLOR_PRIMARIO,
                                       fg=UIHelper.COLOR_EXITO)
        self.lbl_porcentaje.pack(anchor="e", side="right")

        # Frame para barra de progreso
        progress_bar_frame = tk.Frame(status_frame, bg=UIHelper.COLOR_PRIMARIO)
        progress_bar_frame.pack(fill="x", pady=(5, 0))

        # Barra de progreso
        self.progress_bar = ttk.Progressbar(progress_bar_frame, 
                                           mode="determinate", 
                                           length=400,
                                           maximum=100)
        self.progress_bar.pack(fill="x", side="left", expand=True)
        self.progress_bar["value"] = 0

    # ----------------------
    # Métodos de soporte UI MEJORADOS
    # ----------------------
    def iniciar_progreso(self, max_pasos=7, mensaje="Iniciando análisis..."):
        """Iniciar barra de progreso"""
        if self.progress_bar:
            self.progress_bar["maximum"] = 100  # Siempre 100% para porcentaje
            self.progress_bar["value"] = 0
            self.actualizar_estado(mensaje)
            self.actualizar_detalle_progreso("Preparando...")
            self.actualizar_porcentaje(0)
            self.progress_bar.update()

    def avanzar_progreso(self, paso_actual, total_pasos, mensaje_detalle=""):
        """Avanzar un paso con información detallada"""
        if self.progress_bar:
            porcentaje = (paso_actual / total_pasos) * 100
            self.progress_bar["value"] = porcentaje
            self.actualizar_porcentaje(porcentaje)
            if mensaje_detalle:
                self.actualizar_detalle_progreso(mensaje_detalle)
            self.progress_bar.update()

    def actualizar_detalle_progreso(self, mensaje):
        """Actualizar el mensaje detallado del progreso"""
        if self.lbl_progreso_detalle:
            self.lbl_progreso_detalle.config(text=f"Paso actual: {mensaje}")

    def actualizar_porcentaje(self, porcentaje):
        """Actualizar el porcentaje mostrado"""
        if self.lbl_porcentaje:
            self.lbl_porcentaje.config(text=f"{porcentaje:.1f}%")

    def finalizar_progreso(self, mensaje="Análisis completado"):
        """Completar barra de progreso"""
        if self.progress_bar:
            self.progress_bar["value"] = 100
            self.actualizar_porcentaje(100)
            self.actualizar_detalle_progreso("Completado")
            self.actualizar_estado(mensaje)
            self.progress_bar.update()

    def limpiar_resultados(self):
        if self.resultado_area:
            self.resultado_area.delete(1.0, tk.END)
        self.actualizar_estado("Área de resultados limpiada")

    def mostrar_resultados(self, texto):
        if self.resultado_area:
            self.resultado_area.delete(1.0, tk.END)
            self.resultado_area.insert(tk.END, texto)
            self.resultado_area.see(1.0)
        self.actualizar_estado("Resultados mostrados")

    def obtener_resultados(self):
        if self.resultado_area:
            return self.resultado_area.get(1.0, tk.END)
        return ""

    def deshabilitar_botones(self):
        if self.btn_test:
            self.btn_test.config(state="disabled")
        if self.btn_analizar:
            self.btn_analizar.config(state="disabled")
        if self.btn_exportar:
            self.btn_exportar.config(state="disabled")
        self.actualizar_estado("Procesando...")

    def habilitar_botones(self):
        if self.btn_test:
            self.btn_test.config(state="normal")
        if self.btn_analizar:
            self.btn_analizar.config(state="normal")
        if self.btn_exportar:
            self.btn_exportar.config(state="normal")
        self.actualizar_estado("Análisis completado")

    def mostrar_progreso(self, mensaje):
        self.limpiar_resultados()
        if self.resultado_area:
            self.resultado_area.insert(tk.END, f"⏳ {mensaje}\n\nPor favor espere...")
        self.actualizar_estado(mensaje)

    def actualizar_estado(self, mensaje):
        if self.lbl_estado:
            self.lbl_estado.config(text=f"Estado: {mensaje}")

    def mostrar_error(self, mensaje):
        if self.resultado_area:
            self.resultado_area.delete(1.0, tk.END)
            self.resultado_area.insert(tk.END, f"❌ ERROR: {mensaje}")
        self.actualizar_estado(f"Error: {mensaje}")
        # Resetear barra de progreso en caso de error
        if self.progress_bar:
            self.progress_bar["value"] = 0
            self.actualizar_porcentaje(0)
            self.actualizar_detalle_progreso("Error - Proceso interrumpido")

    def mostrar_exito(self, mensaje):
        if self.resultado_area:
            self.resultado_area.insert(tk.END, f"\n\n✅ {mensaje}")
        self.actualizar_estado(mensaje)