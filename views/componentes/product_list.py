import customtkinter as ctk
from estilos.paleta_colores import COLORES
from estilos.fuentes import FUENTES

def crear_lista_productos(parent, on_agregar_callback):
    label = ctk.CTkLabel(parent, text="Productos del área:", font=FUENTES["etiqueta"], text_color=COLORES["dorado"])
    label.pack(anchor="w", pady=(10, 0))

    lista_frame = ctk.CTkScrollableFrame(parent, fg_color=COLORES["campo_fondo"], corner_radius=10)
    lista_frame.pack(fill="both", expand=True, pady=5)

    def agregar_producto(nombre, precio):
        fila = ctk.CTkFrame(lista_frame, fg_color="transparent")
        fila.pack(fill="x", padx=5, pady=2)

        etiqueta = ctk.CTkLabel(fila, text=f"{nombre} - ${precio:.2f}", font=FUENTES["entrada"], text_color="white")
        etiqueta.pack(side="left", padx=5)

        btn_agregar = ctk.CTkButton(fila, text="Agregar", font=FUENTES["boton"],
                                    fg_color=COLORES["dorado"], text_color=COLORES["texto_oscuro"],
                                    corner_radius=8,
                                    command=lambda: on_agregar_callback(nombre, precio))
        btn_agregar.pack(side="right", padx=5)

    lista_frame.agregar_producto = agregar_producto
    lista_frame.limpiar = lambda: [w.destroy() for w in lista_frame.winfo_children()]

    return lista_frame
