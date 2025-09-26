from views.tema_bootstrap import crear_ventana
from services.verificador_db import base_datos_esta_poblada
from services.poblacion_local import poblar_base_local
from services.poblacion_servidor import poblar_base_servidor
from views.login import mostrar_login
from ttkbootstrap import ttk
from tkinter import messagebox

def mostrar_ventana_inicio():
    if base_datos_esta_poblada():
        mostrar_login()
        return

    root = crear_ventana("Inicialización del Sistema", "400x250", "flatly")

    label = ttk.Label(root, text="¿Qué tipo de despliegue deseas realizar?", font=("Arial", 12))
    label.pack(pady=20)

    def iniciar_local():
        poblar_base_local()
        messagebox.showinfo("Despliegue Local", "Base de datos local poblada con 500,000 registros.")
        root.withdraw()  # 👈 Oculta la ventana sin destruirla
        mostrar_login()

    def iniciar_servidor():
        poblar_base_servidor()
        messagebox.showinfo("Despliegue Servidor", "Base mínima poblada para pruebas en servidor.")
        root.withdraw()  # 👈 También aquí
        mostrar_login()

    btn_local = ttk.Button(root, text="Despliegue Local", command=iniciar_local, bootstyle="success")
    btn_local.pack(pady=10)

    btn_servidor = ttk.Button(root, text="Despliegue en Servidor", command=iniciar_servidor, bootstyle="info")
    btn_servidor.pack(pady=10)

    root.mainloop()
