import tkinter as tk
from tkinter import messagebox
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, sum, count, col, desc, explode, max, min
from pyspark.sql.types import DateType
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
        try:
            self.spark = SparkSession.builder \
                .appName("AnalisisSupermercado") \
                .config("spark.mongodb.input.uri", "mongodb://localhost:27017/supermercado_db.clientes") \
                .config("spark.mongodb.output.uri", "mongodb://localhost:27017/supermercado_db.clientes") \
                .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
                .config("spark.sql.adaptive.enabled", "false") \
                .config("spark.sql.shuffle.partitions", "4") \
                .getOrCreate()
            return True
        except Exception as e:
            raise Exception(f"Error al conectar con Spark: {str(e)}")

    def _cargar_datos(self):
        try:
            self.df = self.spark.read \
                .format("mongo") \
                .option("uri", "mongodb://localhost:27017/supermercado_db.clientes") \
                .load()
            return True
        except Exception as e:
            raise Exception(f"Error al cargar datos: {str(e)}")

    def _cerrar_conexion(self):
        if self.spark:
            self.spark.stop()
            self.spark = None

    def realizar_analisis(self):
        try:
            self.view.deshabilitar_botones()
            total_pasos = 7
            self.view.iniciar_progreso(max_pasos=total_pasos, mensaje="Iniciando análisis completo...")

            resultado_texto = "=== ANÁLISIS COMPLETO DEL SUPERMERCADO ===\n\n"
            resultado_texto += f"Fecha del análisis: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

            # Paso 1: Conectar Spark
            self.view.mostrar_progreso("Conectando con Spark...")
            self.view.avanzar_progreso(1, total_pasos, "Conectando con Spark...")
            self._conectar_spark()

            # Paso 2: Cargar datos
            self.view.mostrar_progreso("Cargando datos desde MongoDB...")
            self.view.avanzar_progreso(2, total_pasos, "Cargando datos desde MongoDB...")
            self._cargar_datos()
            resultado_texto += f"Total de registros: {self.df.count()}\n\n"

            # Paso 3: Procesar fechas
            self.view.mostrar_progreso("Procesando fechas...")
            self.view.avanzar_progreso(3, total_pasos, "Procesando fechas...")
            if 'fecha' in self.df.columns:
                self.df = self.df.withColumn("fecha_simple", col("fecha").substr(1, 10))
                self.df = self.df.withColumn("fecha_date", col("fecha_simple").cast(DateType()))
                fechas = self.df.agg(min("fecha_date").alias("min_fecha"), max("fecha_date").alias("max_fecha")).first()
                resultado_texto += f"Rango de fechas en los datos:\n   - Desde: {fechas['min_fecha']}\n   - Hasta: {fechas['max_fecha']}\n\n"

            # Paso 4: Día con más ventas
            self.view.mostrar_progreso("Analizando ventas por día...")
            self.view.avanzar_progreso(4, total_pasos, "Analizando ventas por día...")
            if 'fecha_date' in self.df.columns and 'total' in self.df.columns:
                ventas_por_dia = self.df.groupBy("fecha_date") \
                    .agg(sum("total").alias("total_ventas"), count("_id").alias("cantidad_ventas")) \
                    .orderBy(desc("total_ventas"))
                if ventas_por_dia.count() > 0:
                    dia_mas_ventas = ventas_por_dia.first()
                    resultado_texto += f"1. DÍA CON MÁS VENTAS (POR MONTO):\n   - Fecha: {dia_mas_ventas['fecha_date']}\n   - Total vendido: ${dia_mas_ventas['total_ventas']:.2f}\n   - Ventas realizadas: {dia_mas_ventas['cantidad_ventas']}\n\n"

            # Paso 5: Promedios
            self.view.mostrar_progreso("Calculando promedios...")
            self.view.avanzar_progreso(5, total_pasos, "Calculando promedios...")
            if 'fecha_date' in self.df.columns:
                clientes_por_dia = self.df.groupBy("fecha_date").agg(count("nombre").alias("clientes_dia"))
                promedio_clientes = clientes_por_dia.select(avg("clientes_dia")).first()[0]
                resultado_texto += f"2. PROMEDIO DE CLIENTES POR DÍA:\n   - {promedio_clientes:.2f} clientes/día\n\n"
            if 'total' in self.df.columns:
                promedio_venta = self.df.select(avg("total")).first()[0]
                resultado_texto += f"3. PROMEDIO DE VENTA POR CLIENTE:\n   - ${promedio_venta:.2f} por cliente\n\n"

            # Paso 6: Productos
            self.view.mostrar_progreso("Analizando productos...")
            self.view.avanzar_progreso(6, total_pasos, "Analizando productos...")
            if 'productos' in self.df.columns:
                try:
                    productos_exploded = self.df.select(explode("productos").alias("producto"))
                    productos_cantidad = productos_exploded.groupBy("producto.nombre") \
                        .agg(sum("producto.cantidad").alias("total_vendido"),
                             sum(col("producto.precio") * col("producto.cantidad")).alias("ingresos_totales")) \
                        .orderBy(desc("total_vendido")) \
                        .limit(10)
                    resultado_texto += "4. PRODUCTOS MÁS VENDIDOS (TOP 10):\n"
                    for i, row in enumerate(productos_cantidad.collect(), 1):
                        resultado_texto += f"   {i}. {row['nombre']}: {int(row['total_vendido'])} unidades (${row['ingresos_totales']:.2f})\n"
                    resultado_texto += "\n"
                except Exception as e:
                    resultado_texto += f"4. ERROR en análisis de productos: {str(e)}\n\n"

            # Paso 7: Clientes y estadísticas
            self.view.mostrar_progreso("Analizando clientes y estadísticas finales...")
            self.view.avanzar_progreso(7, total_pasos, "Analizando clientes y estadísticas finales...")
            if 'nombre' in self.df.columns and 'total' in self.df.columns:
                top_clientes = self.df.groupBy("nombre") \
                    .agg(sum("total").alias("gasto_total"), count("*").alias("compras_realizadas")) \
                    .orderBy(desc("gasto_total")).limit(10)
                resultado_texto += "5. CLIENTES QUE MÁS GASTARON (TOP 10):\n"
                for i, row in enumerate(top_clientes.collect(), 1):
                    resultado_texto += f"   {i}. {row['nombre']}: ${row['gasto_total']:.2f} ({row['compras_realizadas']} compras)\n"
                resultado_texto += "\n"
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

            # Finalizar
            self.view.mostrar_resultados(resultado_texto)
            self.view.finalizar_progreso("Análisis completado exitosamente")
            self.view.habilitar_botones()
            self._cerrar_conexion()

        except Exception as e:
            self.view.habilitar_botones()
            self.view.mostrar_error(f"Error en el análisis: {str(e)}")
            error_msg = f"Error en el análisis: {str(e)}\n\n"
            error_msg += "Asegúrate de que:\n1. MongoDB esté ejecutándose en localhost:27017\n2. La base de datos 'supermercado' exista\n3. La colección 'clientes' exista y tenga datos\n4. Los datos tengan la estructura correcta\n\n"
            error_msg += f"Error detallado: {type(e).__name__}"
            messagebox.showerror("Error", error_msg)

    def exportar_resultados(self):
        try:
            contenido = self.view.obtener_resultados().strip()
            if contenido:
                lineas = contenido.split("\n")
                with open("analisis_supermercado.csv", "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    for linea in lineas:
                        if linea.strip():
                            if ":" in linea:
                                partes = [p.strip() for p in linea.split(":", 1)]
                                writer.writerow(partes)
                            else:
                                writer.writerow([linea])
                messagebox.showinfo("Éxito", "Resultados exportados a 'analisis_supermercado.csv'")
            else:
                messagebox.showwarning("Advertencia", "No hay resultados para exportar. Ejecuta el análisis primero.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {str(e)}")

    def iniciar_analisis(self):
        self.root.mainloop()