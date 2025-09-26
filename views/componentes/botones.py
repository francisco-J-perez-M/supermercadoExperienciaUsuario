from ttkbootstrap import ttk

def crear_botones(parent, on_atender_callback, on_resumen_callback, rol_usuario):
    frame = ttk.Frame(parent)
    frame.pack(pady=10)

    btn_atender = ttk.Button(frame, text="Atender Cliente", width=20, command=on_atender_callback, bootstyle="success")
    btn_atender.pack(side="left", padx=10)

    btn_resumen = ttk.Button(frame, text="Mostrar Resumen Diario", width=20, command=on_resumen_callback, bootstyle="info")
    btn_resumen.pack(side="right", padx=10)

    if rol_usuario == "vendedor":
        btn_resumen.config(state="disabled")
