import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, sum, count, col, desc, explode, date_format, max, min, countDistinct
from pyspark.sql.types import DateType, TimestampType
import datetime

def realizar_analisis_completo():
    try:
        # Crear sesión de Spark con el conector de MongoDB
        spark = SparkSession.builder \
            .appName("AnalisisSupermercado") \
            .config("spark.mongodb.input.uri", "mongodb://localhost:27017/supermercado_db.clientes") \
            .config("spark.mongodb.output.uri", "mongodb://localhost:27017/supermercado_db.clientes") \
            .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
            .getOrCreate()

        # Leer la colección clientes
        df = spark.read \
            .format("mongo") \
            .option("uri", "mongodb://localhost:27017/supermercado_db.clientes") \
            .load()

        # Mostrar esquema y algunos datos para debugging
        print("Esquema de los datos:")
        df.printSchema()
        print("\nPrimeras 5 filas:")
        df.show(5, truncate=False)

        resultado_texto = "=== ANÁLISIS COMPLETO DEL SUPERMERCADO ===\n\n"
        resultado_texto += f"Fecha del análisis: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        resultado_texto += f"Total de registros: {df.count()}\n\n"

        # 1. CONVERTIR FECHAS
        if 'fecha' in df.columns:
            # Extraer solo la parte de la fecha (primeros 10 caracteres)
            df = df.withColumn("fecha_simple", col("fecha").substr(1, 10))
            df = df.withColumn("fecha_date", col("fecha_simple").cast(DateType()))
            
            resultado_texto += f"Rango de fechas en los datos:\n"
            fechas = df.agg(min("fecha_date").alias("min_fecha"), max("fecha_date").alias("max_fecha")).first()
            resultado_texto += f"   - Desde: {fechas['min_fecha']}\n"
            resultado_texto += f"   - Hasta: {fechas['max_fecha']}\n\n"

        # 2. DÍA CON MÁS VENTAS (por monto total)
        if 'fecha_date' in df.columns and 'total' in df.columns:
            ventas_por_dia = df.groupBy("fecha_date") \
                .agg(sum("total").alias("total_ventas"),
                     count("_id").alias("cantidad_ventas")) \
                .orderBy(desc("total_ventas"))
            
            ventas_por_dia.show()  # Debug
            
            if ventas_por_dia.count() > 0:
                dia_mas_ventas = ventas_por_dia.first()
                
                resultado_texto += f"1. DÍA CON MÁS VENTAS (POR MONTO):\n"
                resultado_texto += f"   - Fecha: {dia_mas_ventas['fecha_date']}\n"
                resultado_texto += f"   - Total vendido: ${dia_mas_ventas['total_ventas']:.2f}\n"
                resultado_texto += f"   - Ventas realizadas: {dia_mas_ventas['cantidad_ventas']}\n\n"

        # 3. PROMEDIO DE CLIENTES ATENDIDOS POR DÍA
        if 'fecha_date' in df.columns:
            clientes_por_dia = df.groupBy("fecha_date") \
                .agg(count("nombre").alias("clientes_dia"))
            
            promedio_clientes = clientes_por_dia.select(avg("clientes_dia")).first()[0]
            resultado_texto += f"2. PROMEDIO DE CLIENTES POR DÍA:\n"
            resultado_texto += f"   - {promedio_clientes:.2f} clientes/día\n\n"

        # 4. PROMEDIO DE VENTA POR CLIENTE
        if 'total' in df.columns:
            promedio_venta = df.select(avg("total")).first()[0]
            resultado_texto += f"3. PROMEDIO DE VENTA POR CLIENTE:\n"
            resultado_texto += f"   - ${promedio_venta:.2f} por cliente\n\n"

        # 5. PRODUCTOS MÁS VENDIDOS
        if 'productos' in df.columns:
            try:
                # Explodir el array de productos
                productos_exploded = df.select(explode("productos").alias("producto"))
                
                # Productos más vendidos por cantidad
                productos_cantidad = productos_exploded.groupBy("producto.nombre") \
                    .agg(sum("producto.cantidad").alias("total_vendido"),
                         sum(col("producto.precio") * col("producto.cantidad")).alias("ingresos_totales")) \
                    .orderBy(desc("total_vendido")) \
                    .limit(10)
                
                resultado_texto += "4. PRODUCTOS MÁS VENDIDOS (POR CANTIDAD - TOP 10):\n"
                productos_data = productos_cantidad.collect()
                for i, row in enumerate(productos_data, 1):
                    resultado_texto += f"   {i}. {row['nombre']}: {int(row['total_vendido'])} unidades (${row['ingresos_totales']:.2f})\n"
                resultado_texto += "\n"
                
            except Exception as e:
                resultado_texto += f"4. ERROR en análisis de productos: {str(e)}\n\n"

        # 6. CLIENTES QUE MÁS GASTARON
        if 'nombre' in df.columns and 'total' in df.columns:
            top_clientes = df.groupBy("nombre") \
                .agg(sum("total").alias("gasto_total"),
                     count("*").alias("compras_realizadas")) \
                .orderBy(desc("gasto_total")) \
                .limit(10)
            
            resultado_texto += "5. CLIENTES QUE MÁS GASTARON (TOP 10):\n"
            clientes_data = top_clientes.collect()
            for i, row in enumerate(clientes_data, 1):
                resultado_texto += f"   {i}. {row['nombre']}: ${row['gasto_total']:.2f} "
                resultado_texto += f"({row['compras_realizadas']} compras)\n"
            resultado_texto += "\n"

        # 7. ESTADÍSTICAS GENERALES
        if 'total' in df.columns:
            stats = df.agg(
                count("*").alias("total_ventas"),
                sum("total").alias("ingresos_totales"),
                avg("total").alias("ticket_promedio"),
                max("total").alias("venta_maxima"),
                min("total").alias("venta_minima")
            ).first()
            
            resultado_texto += "6. ESTADÍSTICAS GENERALES:\n"
            resultado_texto += f"   - Total de ventas: {stats['total_ventas']}\n"
            resultado_texto += f"   - Ingresos totales: ${stats['ingresos_totales']:.2f}\n"
            resultado_texto += f"   - Ticket promedio: ${stats['ticket_promedio']:.2f}\n"
            resultado_texto += f"   - Venta máxima: ${stats['venta_maxima']:.2f}\n"
            resultado_texto += f"   - Venta mínima: ${stats['venta_minima']:.2f}\n"

        # Mostrar resultados en el área de texto
        resultado_area.delete(1.0, tk.END)
        resultado_area.insert(tk.END, resultado_texto)

        spark.stop()

    except Exception as e:
        error_msg = f"Error en el análisis: {str(e)}\n\n"
        error_msg += "Asegúrate de que:\n"
        error_msg += "1. MongoDB esté ejecutándose en localhost:27017\n"
        error_msg += "2. La base de datos 'supermercado_db' exista\n"
        error_msg += "3. La colección 'clientes' exista y tenga datos\n"
        error_msg += "4. Los datos tengan la estructura correcta\n\n"
        error_msg += f"Error detallado: {type(e).__name__}"
        messagebox.showerror("Error", error_msg)

def exportar_resultados():
    """Exportar resultados a un archivo de texto"""
    try:
        contenido = resultado_area.get(1.0, tk.END)
        if contenido.strip():
            with open("analisis_supermercado.txt", "w", encoding="utf-8") as f:
                f.write(contenido)
            messagebox.showinfo("Éxito", "Resultados exportados a 'analisis_supermercado.txt'")
        else:
            messagebox.showwarning("Advertencia", "No hay resultados para exportar. Ejecuta el análisis primero.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo exportar: {str(e)}")

def test_conexion():
    """Función para probar la conexión a MongoDB"""
    try:
        spark = SparkSession.builder \
            .appName("TestConexion") \
            .config("spark.mongodb.input.uri", "mongodb://localhost:27017/supermercado_db.clientes") \
            .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
            .getOrCreate()

        df = spark.read.format("mongo").load()
        count = df.count()
        spark.stop()
        
        messagebox.showinfo("Conexión Exitosa", f"Conexión a MongoDB exitosa!\nSe encontraron {count} registros en la colección 'clientes'")
    except Exception as e:
        messagebox.showerror("Error de Conexión", f"No se pudo conectar a MongoDB:\n{str(e)}")

# Interfaz gráfica
root = tk.Tk()
root.title("Análisis Completo de Supermercado")
root.geometry("1000x800")

# Frame principal
main_frame = ttk.Frame(root, padding="10")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Configurar grid
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
main_frame.columnconfigure(0, weight=1)
main_frame.rowconfigure(3, weight=1)

# Título
titulo = ttk.Label(main_frame, text="Análisis de Datos del Supermercado", 
                  font=("Arial", 16, "bold"))
titulo.grid(row=0, column=0, pady=10)

# Frame para botones
btn_frame = ttk.Frame(main_frame)
btn_frame.grid(row=1, column=0, pady=10)

# Botón de test de conexión
btn_test = ttk.Button(btn_frame, text="Probar Conexión MongoDB", 
                     command=test_conexion)
btn_test.grid(row=0, column=0, padx=5)

# Botón de análisis
btn_analizar = ttk.Button(btn_frame, text="Realizar Análisis Completo", 
                         command=realizar_analisis_completo)
btn_analizar.grid(row=0, column=1, padx=5)

# Botón de exportación
btn_exportar = ttk.Button(btn_frame, text="Exportar Resultados", 
                         command=exportar_resultados)
btn_exportar.grid(row=0, column=2, padx=5)

# Área de texto para resultados con scroll
resultado_area = scrolledtext.ScrolledText(main_frame, width=120, height=35, 
                                          font=("Consolas", 10))
resultado_area.grid(row=2, column=0, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))

# Información
info_text = """INSTRUCCIONES:
1. Primero haz clic en 'Probar Conexión MongoDB' para verificar la conexión
2. Luego haz clic en 'Realizar Análisis Completo'
3. Si todo funciona, puedes exportar los resultados

ESTRUCTURA ESPERADA DE DATOS:
- nombre: String (Nombre del cliente)
- productos: Array (Productos comprados con nombre, precio, cantidad)
- total: Number (Monto total de la compra)
- fecha: String (Fecha en formato ISO)
"""
info_label = ttk.Label(main_frame, text=info_text, foreground="green", justify=tk.LEFT)
info_label.grid(row=3, column=0, pady=5, sticky=tk.W)

# Configurar expansión
main_frame.columnconfigure(0, weight=1)
main_frame.rowconfigure(2, weight=1)

root.mainloop()