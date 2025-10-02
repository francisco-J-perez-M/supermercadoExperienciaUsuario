import tkinter as tk
from tkinter import messagebox
from db.conexion import get_db
from datetime import datetime
from views.PuntoVentaView import PuntoVentaView

class PuntoVentaController:
    def __init__(self):
        self.root = None
        self.view = None
        self.db = None
        self.collection_areas = None
        self.collection_productos = None
        
        # Variables de estado
        self.areas = []
        self.productos_por_area = {}
        self.cuenta_actual = {}
        self.total_actual = 0
        self.rol_usuario = None

    def iniciar_app(self, rol_usuario):
        self.rol_usuario = rol_usuario
        self.root = tk.Toplevel() if self._hay_ventana_principal() else tk.Tk()
        self.view = PuntoVentaView(self.root, self)
        
        try:
            self.db = get_db()
            self.collection_areas = self.db['areas']
            self.collection_productos = self.db['productos']
        except Exception as e:
            messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos: {str(e)}")
            return

        self.view.crear_vista_principal()
        
        # Restricciones por rol
        if rol_usuario == "vendedor":
            self.view.btn_resumen.config(state="disabled")

        self.cargar_areas()
        self.actualizar_cuenta()
        
        # Configurar cierre de ventana
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)
        self.root.mainloop()

    def _hay_ventana_principal(self):
        """Verificar si hay una ventana principal de Tk abierta"""
        try:
            return len(tk._default_root.children) > 0
        except:
            return False

    def cerrar_ventana(self):
        """Manejar el cierre de la ventana"""
        if messagebox.askyesno("Cerrar", "¿Desea cerrar el punto de venta?"):
            self.root.destroy()

    # ... (el resto de los métodos se mantienen igual)
    def cargar_areas(self):
        try:
            areas_cursor = self.collection_areas.find().sort('nombre')
            self.areas = [area for area in areas_cursor]
            nombres_areas = [area['nombre'] for area in self.areas]
            self.view.actualizar_combo_areas(nombres_areas)
            if nombres_areas:
                self.cargar_productos_por_area(0)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las áreas: {str(e)}")

    def cargar_productos_por_area(self, indice):
        if not self.areas:
            return
        
        area_seleccionada = self.areas[indice]
        area_id = area_seleccionada['_id']
        
        try:
            productos_cursor = self.collection_productos.find({'area_id': area_id}).sort('nombre')
            self.productos_por_area = {prod['_id']: prod for prod in productos_cursor}
            self.view.actualizar_lista_productos(self.productos_por_area.values())
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los productos: {str(e)}")

    def on_area_selected(self, event):
        indice_seleccionado = self.view.combo_area.current()
        if indice_seleccionado >= 0:
            self.cargar_productos_por_area(indice_seleccionado)

    def on_producto_selected(self, event):
        seleccion = self.view.lista_productos.curselection()
        if seleccion:
            indice = seleccion[0]
            producto_id = list(self.productos_por_area.keys())[indice]
            producto = self.productos_por_area[producto_id]
            
            if producto_id in self.cuenta_actual:
                self.cuenta_actual[producto_id]['cantidad'] += 1
            else:
                self.cuenta_actual[producto_id] = {
                    'nombre': producto['nombre'],
                    'precio': producto['precio'],
                    'cantidad': 1
                }
            
            self.total_actual += producto['precio']
            self.actualizar_cuenta()

    def actualizar_cuenta(self):
        self.view.actualizar_cuenta(self.cuenta_actual, self.total_actual)

    def atender_cliente(self):
        if not self.cuenta_actual:
            messagebox.showwarning("Atención", "No hay productos en la cuenta")
            return
        
        try:
            coleccion_clientes = self.db['clientes']
            num_clientes = coleccion_clientes.count_documents({})
            nombre_cliente = f"Cliente {num_clientes + 1}"
            
            cliente = {
                "nombre": nombre_cliente,
                "productos": list(self.cuenta_actual.values()),
                "total": self.total_actual,
                "fecha": datetime.now().isoformat()
            }
            
            coleccion_clientes.insert_one(cliente)
            
            messagebox.showinfo("Éxito", f"{nombre_cliente} atendido por ${self.total_actual:.2f}")
            
            # Reiniciar cuenta
            self.cuenta_actual = {}
            self.total_actual = 0
            self.actualizar_cuenta()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el cliente: {str(e)}")

    def mostrar_resumen(self):
        try:
            hoy_str = datetime.now().strftime('%Y-%m-%d')
            fecha_formateada = datetime.now().strftime('%d/%m/%Y')

            clientes_hoy = list(self.db['clientes'].find({'fecha': {'$regex': f'^{hoy_str}'}}))

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
                fecha_dt = datetime.fromisoformat(cliente['fecha'])
                resumen += f"\n{i}. {cliente['nombre']} - Total: ${cliente['total']:.2f} - {fecha_dt.strftime('%H:%M:%S')}\n"
                for prod in cliente['productos']:
                    resumen += f"   - {prod['nombre']} x{prod['cantidad']}\n"

            ventana_resumen = tk.Toplevel(self.root)
            ventana_resumen.title(f"Resumen Diario - {fecha_formateada}")
            ventana_resumen.geometry("500x400")

            texto_resumen = tk.Text(ventana_resumen, wrap=tk.WORD)
            texto_resumen.pack(fill="both", expand=True, padx=10, pady=10)
            texto_resumen.insert(1.0, resumen)
            texto_resumen.config(state="disabled")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el resumen: {str(e)}")