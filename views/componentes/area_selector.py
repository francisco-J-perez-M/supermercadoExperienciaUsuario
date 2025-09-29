import customtkinter as ctk
from estilos.paleta_colores import COLORES
from estilos.fuentes import FUENTES

def crear_selector_area(parent, on_select_callback):
    label = ctk.CTkLabel(parent, text="Seleccionar área:", font=FUENTES["etiqueta"], text_color=COLORES["dorado"])
    label.pack(anchor="w", pady=(10, 0))

    combo = ctk.CTkComboBox(parent, values=[], command=on_select_callback,
                            font=FUENTES["entrada"], fg_color=COLORES["campo_fondo"],
                            text_color="white", button_color=COLORES["dorado"],
                            dropdown_fg_color=COLORES["campo_fondo"],
                            dropdown_text_color="white", corner_radius=8)
    combo.pack(fill="x", pady=5)

    return combo
