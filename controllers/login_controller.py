import tkinter as tk
from tkinter import messagebox
from db.conexion import get_db
import views.interfaz_terminal as interfaz_terminal

def login():
    usuario = entry_usuario.get().strip()
    password = entry_password.get().strip()

    if not usuario or not password:
        messagebox.showwarning("Campos vacíos", "Debes ingresar usuario y contraseña")
        return

    db = get_db()
    coleccion_usuarios = db["usuarios"]

    user = coleccion_usuarios.find_one({"usuario": usuario, "password": password})

    if user:
        rol = user["rol"]
        messagebox.showinfo("Bienvenido", f"Usuario: {usuario}\nRol: {rol}")
        root.destroy()  # Cerramos login
        interfaz_terminal.iniciar_app(rol)  # Abrimos la ventana principal con permisos según rol
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")


# --- Ventana de login ---
root = tk.Tk()
root.title("Login - Supermercado")
root.geometry("300x200")

tk.Label(root, text="Usuario:").pack(pady=5)
entry_usuario = tk.Entry(root)
entry_usuario.pack(pady=5)

tk.Label(root, text="Contraseña:").pack(pady=5)
entry_password = tk.Entry(root, show="*")
entry_password.pack(pady=5)

btn_login = tk.Button(root, text="Ingresar", command=login)
btn_login.pack(pady=20)

root.mainloop()
