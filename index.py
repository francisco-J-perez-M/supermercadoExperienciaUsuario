import tkinter as tk
from tkinter import ttk, messagebox
from conexion import get_db
from datetime import datetime

# Crear ventana principal
root = tk.Tk()
root.title("Supermercado")
root.geometry("800x500")

# Conectar a la base de datos
try:
    db = get_db()
    collection_areas = db['areas']
    collection_productos = db['productos']
except Exception as e:
    messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos: {str(e)}")
    exit()

# Variables globales
areas = []
productos_por_area = {}
cuenta_actual = {}
total_actual = 0

def cargar_areas():
    """Cargar las áreas desde la base de datos"""
    global areas
    try:
        areas_cursor = collection_areas.find().sort('nombre')
        areas = [area for area in areas_cursor]
        nombres_areas = [area['nombre'] for area in areas]
        combo_area['values'] = nombres_areas
        if nombres_areas:
            combo_area.current(0)
            cargar_productos_por_area(0)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron cargar las áreas: {str(e)}")

def cargar_productos_por_area(indice):
    """Cargar los productos de un área específica"""
    global productos_por_area
    if not areas:
        return
    
    area_seleccionada = areas[indice]
    area_id = area_seleccionada['_id']
    
    try:
        productos_cursor = collection_productos.find({'area_id': area_id}).sort('nombre')
        productos_por_area = {prod['_id']: prod for prod in productos_cursor}
        
        # Actualizar la lista de productos
        lista_productos.delete(0, tk.END)
        for producto in productos_por_area.values():
            lista_productos.insert(tk.END, f"{producto['nombre']} - ${producto['precio']:.2f}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron cargar los productos: {str(e)}")

def on_area_selected(event):
    """Evento cuando se selecciona un área diferente"""
    indice_seleccionado = combo_area.current()
    if indice_seleccionado >= 0:
        cargar_productos_por_area(indice_seleccionado)

def on_producto_selected(event):
    """Evento cuando se selecciona un producto"""
    seleccion = lista_productos.curselection()
    if seleccion:
        indice = seleccion[0]
        producto_id = list(productos_por_area.keys())[indice]
        producto = productos_por_area[producto_id]
        
        # Agregar a la cuenta actual
        global total_actual
        if producto_id in cuenta_actual:
            cuenta_actual[producto_id]['cantidad'] += 1
        else:
            cuenta_actual[producto_id] = {
                'nombre': producto['nombre'],
                'precio': producto['precio'],
                'cantidad': 1
            }
        
        total_actual += producto['precio']
        actualizar_cuenta()

def actualizar_cuenta():
    """Actualizar la visualización de la cuenta"""
    texto_cuenta.config(state="normal")
    texto_cuenta.delete(1.0, tk.END)
    
    for producto_id, datos in cuenta_actual.items():
        texto_cuenta.insert(tk.END, 
                           f"{datos['nombre']} x{datos['cantidad']} - ${datos['precio'] * datos['cantidad']:.2f}\n")
    
    texto_cuenta.insert(tk.END, f"\nTotal: ${total_actual:.2f}")
    texto_cuenta.config(state="disabled")

def atender_cliente():
    """Finalizar la atención del cliente y guardar en clientes"""
    global cuenta_actual, total_actual
    
    if not cuenta_actual:
        messagebox.showwarning("Atención", "No hay productos en la cuenta")
        return
    
    try:
        # Obtener cuántos clientes hay ya en la colección
        coleccion_clientes = db['clientes']
        num_clientes = coleccion_clientes.count_documents({})
        nombre_cliente = f"Cliente {num_clientes + 1}"
        
        # Guardar cliente en la base de datos con la estructura definida
        cliente = {
            "nombre": nombre_cliente,
            "productos": list(cuenta_actual.values()),
            "total": total_actual,
            "fecha": datetime.now().isoformat()
        }
        
        coleccion_clientes.insert_one(cliente)
        
        messagebox.showinfo("Éxito", f"{nombre_cliente} atendido por ${total_actual:.2f}")
        
        # Reiniciar la cuenta
        cuenta_actual = {}
        total_actual = 0
        actualizar_cuenta()
        
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo registrar el cliente: {str(e)}")

def mostrar_resumen():
    try:
        # Obtener la fecha de hoy como string en formato "YYYY-MM-DD" para la búsqueda
        hoy_str = datetime.now().strftime('%Y-%m-%d')
        
        # Formatear la fecha para mostrar en el resumen (ej: "2024-01-15" → "15/01/2024")
        fecha_formateada = datetime.now().strftime('%d/%m/%Y')

        # Consultar clientes cuya fecha (string) empiece con la fecha de hoy
        clientes_hoy = list(db['clientes'].find({'fecha': {'$regex': f'^{hoy_str}'}}))

        if not clientes_hoy:
            messagebox.showinfo("Resumen Diario", f"No hay clientes atendidos el día {fecha_formateada}")
            return

        total_diario = sum(cliente['total'] for cliente in clientes_hoy)
        cantidad_ventas = len(clientes_hoy)

        resumen = f"RESUMEN DEL DÍA: {fecha_formateada}\n\n"
        resumen += f"Clientes atendidos: {cantidad_ventas}\n"
        resumen += f"Total vendido: ${total_diario:.2f}\n\n"
        resumen += "Detalle de clientes:\n"

        for i, cliente in enumerate(clientes_hoy, 1):
            # Convertir el string de fecha a un objeto datetime para formatear la hora
            fecha_dt = datetime.fromisoformat(cliente['fecha'])
            resumen += f"\n{i}. {cliente['nombre']} - Total: ${cliente['total']:.2f} - {fecha_dt.strftime('%H:%M:%S')}\n"
            for prod in cliente['productos']:
                resumen += f"   - {prod['nombre']} x{prod['cantidad']}\n"

        # Crear ventana de resumen
        ventana_resumen = tk.Toplevel(root)
        ventana_resumen.title(f"Resumen Diario - {fecha_formateada}")
        ventana_resumen.geometry("500x400")

        texto_resumen = tk.Text(ventana_resumen, wrap=tk.WORD)
        texto_resumen.pack(fill="both", expand=True, padx=10, pady=10)
        texto_resumen.insert(1.0, resumen)
        texto_resumen.config(state="disabled")

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el resumen: {str(e)}")


# Título
titulo = tk.Label(root, text="Supermercado", font=("Arial", 20, "bold"))
titulo.pack(pady=10)

# Frame principal dividido en dos columnas
frame_principal = tk.Frame(root)
frame_principal.pack(fill="both", expand=True, padx=20, pady=10)

# ---- Columna izquierda: selección de área y productos ----
frame_izq = tk.Frame(frame_principal)
frame_izq.pack(side="left", fill="both", expand=True, padx=10)

lbl_area = tk.Label(frame_izq, text="Seleccionar área:", font=("Arial", 12))
lbl_area.pack(anchor="w")

combo_area = ttk.Combobox(frame_izq, state="readonly")
combo_area.pack(fill="x", pady=5)
combo_area.bind("<<ComboboxSelected>>", on_area_selected)

lbl_productos = tk.Label(frame_izq, text="Productos del área:", font=("Arial", 12))
lbl_productos.pack(anchor="w", pady=(10, 0))

# Frame para la lista de productos con scrollbar
frame_lista = tk.Frame(frame_izq)
frame_lista.pack(fill="both", expand=True)

scrollbar = tk.Scrollbar(frame_lista)
scrollbar.pack(side="right", fill="y")

lista_productos = tk.Listbox(frame_lista, yscrollcommand=scrollbar.set, height=10)
lista_productos.pack(fill="both", expand=True)
lista_productos.bind("<Double-Button-1>", on_producto_selected)

scrollbar.config(command=lista_productos.yview)

# ---- Columna derecha: cuenta en tiempo real ----
frame_der = tk.Frame(frame_principal)
frame_der.pack(side="right", fill="both", expand=True, padx=10)

lbl_cuenta = tk.Label(frame_der, text="Cuenta en tiempo real:", font=("Arial", 12))
lbl_cuenta.pack(anchor="w")

texto_cuenta = tk.Text(frame_der, height=12, state="disabled")
texto_cuenta.pack(fill="both", expand=True)

# ---- Botones ----
frame_botones = tk.Frame(root)
frame_botones.pack(pady=10)

btn_atender = tk.Button(frame_botones, text="Atender Cliente", width=20, command=atender_cliente)
btn_atender.pack(side="left", padx=10)

btn_resumen = tk.Button(frame_botones, text="Mostrar Resumen Diario", width=20, command=mostrar_resumen)
btn_resumen.pack(side="right", padx=10)

# Cargar datos iniciales
cargar_areas()
actualizar_cuenta()

# Ejecutar aplicación
root.mainloop()