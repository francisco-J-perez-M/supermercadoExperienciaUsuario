from pymongo import MongoClient

def get_db():
    try:
        # Conexión local (puerto por defecto 27017)
        client = MongoClient("mongodb://localhost:27017/")

        # Seleccionamos la base de datos
        db = client["supermercado_db"]

        return db
    except Exception as e:
        print("Error al conectar con MongoDB:", e)
        return None
