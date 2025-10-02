import tkinter as tk
from tkinter import messagebox
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, sum, count, col, desc, explode, date_format, max, min, countDistinct
from pyspark.sql.types import DateType, TimestampType
import datetime
import csv
from views.SparkView import SparkView

class SparkController:
    def __init__(self):
        self.root = tk.Toplevel()
        self.view = SparkView(self.root, self)
        self.spark = None
        self.df = None
        self.view.crear_vista()
        
    def _conectar_spark(self):
        """Crear sesión de Spark con el conector de MongoDB"""
        try:
            self.spark = SparkSession.builder \
                .appName("AnalisisSupermercado") \
                .config("spark.mongodb.input.uri", "mongodb://localhost:27017/supermercado_db.clientes") \
                .config("spark.mongodb.output.uri", "mongodb://localhost:27017/supermercado_db.clientes") \
                .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
                .getOrCreate()
            return True
        except Exception as e:
            raise Exception(f"Error al conectar con Spark: {str(e)}")

    def _cargar_datos(self):
        """Leer la colección clientes desde MongoDB"""
        try:
            self.df = self.spark.read \
                .format("mongo") \
                .option("uri", "mongodb://localhost:27017/supermercado_db.clientes") \
                .load()
            return True
        except Exception as e:
            raise Exception(f"Error al cargar datos: {str(e)}")

    def _cerrar_conexion(self):
        """Cerrar la sesión de Spark"""
        if self.spark:
            self.spark.stop()
            self.spark = None

    

    def realizar_analisis(self):
        """Realizar análisis completo de los datos"""
        try:
            self.view.deshabilitar_botones()
            self.view.mostrar_progreso("Conectando con Spark...")
            
            # Crear sesión de Spark con el conector de MongoDB
            self._conectar_spark()

            self.view.mostrar_progreso("Cargando datos desde MongoDB...")
            # Leer la colección clientes
            self._cargar_datos()

            # Mostrar esquema y algunos datos para debugging
            print("Esquema de los datos:")
            self.df.printSchema()
            print("\nPrimeras 5 filas:")
            self.df.show(5, truncate=False)

            resultado_texto = "=== ANÁLISIS COMPLETO DEL SUPERMERCADO ===\n\n"
            resultado_texto += f"Fecha del análisis: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            resultado_texto += f"Total de registros: {self.df.count()}\n\n"

            self.view.mostrar_progreso("Procesando fechas...")
            # 1. CONVERTIR FECHAS
            if 'fecha' in self.df.columns:
                # Extraer solo la parte de la fecha (primeros 10 caracteres)
                self.df = self.df.withColumn("fecha_simple", col("fecha").substr(1, 10))
                self.df = self.df.withColumn("fecha_date", col("fecha_simple").cast(DateType()))
                
                resultado_texto += f"Rango de fechas en los datos:\n"
                fechas = self.df.agg(min("fecha_date").alias("min_fecha"), max("fecha_date").alias("max_fecha")).first()
                resultado_texto += f"   - Desde: {fechas['min_fecha']}\n"
                resultado_texto += f"   - Hasta: {fechas['max_fecha']}\n\n"

            self.view.mostrar_progreso("Analizando ventas por día...")
            # 2. DÍA CON MÁS VENTAS (por monto total)
            if 'fecha_date' in self.df.columns and 'total' in self.df.columns:
                ventas_por_dia = self.df.groupBy("fecha_date") \
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

            self.view.mostrar_progreso("Calculando promedios...")
            # 3. PROMEDIO DE CLIENTES ATENDIDOS POR DÍA
            if 'fecha_date' in self.df.columns:
                clientes_por_dia = self.df.groupBy("fecha_date") \
                    .agg(count("nombre").alias("clientes_dia"))
                
                promedio_clientes = clientes_por_dia.select(avg("clientes_dia")).first()[0]
                resultado_texto += f"2. PROMEDIO DE CLIENTES POR DÍA:\n"
                resultado_texto += f"   - {promedio_clientes:.2f} clientes/día\n\n"

            # 4. PROMEDIO DE VENTA POR CLIENTE
            if 'total' in self.df.columns:
                promedio_venta = self.df.select(avg("total")).first()[0]
                resultado_texto += f"3. PROMEDIO DE VENTA POR CLIENTE:\n"
                resultado_texto += f"   - ${promedio_venta:.2f} por cliente\n\n"

            self.view.mostrar_progreso("Analizando productos...")
            # 5. PRODUCTOS MÁS VENDIDOS
            if 'productos' in self.df.columns:
                try:
                    # Explodir el array de productos
                    productos_exploded = self.df.select(explode("productos").alias("producto"))
                    
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

            self.view.mostrar_progreso("Analizando clientes...")
            # 6. CLIENTES QUE MÁS GASTARON
            if 'nombre' in self.df.columns and 'total' in self.df.columns:
                top_clientes = self.df.groupBy("nombre") \
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

            self.view.mostrar_progreso("Generando estadísticas finales...")
            # 7. ESTADÍSTICAS GENERALES
            if 'total' in self.df.columns:
                stats = self.df.agg(
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
            self.view.mostrar_resultados(resultado_texto)
            self.view.habilitar_botones()

            self._cerrar_conexion()

        except Exception as e:
            self.view.habilitar_botones()
            error_msg = f"Error en el análisis: {str(e)}\n\n"
            error_msg += "Asegúrate de que:\n"
            error_msg += "1. MongoDB esté ejecutándose en localhost:27017\n"
            error_msg += "2. La base de datos 'supermercado' exista\n"
            error_msg += "3. La colección 'clientes' exista y tenga datos\n"
            error_msg += "4. Los datos tengan la estructura correcta\n\n"
            error_msg += f"Error detallado: {type(e).__name__}"
            messagebox.showerror("Error", error_msg)

    def exportar_resultados(self):
        """Exportar resultados a un archivo CSV"""
        try:
            contenido = self.view.obtener_resultados().strip()
            if contenido:
                # Dividir el contenido en líneas
                lineas = contenido.split("\n")

                with open("analisis_supermercado.csv", "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)

                    for linea in lineas:
                        if linea.strip():
                            # Separar por ":" para hacer columnas simples (clave, valor)
                            if ":" in linea:
                                partes = [p.strip() for p in linea.split(":", 1)]
                                writer.writerow(partes)
                            else:
                                # Si no hay ":", guardar la línea completa en una sola celda
                                writer.writerow([linea])

                messagebox.showinfo("Éxito", "Resultados exportados a 'analisis_supermercado.csv'")
            else:
                messagebox.showwarning("Advertencia", "No hay resultados para exportar. Ejecuta el análisis primero.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {str(e)}")

    def iniciar_analisis(self):
        """Iniciar la ventana de análisis Spark"""
        self.root.mainloop()