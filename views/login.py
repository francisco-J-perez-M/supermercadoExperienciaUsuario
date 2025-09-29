from estilos.tema_personalizado import crear_ventana
from estilos.paleta_colores import COLORES
from estilos.fuentes import FUENTES
from estilos.estilos_widgets import aplicar_estilo_label, aplicar_estilo_entry, aplicar_estilo_boton
from controllers.login_controller import autenticar_usuario
import customtkinter as ctk

def mostrar_login():
    root = crear_ventana("Login - Supermercado")

    # --- Tarjeta centrada con bordes redondeados ---
    tarjeta = ctk.CTkFrame(root, width=340, height=260,
                        fg_color=COLORES["fondo_principal"],
                        corner_radius=20,
                        border_color=COLORES["borde_dorado"],
                        border_width=2)
    tarjeta.place(relx=0.5, rely=0.5, anchor="center")  # ✅ Sin width/height aquí

    # --- Título institucional ---
    titulo = ctk.CTkLabel(tarjeta, text="Login", font=FUENTES["titulo"],
                          text_color=COLORES["dorado"])
    titulo.pack(pady=(15, 10))

    # --- Usuario ---
    lbl_usuario = ctk.CTkLabel(tarjeta, text="Usuario:")
    aplicar_estilo_label(lbl_usuario)
    lbl_usuario.pack(anchor="w", padx=20)
    entry_usuario = ctk.CTkEntry(tarjeta)
    aplicar_estilo_entry(entry_usuario)
    entry_usuario.pack(fill="x", padx=20, pady=5)

    # --- Contraseña ---
    lbl_password = ctk.CTkLabel(tarjeta, text="Contraseña:")
    aplicar_estilo_label(lbl_password)
    lbl_password.pack(anchor="w", padx=20, pady=(10, 0))
    entry_password = ctk.CTkEntry(tarjeta, show="*")
    aplicar_estilo_entry(entry_password)
    entry_password.pack(fill="x", padx=20, pady=5)

    # --- Botón ingresar ---
    def intentar_login():
        usuario = entry_usuario.get().strip()
        password = entry_password.get().strip()
        autenticar_usuario(usuario, password, root)

    btn_login = ctk.CTkButton(tarjeta, text="Ingresar", command=intentar_login)
    aplicar_estilo_boton(btn_login)
    btn_login.pack(pady=15)

    root.mainloop()
