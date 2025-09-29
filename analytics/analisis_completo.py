# analytics/analisis_completo.py
import datetime
import csv
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, sum, count, col, desc, explode, max, min, stddev
from pyspark.sql.types import DateType

def crear_spark(app_name="AnalisisSupermercado"):
    """Crea la sesión de Spark conectada a MongoDB"""
    spark = SparkSession.builder \
        .appName(app_name) \
        .config("spark.mongodb.input.uri", "mongodb://localhost:27017/supermercado_db.clientes") \
        .config("spark.mongodb.output.uri", "mongodb://localhost:27017/supermercado_db.clientes") \
        .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
        .getOrCreate()
    return spark

def realizar_analisis():
    """Ejecuta el análisis completo y devuelve un texto con los resultados"""
    spark = crear_spark()
    df = spark.read.format("mongo").load()

    resultado_texto = "=== ANÁLISIS COMPLETO DEL SUPERMERCADO ===\n\n"
    resultado_texto += f"Fecha del análisis: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    resultado_texto += f"Total de registros: {df.count()}\n\n"

    # Conversión de fechas
    if 'fecha' in df.columns:
        df = df.withColumn("fecha_simple", col("fecha").substr(1, 10))
        df = df.withColumn("fecha_date", col("fecha_simple").cast(DateType()))
        fechas = df.agg(min("fecha_date").alias("min_fecha"), max("fecha_date").alias("max_fecha")).first()
        resultado_texto += f"Rango de fechas en los datos:\n"
        resultado_texto += f"   - Desde: {fechas['min_fecha']}\n"
        resultado_texto += f"   - Hasta: {fechas['max_fecha']}\n\n"

    # Día con más ventas
    if 'fecha_date' in df.columns and 'total' in df.columns:
        ventas_por_dia = df.groupBy("fecha_date").agg(sum("total").alias("total_ventas")).orderBy(desc("total_ventas"))
        if ventas_por_dia.count() > 0:
            dia_mas_ventas = ventas_por_dia.first()
            resultado_texto += f"1. DÍA CON MÁS VENTAS: {dia_mas_ventas['fecha_date']} (${dia_mas_ventas['total_ventas']:.2f})\n\n"

    # Promedio de venta por cliente
    if 'total' in df.columns:
        promedio_venta = df.select(avg("total")).first()[0]
        resultado_texto += f"2. PROMEDIO DE VENTA POR CLIENTE: ${promedio_venta:.2f}\n\n"

    # Promedio de clientes atendidos por día
    if 'fecha_date' in df.columns:
        clientes_por_dia = df.groupBy("fecha_date").agg(count("*").alias("clientes"))
        promedio_clientes = clientes_por_dia.select(avg("clientes")).first()[0]
        resultado_texto += f"3. PROMEDIO DE CLIENTES ATENDIDOS POR DÍA: {promedio_clientes:.2f}\n\n"

    # Productos más vendidos
    if 'productos' in df.columns:
        productos_exploded = df.select(explode("productos").alias("producto"))
        productos_cantidad = productos_exploded.groupBy("producto.nombre") \
            .agg(sum("producto.cantidad").alias("total_vendido")) \
            .orderBy(desc("total_vendido")).limit(10)
        resultado_texto += "5. PRODUCTOS MÁS VENDIDOS (TOP 10):\n"
        for i, row in enumerate(productos_cantidad.collect(), 1):
            resultado_texto += f"   {i}. {row['nombre']}: {row['total_vendido']} unidades\n"
        resultado_texto += "\n"

    # Estadísticas generales de ventas
    if 'total' in df.columns:
        stats = df.select(
            max("total").alias("maximo"),
            min("total").alias("minimo"),
            avg("total").alias("promedio"),
            stddev("total").alias("desviacion")
        ).first()
        resultado_texto += "6. ESTADÍSTICAS GENERALES DE VENTAS:\n"
        resultado_texto += f"   - Venta máxima: ${stats['maximo']:.2f}\n"
        resultado_texto += f"   - Venta mínima: ${stats['minimo']:.2f}\n"
        resultado_texto += f"   - Promedio: ${stats['promedio']:.2f}\n"
        resultado_texto += f"   - Desviación estándar: {stats['desviacion']:.2f}\n\n"

    spark.stop()
    return resultado_texto

def test_conexion():
    """Prueba si la conexión con MongoDB funciona"""
    spark = crear_spark("TestConexion")
    df = spark.read.format("mongo").load()
    count = df.count()
    spark.stop()
    return count

def exportar_csv(contenido, filename="analisis_supermercado.csv"):
    """Exporta resultados a CSV"""
    lineas = contenido.split("\n")
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for linea in lineas:
            if ":" in linea:
                writer.writerow([p.strip() for p in linea.split(":", 1)])
            else:
                writer.writerow([linea])
