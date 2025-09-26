from db.conexion import get_db

def base_datos_esta_poblada():
    db = get_db()
    colecciones = ["usuarios", "clientes", "productos", "areas"]
    for nombre in colecciones:
        if db[nombre].count_documents({}) == 0:
            return False
    return True
