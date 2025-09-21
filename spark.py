import tkinter as tk
from tkinter import messagebox
from pyspark.sql import SparkSession

def calcular_promedio():
    try:
        # Crear sesión de Spark con el conector de MongoDB
        spark = SparkSession.builder \
            .appName("ClientesPromedio") \
            .config("spark.mongodb.input.uri", "mongodb://localhost:27017/supermercado_db.clientes") \
            .config("spark.mongodb.output.uri", "mongodb://localhost:27017/supermercado_db.clientes") \
            .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
            .getOrCreate()

        # Leer la colección clientes con el conector
        df = spark.read \
            .format("com.mongodb.spark.sql.DefaultSource") \
            .option("uri", "mongodb://localhost:27017/supermercado_db.clientes") \
            .load()

        # Mostrar el esquema para verificar los datos
        df.printSchema()
        
        # Mostrar algunas filas para debugging
        df.show(5)

        # Calcular el promedio del campo "total"
        promedio = df.selectExpr("avg(total) as promedio_total").collect()[0]["promedio_total"]

        # Mostrar resultado en ventana
        messagebox.showinfo("Resultado", f"El total promedio es: {promedio:.2f}")

        spark.stop()
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Interfaz gráfica Tkinter
root = tk.Tk()
root.title("Promedio de Clientes")
root.geometry("300x150")

btn = tk.Button(root, text="Calcular Promedio", command=calcular_promedio)
btn.pack(pady=40)

root.mainloop()