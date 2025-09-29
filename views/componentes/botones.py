import customtkinter as ctk
from estilos.paleta_colores import COLORES
from estilos.fuentes import FUENTES

def crear_botones(parent, on_atender_callback, on_resumen_callback, rol_usuario):
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(pady=10)

    btn_atender = ctk.CTkButton(frame, text="Atender Cliente", command=on_atender_callback,
                                font=FUENTES["boton"], fg_color=COLORES["dorado"],
                                text_color=COLORES["texto_oscuro"], corner_radius=10)
    btn_atender.pack(side="left", padx=10)

    btn_resumen = ctk.CTkButton(frame, text="Resumen Diario", command=on_resumen_callback,
                                font=FUENTES["boton"], fg_color=COLORES["dorado"],
                                text_color=COLORES["texto_oscuro"], corner_radius=10)
    btn_resumen.pack(side="right", padx=10)

    if rol_usuario == "vendedor":
        btn_resumen.configure(state="disabled")
