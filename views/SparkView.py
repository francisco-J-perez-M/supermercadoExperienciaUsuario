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
        
    def crear_vista(self):
        """Crear la interfaz gráfica del análisis Spark"""
        # Configurar estilo oscuro para ttk
        UIHelper.configurar_estilo_modo_oscuro()
        
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

        # Etiqueta del área de resultados
        lbl_resultados = tk.Label(result_frame, 
                                 text="Resultados del Análisis:",
                                 font=("Segoe UI", 12, "bold"),
                                 bg=UIHelper.COLOR_SECUNDARIO,
                                 fg=UIHelper.COLOR_TEXTO)
        lbl_resultados.pack(anchor="w", padx=10, pady=(10, 5))

        # Área de texto para resultados con scroll
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

        # Frame de estado
        status_frame = tk.Frame(main_frame, bg=UIHelper.COLOR_PRIMARIO)
        status_frame.pack(fill="x", pady=10)

        self.lbl_estado = tk.Label(status_frame, 
                                  text="Listo para realizar análisis",
                                  font=("Segoe UI", 10),
                                  bg=UIHelper.COLOR_PRIMARIO,
                                  fg=UIHelper.COLOR_TEXTO_SECUNDARIO)
        self.lbl_estado.pack(anchor="w")

    def limpiar_resultados(self):
        """Limpiar el área de resultados"""
        if self.resultado_area:
            self.resultado_area.delete(1.0, tk.END)
        self.actualizar_estado("Área de resultados limpiada")

    def mostrar_resultados(self, texto):
        """Mostrar resultados en el área de texto"""
        if self.resultado_area:
            self.resultado_area.delete(1.0, tk.END)
            self.resultado_area.insert(tk.END, texto)
            # Mover el cursor al inicio
            self.resultado_area.see(1.0)
        self.actualizar_estado("Resultados mostrados")

    def obtener_resultados(self):
        """Obtener el texto actual del área de resultados"""
        if self.resultado_area:
            return self.resultado_area.get(1.0, tk.END)
        return ""

    def deshabilitar_botones(self):
        """Deshabilitar botones durante el análisis"""
        if self.btn_test:
            self.btn_test.config(state="disabled")
        if self.btn_analizar:
            self.btn_analizar.config(state="disabled")
        if self.btn_exportar:
            self.btn_exportar.config(state="disabled")
        self.actualizar_estado("Procesando...")

    def habilitar_botones(self):
        """Habilitar botones después del análisis"""
        if self.btn_test:
            self.btn_test.config(state="normal")
        if self.btn_analizar:
            self.btn_analizar.config(state="normal")
        if self.btn_exportar:
            self.btn_exportar.config(state="normal")
        self.actualizar_estado("Análisis completado")

    def mostrar_progreso(self, mensaje):
        """Mostrar mensaje de progreso"""
        self.limpiar_resultados()
        if self.resultado_area:
            self.resultado_area.insert(tk.END, f"⏳ {mensaje}\n\nPor favor espere...")
        self.actualizar_estado(mensaje)

    def actualizar_estado(self, mensaje):
        """Actualizar la barra de estado"""
        if hasattr(self, 'lbl_estado'):
            self.lbl_estado.config(text=f"Estado: {mensaje}")

    def mostrar_error(self, mensaje):
        """Mostrar mensaje de error"""
        if self.resultado_area:
            self.resultado_area.delete(1.0, tk.END)
            self.resultado_area.insert(tk.END, f"❌ ERROR: {mensaje}")
        self.actualizar_estado(f"Error: {mensaje}")

    def mostrar_exito(self, mensaje):
        """Mostrar mensaje de éxito"""
        if self.resultado_area:
            self.resultado_area.insert(tk.END, f"\n\n✅ {mensaje}")
        self.actualizar_estado(mensaje)