from ttkbootstrap import ttk
from views.componentes.analisis_view import abrir_ventana_analisis

def crear_botones(parent, on_atender_callback, on_resumen_callback, rol_usuario):
    frame = ttk.Frame(parent)
    frame.pack(pady=10)

    # Botón Atender Cliente
    btn_atender = ttk.Button(
        frame,
        text="Atender Cliente",
        width=20,
        command=on_atender_callback,
        bootstyle="success"
    )
    btn_atender.pack(side="left", padx=10)

    # Botón Resumen Diario
    btn_resumen = ttk.Button(
        frame,
        text="Resumen Diario",
        width=20,
        command=on_resumen_callback,
        bootstyle="primary"
    )
    btn_resumen.pack(side="left", padx=10)

    # Botón Análisis con Spark
    btn_analisis = ttk.Button(
        frame,
        text="Análisis con Spark",
        width=20,
        command=abrir_ventana_analisis,
        bootstyle="info"
    )
    btn_analisis.pack(side="left", padx=10)

    # Restricción por rol
    if rol_usuario == "vendedor":
        btn_analisis.config(state="disabled")
