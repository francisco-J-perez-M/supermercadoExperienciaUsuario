import tkinter as tk
from tkinter import ttk

class UIHelper:
    # Colores para modo oscuro
    COLOR_PRIMARIO = "#1e1e1e"
    COLOR_SECUNDARIO = "#2d2d30"
    COLOR_TERCIARIO = "#3e3e42"
    COLOR_TEXTO = "#ffffff"
    COLOR_TEXTO_SECUNDARIO = "#cccccc"
    COLOR_ACENTO = "#007acc"
    COLOR_ACENTO_HOVER = "#005a9e"
    COLOR_EXITO = "#107c10"
    COLOR_PELIGRO = "#d13438"
    
    @staticmethod
    def configurar_estilo_modo_oscuro():
        """Configura el estilo para modo oscuro en ttk widgets"""
        estilo = ttk.Style()
        estilo.theme_use('clam')
        
        # Configurar colores para ttk widgets
        estilo.configure("TCombobox", 
                        fieldbackground=UIHelper.COLOR_TERCIARIO,
                        background=UIHelper.COLOR_TERCIARIO,
                        foreground=UIHelper.COLOR_TEXTO,
                        selectbackground=UIHelper.COLOR_ACENTO)
        
        estilo.configure("TScrollbar", 
                        background=UIHelper.COLOR_TERCIARIO,
                        troughcolor=UIHelper.COLOR_SECUNDARIO,
                        bordercolor=UIHelper.COLOR_PRIMARIO)
        
        estilo.map('TCombobox', 
                  fieldbackground=[('readonly', UIHelper.COLOR_TERCIARIO)],
                  selectbackground=[('readonly', UIHelper.COLOR_ACENTO)])

    @staticmethod
    def estilizar_boton(boton, bg=None, fg=None, hover=None):
        """Estiliza un botón de tkinter con colores del modo oscuro"""
        bg_color = bg or UIHelper.COLOR_ACENTO
        fg_color = fg or UIHelper.COLOR_TEXTO
        hover_color = hover or UIHelper.COLOR_ACENTO_HOVER
        
        boton.config(
            bg=bg_color,
            fg=fg_color,
            font=("Segoe UI", 10),
            relief="flat",
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2"
        )
        
        # Efectos hover
        def on_enter(e):
            boton.config(bg=hover_color)
        
        def on_leave(e):
            boton.config(bg=bg_color)
            
        boton.bind("<Enter>", on_enter)
        boton.bind("<Leave>", on_leave)