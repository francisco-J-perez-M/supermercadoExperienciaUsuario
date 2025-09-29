import customtkinter as ctk
from estilos.paleta_colores import COLORES
from estilos.fuentes import FUENTES

def crear_cuenta_display(parent):
    label = ctk.CTkLabel(parent, text="Cuenta en tiempo real:", font=FUENTES["etiqueta"], text_color=COLORES["dorado"])
    label.pack(anchor="w", pady=(10, 0))

    texto = ctk.CTkTextbox(parent, height=180, font=FUENTES["entrada"],
                           fg_color=COLORES["campo_fondo"], text_color="white",
                           corner_radius=8)
    texto.pack(fill="both", expand=True, pady=5)
    texto.configure(state="disabled")

    return texto
