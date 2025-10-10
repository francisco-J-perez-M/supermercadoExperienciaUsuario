import tkinter as tk
from tkinter import ttk

class UIHelper:
    # ───────────────────────────────────────────────────────────────
    # Modo 1: Oscuro clásico (ya existente)
    # ───────────────────────────────────────────────────────────────
    MODO_OSCURO = {
        "COLOR_PRIMARIO": "#1e1e1e",
        "COLOR_SECUNDARIO": "#2d2d30",
        "COLOR_TERCIARIO": "#3e3e42",
        "COLOR_TEXTO": "#ffffff",
        "COLOR_TEXTO_SECUNDARIO": "#cccccc",
        "COLOR_ACENTO": "#007acc",
        "COLOR_ACENTO_HOVER": "#005a9e",
        "COLOR_EXITO": "#107c10",
        "COLOR_PELIGRO": "#d13438"
    }

    # ───────────────────────────────────────────────────────────────
    # Modo 2: Claro elegante
    # ───────────────────────────────────────────────────────────────
    MODO_CLARO = {
        "COLOR_PRIMARIO": "#f5f5f5",
        "COLOR_SECUNDARIO": "#e0e0e0",
        "COLOR_TERCIARIO": "#d0d0d0",
        "COLOR_TEXTO": "#1e1e1e",
        "COLOR_TEXTO_SECUNDARIO": "#4d4d4d",
        "COLOR_ACENTO": "#007acc",
        "COLOR_ACENTO_HOVER": "#005a9e",
        "COLOR_EXITO": "#107c10",
        "COLOR_PELIGRO": "#d13438"
    }

    # ───────────────────────────────────────────────────────────────
    # Modo 3: Inspirado en imagen japonesa
    # ───────────────────────────────────────────────────────────────
    MODO_JAPON = {
        "COLOR_PRIMARIO": "#CDD5DB",       # fondo claro
        "COLOR_SECUNDARIO": "#A4B5C4",     # fondo intermedio
        "COLOR_TERCIARIO": "#4B6382",      # fondo profundo
        "COLOR_TEXTO": "#071739",          # texto principal
        "COLOR_TEXTO_SECUNDARIO": "#A68868",  # texto secundario
        "COLOR_ACENTO": "#E3C39D",         # beige dorado
        "COLOR_ACENTO_HOVER": "#A68868",   # taupe cálido
        "COLOR_EXITO": "#107c10",
        "COLOR_PELIGRO": "#d13438"
    }

    # Variables activas
    COLOR_PRIMARIO = MODO_OSCURO["COLOR_PRIMARIO"]
    COLOR_SECUNDARIO = MODO_OSCURO["COLOR_SECUNDARIO"]
    COLOR_TERCIARIO = MODO_OSCURO["COLOR_TERCIARIO"]
    COLOR_TEXTO = MODO_OSCURO["COLOR_TEXTO"]
    COLOR_TEXTO_SECUNDARIO = MODO_OSCURO["COLOR_TEXTO_SECUNDARIO"]
    COLOR_ACENTO = MODO_OSCURO["COLOR_ACENTO"]
    COLOR_ACENTO_HOVER = MODO_OSCURO["COLOR_ACENTO_HOVER"]
    COLOR_EXITO = MODO_OSCURO["COLOR_EXITO"]
    COLOR_PELIGRO = MODO_OSCURO["COLOR_PELIGRO"]

    @staticmethod
    def aplicar_modo(modo: str):
        """Aplica el conjunto de colores según el modo elegido"""
        if modo == "claro":
            colores = UIHelper.MODO_CLARO
        elif modo == "japon":
            colores = UIHelper.MODO_JAPON
        else:
            colores = UIHelper.MODO_OSCURO

        for k, v in colores.items():
            setattr(UIHelper, k, v)

    @staticmethod
    def configurar_estilo_ttk():
        """Configura el estilo ttk según el modo activo"""
        estilo = ttk.Style()
        estilo.theme_use('clam')

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
        """Estiliza un botón de tkinter con colores activos"""
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

        def on_enter(e):
            boton.config(bg=hover_color)

        def on_leave(e):
            boton.config(bg=bg_color)

        boton.bind("<Enter>", on_enter)
        boton.bind("<Leave>", on_leave)
