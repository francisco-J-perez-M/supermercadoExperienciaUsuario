from ttkbootstrap import ttk

def crear_selector_area(parent, on_select_callback):
    label = ttk.Label(parent, text="Seleccionar área:", font=("Arial", 12))
    label.pack(anchor="w")

    combo = ttk.Combobox(parent, state="readonly")
    combo.pack(fill="x", pady=5)
    combo.bind("<<ComboboxSelected>>", on_select_callback)

    return combo
