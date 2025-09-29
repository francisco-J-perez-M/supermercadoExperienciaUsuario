from models.usuario import UsuarioModel
from views.interfaz_terminal import iniciar_app
import customtkinter as ctk
from estilos.paleta_colores import COLORES
from estilos.fuentes import FUENTES

def autenticar_usuario(usuario, password, ventana_login):
    modelo = UsuarioModel()
    user = modelo.validar_credenciales(usuario, password)

    if user:
        rol = user["rol"]

        # --- Ventana institucional de bienvenida ---
        aviso = ctk.CTkToplevel(ventana_login)
        aviso.title("Bienvenido")
        aviso.geometry("300x180")
        aviso.configure(fg_color=COLORES["fondo_principal"])

        mensaje = ctk.CTkLabel(aviso, text=f"Bienvenido, {usuario}\nRol: {rol}",
                               font=FUENTES["etiqueta"], text_color=COLORES["dorado"])
        mensaje.pack(pady=30)

        btn_continuar = ctk.CTkButton(aviso, text="Continuar", font=FUENTES["boton"],
                                      fg_color=COLORES["dorado"], text_color=COLORES["texto_oscuro"],
                                      corner_radius=10,
                                      command=lambda: continuar_login(aviso, ventana_login, usuario, rol))
        btn_continuar.pack(pady=10)

    else:
        # --- Ventana institucional de error ---
        error = ctk.CTkToplevel(ventana_login)
        error.title("Error de acceso")
        error.geometry("300x160")
        error.configure(fg_color=COLORES["fondo_principal"])

        mensaje = ctk.CTkLabel(error, text="Usuario o contraseña incorrectos",
                               font=FUENTES["etiqueta"], text_color="red")
        mensaje.pack(pady=30)

        btn_cerrar = ctk.CTkButton(error, text="Cerrar", font=FUENTES["boton"],
                                   fg_color=COLORES["dorado"], text_color=COLORES["texto_oscuro"],
                                   corner_radius=10,
                                   command=error.destroy)
        btn_cerrar.pack(pady=10)

def continuar_login(aviso, ventana_login, usuario, rol):
    aviso.destroy()
    ventana_login.withdraw()
    iniciar_app(usuario, rol)
