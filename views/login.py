from views.tema_bootstrap import crear_ventana
from controllers.login_controller import autenticar_usuario
from ttkbootstrap import ttk

def mostrar_login():
    root = crear_ventana("Login - Supermercado", "300x220", "flatly")

    # --- Etiquetas y campos ---
    ttk.Label(root, text="Usuario:").pack(pady=(15, 5))
    entry_usuario = ttk.Entry(root)
    entry_usuario.pack(pady=5)

    ttk.Label(root, text="Contraseña:").pack(pady=5)
    entry_password = ttk.Entry(root, show="*")
    entry_password.pack(pady=5)

    # --- Botón de ingreso ---
    def intentar_login():
        usuario = entry_usuario.get().strip()
        password = entry_password.get().strip()
        autenticar_usuario(usuario, password, root)

    btn_login = ttk.Button(root, text="Ingresar", command=intentar_login, bootstyle="primary")
    btn_login.pack(pady=15)

    root.mainloop()
