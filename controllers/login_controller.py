from models.usuario import UsuarioModel
from views.interfaz_terminal import iniciar_app
from tkinter import messagebox

def autenticar_usuario(usuario, password, ventana_login):
    modelo = UsuarioModel()
    user = modelo.validar_credenciales(usuario, password)

    if user:
        rol = user["rol"]
        messagebox.showinfo("Bienvenido", f"Usuario: {usuario}\nRol: {rol}")
        # 👇 Ocultamos la ventana de login en lugar de destruirla
        ventana_login.withdraw()
        iniciar_app(rol)
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")
