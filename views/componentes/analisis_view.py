# views/componentes/analisis_view.py
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from controllers.analisis_controller import ejecutar_analisis, probar_conexion, exportar_resultados

def abrir_ventana_analisis():
    root = tk.Toplevel()
    root.title("Análisis Completo de Supermercado")
    root.geometry("1000x800")

    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill="both", expand=True)

    titulo = ttk.Label(main_frame, text="Análisis de Datos del Supermercado", font=("Arial", 16, "bold"))
    titulo.pack(pady=10)

    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(pady=10)

    resultado_area = scrolledtext.ScrolledText(main_frame, width=120, height=35, font=("Consolas", 10))
    resultado_area.pack(pady=10, fill="both", expand=True)

    def accion_test():
        try:
            count = probar_conexion()
            messagebox.showinfo("Conexión Exitosa", f"Se encontraron {count} registros en 'clientes'")
        except Exception as e:
            messagebox.showerror("Error de Conexión", str(e))

    def accion_analizar():
        try:
            resultado = ejecutar_analisis()
            resultado_area.delete(1.0, tk.END)
            resultado_area.insert(tk.END, resultado)
        except Exception as e:
            messagebox.showerror("Error en análisis", str(e))

    def accion_exportar():
        contenido = resultado_area.get(1.0, tk.END).strip()
        if contenido:
            exportar_resultados(contenido)
            messagebox.showinfo("Éxito", "Resultados exportados")
        else:
            messagebox.showwarning("Advertencia", "Ejecuta el análisis primero.")

    ttk.Button(btn_frame, text="Probar Conexión", command=accion_test).grid(row=0, column=0, padx=5)
    ttk.Button(btn_frame, text="Realizar Análisis", command=accion_analizar).grid(row=0, column=1, padx=5)
    ttk.Button(btn_frame, text="Exportar CSV", command=accion_exportar).grid(row=0, column=2, padx=5)

    root.mainloop()
