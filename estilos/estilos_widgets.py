from estilos.paleta_colores import COLORES
from estilos.fuentes import FUENTES

def aplicar_estilo_label(widget):
    widget.configure(font=FUENTES["etiqueta"], text_color=COLORES["dorado"])

def aplicar_estilo_entry(widget):
    widget.configure(font=FUENTES["entrada"], fg_color=COLORES["campo_fondo"],
                     text_color="white", border_color=COLORES["dorado"], corner_radius=8)

def aplicar_estilo_boton(widget):
    widget.configure(font=FUENTES["boton"], fg_color=COLORES["dorado"],
                     text_color=COLORES["texto_oscuro"], corner_radius=10)
