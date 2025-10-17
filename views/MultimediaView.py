import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import io
import os
import tempfile
import cv2
from ui_helper import UIHelper


class MultimediaView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        
        self.imagen_label = None
        self.lista_archivos = None
        self.tipo_seleccionado = tk.StringVar(value="imagen")

    def crear_vista(self):
        """Crea la interfaz gráfica"""
        UIHelper.configurar_estilo_ttk()

        self.root.config(bg=UIHelper.COLOR_PRIMARIO)
        # Título
        titulo = tk.Label(self.root, text="🎨 Visualizador de Imágenes y Videos",
                          font=("Segoe UI", 18, "bold"),
                          bg=UIHelper.COLOR_PRIMARIO,
                          fg=UIHelper.COLOR_TEXTO)
        titulo.pack(pady=10)

        # Frame principal
        frame_principal = tk.Frame(self.root, bg=UIHelper.COLOR_PRIMARIO)
        frame_principal.pack(fill="both", expand=True, padx=20, pady=10)

        # Panel izquierdo - lista de archivos
        frame_izq = tk.Frame(frame_principal, bg=UIHelper.COLOR_SECUNDARIO, bd=1, relief="solid")
        frame_izq.pack(side="left", fill="y", padx=10, pady=5)

        lbl_tipo = tk.Label(frame_izq, text="Tipo de archivo:",
                            bg=UIHelper.COLOR_SECUNDARIO,
                            fg=UIHelper.COLOR_TEXTO,
                            font=("Segoe UI", 11, "bold"))
        lbl_tipo.pack(pady=(10, 0))

        # Combobox para tipo de archivo
        combo_tipo = ttk.Combobox(frame_izq, textvariable=self.tipo_seleccionado, state="readonly")
        combo_tipo["values"] = ("imagen", "foto", "video")
        combo_tipo.current(0)
        combo_tipo.pack(padx=10, pady=5, fill="x")
        combo_tipo.bind("<<ComboboxSelected>>", self.controller.actualizar_lista_archivos)

        lbl_lista = tk.Label(frame_izq, text="Archivos disponibles:",
                             bg=UIHelper.COLOR_SECUNDARIO,
                             fg=UIHelper.COLOR_TEXTO,
                             font=("Segoe UI", 11))
        lbl_lista.pack(anchor="w", padx=10, pady=(10, 0))

        # Lista de archivos
        frame_lista = tk.Frame(frame_izq, bg=UIHelper.COLOR_SECUNDARIO)
        frame_lista.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(frame_lista)
        scrollbar.pack(side="right", fill="y")

        self.lista_archivos = tk.Listbox(frame_lista,
                                         yscrollcommand=scrollbar.set,
                                         bg=UIHelper.COLOR_TERCIARIO,
                                         fg=UIHelper.COLOR_TEXTO,
                                         selectbackground=UIHelper.COLOR_ACENTO,
                                         relief="flat",
                                         bd=0,
                                         font=("Consolas", 10))
        self.lista_archivos.pack(fill="both", expand=True)
        self.lista_archivos.bind("<Double-1>", self.controller.ver_archivo)

        scrollbar.config(command=self.lista_archivos.yview)

        # Panel derecho - vista previa
        frame_der = tk.Frame(frame_principal, bg=UIHelper.COLOR_SECUNDARIO, bd=1, relief="solid")
        frame_der.pack(side="right", fill="both", expand=True, padx=10, pady=5)

        lbl_preview = tk.Label(frame_der, text="Vista previa:",
                               bg=UIHelper.COLOR_SECUNDARIO,
                               fg=UIHelper.COLOR_TEXTO,
                               font=("Segoe UI", 12, "bold"))
        lbl_preview.pack(anchor="w", padx=10, pady=(10, 5))

        self.imagen_label = tk.Label(frame_der, bg=UIHelper.COLOR_TERCIARIO)
        self.imagen_label.pack(fill="both", expand=True, padx=20, pady=10)

        # Botón de recarga
        btn_recargar = tk.Button(self.root, text="🔄 Recargar lista", 
                               command=self.controller.actualizar_lista_archivos)
        UIHelper.estilizar_boton(btn_recargar, bg=UIHelper.COLOR_ACENTO)
        btn_recargar.pack(pady=10)

        # Cargar lista inicial
        self.controller.actualizar_lista_archivos()

    # ----------------------------------------------------------
    # Métodos de actualización de vista
    # ----------------------------------------------------------

    def actualizar_lista_ui(self, archivos):
        """Actualiza la lista de archivos en la interfaz"""
        self.lista_archivos.delete(0, tk.END)
        for archivo in archivos:
            self.lista_archivos.insert(tk.END, archivo)

    def mostrar_imagen(self, imagen_tk):
        """Muestra una imagen en el label"""
        self.imagen_label.config(image=imagen_tk)
        self.imagen_label.image = imagen_tk

    def limpiar_vista_previa(self):
        """Limpia la vista previa"""
        self.imagen_label.config(image='')
        self.imagen_label.image = None

    def obtener_tipo_seleccionado(self):
        """Retorna el tipo de archivo seleccionado"""
        return self.tipo_seleccionado.get()

    def obtener_archivo_seleccionado(self):
        """Retorna el archivo seleccionado en la lista"""
        seleccion = self.lista_archivos.curselection()
        if seleccion:
            return self.lista_archivos.get(seleccion[0])
        return None

    def mostrar_error(self, titulo, mensaje):
        """Muestra un mensaje de error"""
        messagebox.showerror(titulo, mensaje)

    def mostrar_advertencia(self, titulo, mensaje):
        """Muestra un mensaje de advertencia"""
        messagebox.showwarning(titulo, mensaje)